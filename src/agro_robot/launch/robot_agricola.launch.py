import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(get_package_share_directory('agro_robot'), 'config', 'robot_params.yaml')

    return LaunchDescription([
        Node(package='agro_robot', executable='percepcion', name='percepcion', output='screen'),
        Node(package='agro_robot', executable='control_traccion', name='control_traccion',
             parameters=[params], output='screen'),
    ])
