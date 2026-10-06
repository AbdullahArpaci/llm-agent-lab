from pymavlink import mavutil
from rclpy.node import Node
from swarm_talk.mavlink_link import Drone
from swarm_talk_interfaces.msg import DronState
from swarm_talk.frames import *
import rclpy

class DroneAdapter(Node):
    def __init__(self):
        super().__init__("drone")

        self.declare_parameters(
            namespace='',
            parameters=[("connection_string","conn_str"),("drone_id",0)]
        )

        self.drone_id = self.get_parameter("drone_id").value
        self.connection_string = self.get_parameter("connection_string").value

        self.drone = Drone(connection_string = self.connection_string,id = self.drone_id)
        self.state = None


        self.drone.connect()
        self.drone.switch_mode("GUIDED")
        self.drone.arm()
        self.drone.takeoff(10)
        self.publisher = self.create_publisher(DronState,
                                               "/SwarmState",
                                               10)



        self.ref_lat = 0
        self.ref_lon = 0
        self.ref_alt = 0

        self.msg = DronState()
        self.msg.drone_id = self.drone_id


        self.timer = self.create_timer(0.1,self.timer_callback)

    def timer_callback(self):
        self.drone.update_telemetry()
        self.state = self.drone.state
        e, n, u = geodetic_to_enu(
            self.state["lat"], self.state["lon"], self.state["alt"],
            self.ref_lat, self.ref_lon, self.ref_alt,
        )
        self.msg.position.x = e
        self.msg.position.y = n
        self.msg.position.z = u

        ve,vn,vu = ned_to_enu(self.state["vx"],self.state["vy"],self.state["vz"])
        self.msg.velocity.x = ve
        self.msg.velocity.y = vn
        self.msg.velocity.z = vu

        self.msg.yaw = self.state["yaw"]
        self.msg.armed = self.state["arm"]
        self.msg.mode = self.state["mode"]
        self.msg.link_ok = self.state["link_ok"]

        self.publisher.publish(self.msg)
        
def main(args = None):
    rclpy.init(args=args)
    dron_node = DroneAdapter()
    rclpy.spin(dron_node)
    rclpy.shutdown()
    dron_node.destroy_node


if __name__ == "__main__":
    main()