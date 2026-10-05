from pymavlink import mavutil
from rclpy import Node
from typing import Any


class DronNode(Node):
    def __init__(self):
        super().__init__(f"dron_{id}")
        self.parameters = self.declare_parameters(
            namespace=''
            parameters=[("id",0),("port","default_string")]
        )

        self.port = self.get_parameter("port").value
        self.id = self.get_parameter("id").value



def main(args = None):
    pass


if __name__ == "__main__":
    main()