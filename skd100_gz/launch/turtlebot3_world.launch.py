from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    use_sim_time = LaunchConfiguration('use_sim_time', default = True)
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value = use_sim_time,
        description = 'Use simulation (Gazebo) clock if true'
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
        declare_initial_robot_pose_x,
        declare_initial_robot_pose_y,
        declare_initial_robot_pose_z,
        declare_initial_robot_pose_yaw,
    ]
    
    skd100_gz_launch_file = PathJoinSubstitution(
        [FindPackageShare("skd100_gz"), "launch", "skd100_gz_sim.launch.py"],
    )
    
    world_file = PathJoinSubstitution(
        [FindPackageShare("skd100_gz"), "worlds", "turtlebot3_world.world"]
    )
    
    launch_gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([skd100_gz_launch_file]),
        launch_arguments = {
            'use_sim_time': use_sim_time,
            'world_path': world_file,
            'x': initial_robot_pose_x,
            'y': initial_robot_pose_y,
            'z': initial_robot_pose_z,
            'yaw': initial_robot_pose_yaw,
        }.items(),
    )

    
    ld = LaunchDescription(ARGUMENTS)
    
    ld.add_action(launch_gz_sim)
    
    return ld
