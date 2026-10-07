from pymavlink import mavutil
from rclpy.node import Node
from swarm_talk.mavlink_link import Drone
from swarm_talk_interfaces.msg import DronState,Setpoint
from swarm_talk_interfaces.srv import Takeoff
from std_srvs.srv import Trigger 
from swarm_talk.frames import *
import rclpy

class DroneAdapter(Node):
    def __init__(self):
        super().__init__("drone")

        self.declare_parameters(
            namespace='',
            parameters=[("connection_string","conn_str"),("drone_id",0),("ref_lat",0.0),("ref_lon",0.0),("ref_alt",0.0)]
        )

        self.drone_id = self.get_parameter("drone_id").value
        self.connection_string = self.get_parameter("connection_string").value
        self.ref_lat = self.get_parameter("ref_lat").value
        self.ref_lon = self.get_parameter("ref_lon").value
        self.ref_alt = self.get_parameter("ref_alt").value

        self.drone = Drone(connection_string = self.connection_string,id = self.drone_id)
        self.drone.connect()

        

        self.publisher = self.create_publisher(
            DronState,
            f"/drone_{self.drone_id}/state",
            10
        )

        self.subscriber = self.create_subscription(
            Setpoint,
            f"/drone_{self.drone_id}/setpoint",
            self._setpoint_callback,
            10
        )
        

        self.msg = DronState()
        self.msg.drone_id = self.drone_id

        self.takeoff_service = self.create_service(
            Takeoff,
            f"/drone_{self.drone_id}/takeoff",
            self.takeoff_service_callback
        )

        self.land_service = self.create_service(
            Trigger,
            f"/drone_{self.drone_id}/land",
            self.land_service_callback
        )

        self.timer = self.create_timer(
            0.1,
            self.timer_callback
        )

    def timer_callback(self):
        self.drone.update_telemetry()
        self.drone.heartbeat()
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

        self.msg.yaw = yaw_ned_to_enu(self.state["yaw"])
        self.msg.armed = self.state["arm"]
        self.msg.mode = self.state["mode"]
        self.msg.link_ok = self.state["link_ok"]

        self.publisher.publish(self.msg)

    def takeoff_service_callback(self, request, response):
        altitude = request.altitude

        mode_s = self.drone.switch_mode("GUIDED")

        if not mode_s:
            response.success = False
            response.message = "GUIDED mode could not be set"
            return response

        arm_s = self.drone.arm()

        if not arm_s:
            response.success = False
            response.message = "Drone could not be armed"
            return response

        takeoff_s = self.drone.takeoff(altitude)

        if not takeoff_s:
            response.success = False
            response.message = "Takeoff command failed"
            return response

        response.success = True
        response.message = "Takeoff started"
        return response
    def _setpoint_callback(self, msg):

        self.get_logger().info(
            f"Yeni setpoint: "
            f"x={msg.position.x:.2f}, "
            f"y={msg.position.y:.2f}, "
            f"z={msg.position.z:.2f}"
        )

        lat,lon,alt = enu_to_geodetic(msg.position.x,msg.position.y,msg.position.z,self.ref_lat,self.ref_lon,self.ref_alt)

        self.drone.goto_global(lat=lat,lon=lon,alt=alt)

    def land_service_callback(self, request, response):
        land_s = self.drone.land()

        if land_s:
            response.success = True
            response.message = "Landing started"
        else:
            response.success = False
            response.message = "Landing command failed"

        return response

def main(args = None):
    rclpy.init(args=args)
    dron_node = DroneAdapter()
    rclpy.spin(dron_node)
    rclpy.shutdown()
    dron_node.destroy_node()


if __name__ == "__main__":
    main()