from pymavlink import mavutil
import time
import math


class Drone:

    def __init__(self, connection_string, id):
        self.connection_string = connection_string
        self.conn = None
        self.id = id
        self.state = {
            "alt" : 0.0,
            "lat" : 0.0,
            "lon" : 0.0,
            "vx":0.0,
            "vy":0.0,
            "vz":0.0,
            "yaw" : 0.0,
            "arm" : False,
            "mode" : "mod_yok",
            "link_ok" : False
        }
        self.pending_ack = None

        self.last_heartbeat = None


    def connect(self) -> bool:
        self.conn = mavutil.mavlink_connection(
            self.connection_string
        )

        heartbeat = self.conn.wait_heartbeat(timeout=10)
        if heartbeat is not None:
            print(f"Drone_{self.id} ile bağlantı kuruldu")
            self.last_heartbeat = time.monotonic()
            return True
        print(f"Drone_{self.id} ile bağlantı kurulamadı")
        return False


    def update_telemetry(self):
        while(True):
            msg = self.conn.recv_msg()

            if msg is None:
                break

            msg_type = msg.get_type()

            if msg_type == "GLOBAL_POSITION_INT":
                self.state["lat"] = msg.lat / 1e7
                self.state["lon"] = msg.lon / 1e7
                self.state["alt"] = msg.alt / 1000
                self.state["vx"] = msg.vx / 100
                self.state["vy"] = msg.vy / 100
                self.state["vz"] = msg.vz / 100

                if msg.hdg == 65535:
                    self.state["yaw"] = None
                else:
                    self.state["yaw"] = math.radians(msg.hdg / 100)


            elif msg_type == "HEARTBEAT" and msg.get_srcSystem() == self.conn.target_system:
                self.last_heartbeat = time.monotonic()
                self.state["arm"] = bool(
                    msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                )
                self.state["mode"] = mavutil.mode_string_v10(msg)
        

    def arm(self) -> bool:

        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            command,
            0,
            1,
            0, 0, 0, 0, 0, 0
        )

        ack = self.conn.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=3
        )

        if ack is None:
            return False

        if ack.command != command:
            return False
        return ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def switch_mode(self, mode: str) -> bool:

        mode_mapping = self.conn.mode_mapping()

        if mode not in mode_mapping:
            print(f"Geçersiz mode: {mode}")
            return False

        mode_id = mode_mapping[mode]

        command = mavutil.mavlink.MAV_CMD_DO_SET_MODE

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            command,
            0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
            0, 0, 0, 0, 0
        )

        ack = self.conn.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=3
        )

        if ack is None:
            print("ACK alınamadı.")
            return False

        if ack.command != command:
            return False

        if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            return True

        return False
    def goto_global(self, lat: float, lon: float, alt: float):

        self.conn.mav.set_position_target_global_int_send(
            0,
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_INT,

            0b0000111111111000,

            int(lat * 1e7),
            int(lon * 1e7),
            alt,

            0, 0, 0,
            0, 0, 0,
            0, 0
        )
    def takeoff(self, alt) -> bool:

        command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            command,
            0,
            0,
            0, 0, 0, 0, 0, alt
        )

        ack = self.conn.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=3
        )

        if ack is None:
            return False

        if ack.command != command:
            return False

        return ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def heartbeat(self):
        if (time.monotonic() - self.last_heartbeat) <= 3:
            self.state["link_ok"] = True
        else:
            self.state["link_ok"] = False

    def land(self) -> bool:

        command = mavutil.mavlink.MAV_CMD_NAV_LAND

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            command,
            0,
            0, 0, 0, 0, 0, 0, 0
        )

        ack = self.conn.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=3
        )

        if ack is None:
            return False

        if ack.command != command:
            return False

        return ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED
