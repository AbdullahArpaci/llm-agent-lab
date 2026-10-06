from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import yaml

def create_drones(count : int,udp_port : str,ip_address : str, drone_id : int = 1):
    drones = []
    for _ in range(count):
        connection_string = f"udp:{ip_address}:{udp_port}"
        node = Node(
            namespace=f"drone_{drone_id}",
            package="swarm_talk",
            executable="drone_adapter",
            parameters=[{
                "connection_string": connection_string,
                "drone_id": drone_id,
            }])
        udp_port += 10
        drone_id +=1
        drones.append(node)
    return drones


    

def generate_launch_description():

    config = os.path.join(
        get_package_share_directory("swarm_talk"),
        'config',
        'drones.yaml'
    )

    with open(config) as f:
        data = yaml.safe_load(f)

    drones = create_drones(data["num_drones"],data["base_port"],data["ip_address"])
    return LaunchDescription([
        *drones,
        Node(
            namespace="SwarmManager",
            package="swarm_talk",
            executable="swarm_manager"
        )
    ])