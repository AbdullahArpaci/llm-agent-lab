from pymavlink import mavutil
from rclpy import Node
from mavlink_link import Drone
from swarm_talk_interfaces.msg import DronState
import rclpy

class DroneAdapter(Node):
    def __init__(self):
        super().__init__()

        self.declare_parameters(
            namespace=' ',
            parameters=[("connection_string",str),("drone_id",int)]
        )

        self.dron_id = self.get_parameter("dron_id").value
        self.connection_string = self.get_parameter("connection_string").value

        self.drone = Drone(connection_string = self.connection_string,id = self.dron_id)
        self.state = None

        self.publisher = self.create_publisher(DronState,
                                               "/SwarmState",
                                               10)
        self.msg = DronState()
        self.msg.dron_id = self.dron_id


        self.timer = self.create_timer(0.1,self.timer_callback)

    def timer_callback(self):
        self.state = self.drone.state
        self.msg.position = self.state["position"]
        self.msg.velocity = self.state["velocity"]
        self.msg.yaw = self.state["yaw"]
        self.msg.armed = self.state["arm"]
        self.msg.mode = self.state["mode"]
        self.msg.link_pk = self.state["link_ok"]

        self.publisher.publish(self.msg)
def main(args = None):
    rclpy


if __name__ == "__main__":
    main()