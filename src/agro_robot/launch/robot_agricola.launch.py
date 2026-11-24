from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='agro_robot', executable='percepcion', name='percepcion', output='screen'),
        Node(package='agro_robot', executable='control_traccion', name='control_traccion', output='screen'),
    ])
