import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    main_launch = os.path.join(
        get_package_share_directory('lab1_bringup'), 'launch', 'lab1.launch.py')

    send_square = ExecuteProcess(
        cmd=['ros2', 'action', 'send_goal', '--feedback', '/draw_square',
             'lab1_interfaces/action/DrawSquare', '{side_length: 3.0}'],
        output='screen')

    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(main_launch)),
        TimerAction(period=4.0, actions=[send_square]),
    ])