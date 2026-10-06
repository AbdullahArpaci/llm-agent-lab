import rclpy
from rclpy.node import Node
from swarm_talk_interfaces.msg import DronState


class SwarmManager(Node):
    def __init__(self):
        super().__init__("SwarmManager")


        self.subscriber = self.create_subscription(DronState,
                                                   "/SwarmState",
                                                   self._subscriber_callback,
                                                   10)


    def _subscriber_callback(self,msg):
        self.get_logger().info(f"Arming Check: {msg.armed}")
        self.get_logger().info(f"Mode Status: {msg.mode}")
        self.get_logger().info(f"Hearbeat Status: {msg.link_ok}")


def main(args = None):
    rclpy.init()
    SwarmManagerNode = SwarmManager()
    rclpy.spin(SwarmManagerNode)
    rclpy.shutdown()
    SwarmManagerNode.destroy_node()

if __name__ == "__main__":
    main()