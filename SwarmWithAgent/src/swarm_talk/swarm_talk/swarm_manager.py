import rclpy
from rclpy.node import Node
from swarm_talk_interfaces.msg import DronState , Setpoint
from std_srvs.srv import Trigger
from swarm_talk_interfaces.srv import Takeoff,SetFormation


class SwarmManager(Node):

    def __init__(self):
        super().__init__("swarm_manager")

        self.declare_parameter("drone_ids", [1, 2, 3])

        self.drone_ids = self.get_parameter("drone_ids").value

        self.pubss = {}
        self.subscribers = {}
        self.takeoff_clients = {}
        self.land_clients = {}

        for drone in self.drone_ids:

            self.pubs[drone] = self.create_publisher(
                Setpoint,
                f"/drone_{drone}/setpoint",
                10
            )

            self.subscribers[drone] = self.create_subscription(
                DronState,
                f"/drone_{drone}/state",
                lambda msg, drone_id=drone:
                    self._subscriber_callback,
                10
            )

            self.takeoff_clients[drone] = self.create_client(
                Takeoff,
                f"/drone_{drone}/takeoff"
            )

            self.land_clients[drone] = self.create_client(
                Trigger,
                f"/drone_{drone}/land"
            )

    def _subscriber_callback(self,msg):
        self.get_logger().info(f"Arming Check: {msg.armed}")
        self.get_logger().info(f"Mode Status: {msg.mode}")
        self.get_logger().info(f"Hearbeat Status: {msg.link_ok}")
        self.get_logger().info(f"Altitude Status: {msg.position.z:.2f}",throttle_duration_sec=3.0)


def main(args = None):
    rclpy.init()
    SwarmManagerNode = SwarmManager()
    rclpy.spin(SwarmManagerNode)
    rclpy.shutdown()
    SwarmManagerNode.destroy_node()

if __name__ == "__main__":
    main()