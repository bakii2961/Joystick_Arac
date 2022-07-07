from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([Node(
        package='joyistick',
        executable='joy_input',
        output='screen'),
    ])
