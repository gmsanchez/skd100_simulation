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
    
    default_slam_params_file = PathJoinSubstitution(
        [FindPackageShare("skd100_navigation"), "config", "mapper_params_online_async.yaml"]
    )
    slam_params_file = LaunchConfiguration('slam_param_files', default = default_slam_params_file) 
    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value = slam_params_file,
        description = 'Full path to param yaml file to load for SLAM Online Async'
    )
    
    default_nav2_params_file = PathJoinSubstitution(
        [FindPackageShare("skd100_navigation"), "config", "nav2_params.yaml"]
    )
    nav2_params_file = LaunchConfiguration('nav2_params_file', default = default_nav2_params_file)
    declare_nav2_params_file = DeclareLaunchArgument(
        'nav2_params_file',
        default_value = nav2_params_file,
        description = 'Full path to param yaml file to load for Nav2'
    )
    
    ARGUMENTS = [
        declare_use_sim_time,
        declare_initial_robot_pose_x,
        declare_initial_robot_pose_y,
        declare_initial_robot_pose_z,
        declare_initial_robot_pose_yaw,
        declare_slam_params_file,
        declare_nav2_params_file,
    ]
    
    gz_nav2_launch_file = PathJoinSubstitution(
        [FindPackageShare("skd100_nav2_sim"), "launch", "gz_nav2.launch.py"],
    )
    
    world_file = PathJoinSubstitution(
        [FindPackageShare("skd100_gz"), "worlds", "turtlebot3_world.world"]
    )
    
    launch_gz_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_nav2_launch_file]),
        launch_arguments = {
            'use_sim_time': use_sim_time,
            'world_path': world_file,
            'x': initial_robot_pose_x,
            'y': initial_robot_pose_y,
            'z': initial_robot_pose_z,
            'yaw': initial_robot_pose_yaw,
            'slam_params_file': slam_params_file,
            'nav2_params_file': nav2_params_file,
        }.items(),
    )

    
    ld = LaunchDescription(ARGUMENTS)
    
    ld.add_action(launch_gz_nav2)
    
    return ld
