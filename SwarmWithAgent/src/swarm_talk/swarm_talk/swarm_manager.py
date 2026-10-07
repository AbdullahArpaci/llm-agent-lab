import rclpy
from rclpy.node import Node
from swarm_talk_interfaces.msg import DronState , Setpoint
from std_srvs.srv import Trigger
from swarm_talk_interfaces.srv import Takeoff,SetFormation
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup ,ReentrantCallbackGroup
import time

class SwarmManager(Node):

    def __init__(self):
        super().__init__("swarm_manager")

        self.declare_parameter("drone_ids", [1, 2, 3])

        self.drone_ids = self.get_parameter("drone_ids").value

        self.pubs = {}
        self.subscribers = {}
        self.takeoff_clients = {}
        self.land_clients = {}
        self.latest_states = {}
        
        self.service_group = MutuallyExclusiveCallbackGroup()
        self.client_group = ReentrantCallbackGroup()

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
                    self._subscriber_callback(msg,drone_id),
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

        self.swarm_takeoff_srv = self.create_service(
            Takeoff, "/swarm/takeoff",
            self.swarm_takeoff_callback,
            callback_group=self.service_group,
        )

        self.swarm_takeoff_srv = self.create_service(
            Trigger,"/swarm/land",
            self.swarm_land_callback,
            callback_group=self.service_group,
        )

    def send_takeoff_requests(self, altitude):
        futures = {}
        for drone_id in self.drone_ids:
            client = self.takeoff_clients[drone_id]
            if not client.service_is_ready():
                futures[drone_id] = None
                continue
            req = Takeoff.Request()
            req.altitude = altitude
            futures[drone_id] = client.call_async(req)
        return futures

    def send_land_requests(self):
            futures = {}
            for drone_id in self.drone_ids:
                client = self.land_clients[drone_id]
                if not client.service_is_ready():
                    futures[drone_id] = None
                    continue
                req = Trigger.Request()
                futures[drone_id] = client.call_async(req)
            return futures
        
        
    def _subscriber_callback(self,msg,drone_id):
        self.get_logger().info(f"Arming Check: {msg.armed}")
        self.get_logger().info(f"Mode Status: {msg.mode}")
        self.get_logger().info(f"Hearbeat Status: {msg.link_ok}")
        self.get_logger().info(f"Altitude Status: {msg.position.z:.2f}",throttle_duration_sec=3.0)

        self.latest_states[drone_id] = msg
    
    
    def swarm_takeoff_callback(self, request, response):
        altitude = request.altitude

        if not (1 <= altitude <= 30):
            response.success = False
            response.message = (
                f"Reddedildi: irtifa 1-30 m arasında olmalı, "
                f"istenen {altitude:.1f} m."
            )
            return response

        futures = self.send_takeoff_requests(altitude)

        
        deadline = time.monotonic() + 12.0
        while time.monotonic() < deadline:
            if all(f is None or f.done() for f in futures.values()):
                break
            time.sleep(0.05)

        results = []
        all_ok = True
        for drone_id, future in futures.items():
            if future is None:
                ok, msg = False, "servis bulunamadı"
            elif not future.done():
                ok, msg = False, "zaman aşımı"
            else:
                result = future.result()
                ok, msg = result.success, result.message
            all_ok = all_ok and ok
            results.append(f"drone_{drone_id}: {msg}")

        response.success = all_ok
        response.message = "; ".join(results)
        return response

    def swarm_land_callback(self, request, response):

        futures = self.send_land_requests()

        deadline = time.monotonic() + 12.0
        while time.monotonic() < deadline:
            if all(f is None or f.done() for f in futures.values()):
                break
            time.sleep(0.05)

        results = []
        all_ok = True
        for drone_id, future in futures.items():
            if future is None:
                ok, msg = False, "servis bulunamadı"
            elif not future.done():
                ok, msg = False, "zaman aşımı"
            else:
                result = future.result()
                ok, msg = result.success, result.message
            all_ok = all_ok and ok
            results.append(f"drone_{drone_id}: {msg}")

        response.success = all_ok
        response.message = "; ".join(results)
        return response

def main(args = None):
    rclpy.init(args=args)
    executer = MultiThreadedExecutor()
    node = SwarmManager()
    executer.add_node(node)
    executer.spin()
    rclpy.shutdown()
    node.destroy_node()

if __name__ == "__main__":
    main()