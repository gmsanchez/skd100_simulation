from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, 
    DeclareLaunchArgument,
    RegisterEventHandler,
    AppendEnvironmentVariable,
    )
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare, FindPackagePrefix
from launch_ros.actions import Node

def generate_launch_description():
    
    use_sim_time = LaunchConfiguration('use_sim_time', default = True)
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value = use_sim_time,
        description = 'Use simulation (Gazebo) clock if true'
    )
    
    # Default empty (base) world
    empty_world = PathJoinSubstitution(
        [FindPackageShare("skd100_gz"), "worlds", "empty_world.world"]
    )
    world_path = LaunchConfiguration('world_path', default = empty_world)
    declare_world_path = DeclareLaunchArgument(
        'world_path',
        default_value = world_path,
        description = 'The world path, by default is empty.world'
    )
    
    initial_robot_pose_x = LaunchConfiguration('x', default = '0.0')
    declare_initial_robot_pose_x = DeclareLaunchArgument(
        'x', default_value=initial_robot_pose_x, description='x-axis initial position'
    )
    
    initial_robot_pose_y = LaunchConfiguration('y', default = '0.0')
    declare_initial_robot_pose_y = DeclareLaunchArgument(
        'y', default_value=initial_robot_pose_y, description='y-axis initial position'
    )
    
    initial_robot_pose_z = LaunchConfiguration('z', default = '0.2')
    declare_initial_robot_pose_z = DeclareLaunchArgument(
        'z', default_value=initial_robot_pose_z, description='z-axis initial position'
    )
    
    initial_robot_pose_yaw = LaunchConfiguration('yaw', default = '0.0')
    declare_initial_robot_pose_yaw = DeclareLaunchArgument(
        'yaw', default_value=initial_robot_pose_yaw, description='YAW initial orientation'
    )
    
    ARGUMENTS = [
        declare_use_sim_time,
        declare_world_path,
        declare_initial_robot_pose_x,
        declare_initial_robot_pose_y,
        declare_initial_robot_pose_z,
        declare_initial_robot_pose_yaw,
    ]
    
    # Add to Gazebo Resource PATH the location for meshes from URDF
    append_skd100_meshes_gz_resource_path = AppendEnvironmentVariable(
        name = 'GZ_SIM_RESOURCE_PATH',
        value = PathJoinSubstitution([FindPackagePrefix("skd100_description"), "share"]),
    )
    
    append_sim_models_gz_resource_path = AppendEnvironmentVariable(
        name = 'GZ_SIM_RESOURCE_PATH',
        value = PathJoinSubstitution([FindPackageShare("skd100_gz"), "models"]),
    )
    
    # Launch Gazebo
    launch_gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            ])
        ]),
        launch_arguments = {
            # 'gz_args': ['-r -v 4 ', world_path],
            'gz_args': ['-r ', world_path],
        }.items(),
    )
    
    # Launch robot_state_publisher (with robot_description)
    launch_robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("skd100_description"),
                "launch",
                "description.launch.py"
            ])
        ]),
        launch_arguments= {
            'use_sim_time': use_sim_time,
        }.items(),
    )
    
    spawn_skd100_entity = Node(
        package = 'ros_gz_sim',
        executable = 'create',
        arguments = [
            '-entity', 'skd1',
            '-topic', 'robot_description',
            '-x', initial_robot_pose_x,
            '-y', initial_robot_pose_y,
            '-z', initial_robot_pose_z,
            '-Y', initial_robot_pose_yaw,
        ],
        parameters = [{ 'use_sim_time': use_sim_time }],
        output = 'screen',
    )
    
    ros_gz_bridge_params = PathJoinSubstitution(
        [FindPackageShare("skd100_gz"), "config", "ros_gz_bridge.yaml"],
    )
    
    ros_gz_bridge_node = Node(
        package = 'ros_gz_bridge',
        executable = 'parameter_bridge',
        name = 'ros_gz_bridge',
        parameters = [{
            'config_file': ros_gz_bridge_params,
        }],
        output='screen',
    )
    
    joint_state_broadcaster_spawn_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager',
        ],
    )
    
    skd_base_controller_spawn_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'skd_base_controller',
            '--controller-manager',
            '/controller_manager',
        ],
    )
    
    # Delay start of `joint_state_broadcaster` after spawn_skd1_entity
    delay_joint_state_broadcaster_after_spawn_skd100_entity = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_skd100_entity,
            on_exit=[joint_state_broadcaster_spawn_node],
        )
    )
    
    # Delay start of velocity_controller after `joint_state_broadcaster`
    delay_velocity_controller_after_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawn_node,
            on_exit=[skd_base_controller_spawn_node],
        )
    )
    
    
    ld = LaunchDescription(ARGUMENTS)
    
    ld.add_action(append_skd100_meshes_gz_resource_path)
    ld.add_action(append_sim_models_gz_resource_path)
    ld.add_action(launch_gz_sim)
    ld.add_action(launch_robot_state_publisher)
    ld.add_action(spawn_skd100_entity)
    ld.add_action(ros_gz_bridge_node)
    ld.add_action(delay_joint_state_broadcaster_after_spawn_skd100_entity)
    ld.add_action(delay_velocity_controller_after_joint_state_broadcaster)

    return ld
