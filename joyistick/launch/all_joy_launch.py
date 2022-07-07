from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    joy = IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(get_package_share_directory("joyistick"), 'joy_node_launch.py')]))
    input_joy = IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(get_package_share_directory("joyistick"), 'joy_input_launch.py')]))
    output_joy = IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(get_package_share_directory("joyistick"), 'joy_output_launch.py')]))
    out = LaunchDescription([joy, input_joy, output_joy])
    return out
