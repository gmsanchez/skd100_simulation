from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import SetRemap

def generate_launch_description():
    
    use_sim_time = LaunchConfiguration('use_sim_time', default = True)
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value = use_sim_time,
        description = 'Use simulation (Gazebo) clock if true'
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
        declare_slam_params_file,
        declare_nav2_params_file,
    ]

    launch_teleop_twist_mux = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("skd100_teleop"),
                "launch",
                "twist_mux.launch.py",
            ])
        ]),
        launch_arguments = {'use_sim_time': use_sim_time}.items(),
    )
    
    launch_local_ekf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("skd100_localization"),
                "launch",
                "local_ekf.launch.py",
            ])
        ]),
        launch_arguments = {'use_sim_time': use_sim_time}.items(),
    )
    
    launch_global_ekf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("skd100_localization"),
                "launch",
                "pose_global_ekf.launch.py"],
            )
        ),
        launch_arguments= {'use_sim_time': use_sim_time}.items(),
    )
    
    launch_online_async = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("slam_toolbox"),
                "launch",
                "online_async_launch.py",
            ])
        ]),
        launch_arguments = {
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file
        }.items(),
    )
    
    # Remapping '/scan' (SLAM) to '/scan_raw' (LIDAR without filtering in simulation)
    only_async_with_remapping = GroupAction(
        actions = [
            SetRemap(src = 'scan', dst = 'scan_raw'),
            launch_online_async
        ]
    )

    launch_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('skd100_navigation'),
                'launch',
                'navigation.launch.py'
            ]),
        ]),
        launch_arguments = {
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file
        }.items()
    )
    
    
    ld = LaunchDescription(ARGUMENTS)
    
    ld.add_action(launch_teleop_twist_mux)
    ld.add_action(launch_local_ekf)
    ld.add_action(launch_global_ekf)
    ld.add_action(only_async_with_remapping)
    ld.add_action(launch_nav2)
    
    return ld
