from pymavlink import mavutil
from typing import Any


class Drone:

    def __init__(self, connection_string, id):
        self.connection_string = connection_string
        self.conn = None
        self.id = id
        self.state = {
            "alt" : None,
            "lat" : None,
            "lon" : None,
            "ground_speed" : None,
            "air_speed" : None,
            "roll" : None,
            "pitch" : None,
            "yaw" : None
        }

    def connect(self) -> bool:
        self.conn = mavutil.mavlink_connection(
            self.connection_string
        )

        msg = self.recv_message("HEARTBEAT")

        if msg is None:
            print(f"Drone_{self.id} bağlantı kurulamadı!")
            return False

        print(f"Drone_{self.id} ile bağlantı kuruldu")
        return True

    def recv_message(self, type : str, timeout : int = 5, retries : int = 3):

        for _ in range(retries):

            msg = self.conn.recv_match(
                type=type,
                blocking=True,
                timeout=timeout
            )

            if msg is not None:
                return msg

        return None

    def update_telemetry(self):
        msg = self.conn.recv_msg()

        if msg is None:
            return
        if msg.get_type() == "GLOBAL_POSITION_INT":
            self.state["lat"] = msg.lat / 1e7
            self.state["lon"] = msg.lon / 1e7
            self.state["alt"] = msg.relative_alt / 1000

        elif msg.get_type() == "VFR_HUD":
            self.state["ground_speed"] = msg.groundspeed
            self.state["air_speed"] = msg.airspeed

        elif msg.get_type() == "ATTITUDE":
            self.state["roll"] = msg.roll
            self.state["pitch"] = msg.pitch
            self.state["yaw"] = msg.yaw


    def arm(self) -> bool:

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,
            0, 0, 0, 0, 0, 0
        )

        msg = self.recv_message("COMMAND_ACK")

        if msg is None:
            print("ARM ACK alınamadı")
            return False

        if msg.command != mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
            print("Gelen ACK ARM komutuna ait değil")
            return False

        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"Drone_{self.id} was armed!")
            return True

        print(f"ARM başarısız: {msg.result}")
        return False

    def switch_mode(self, mode: str) -> bool:

        mode_mapping = self.conn.mode_mapping()

        if mode not in mode_mapping:
            print(f"Geçersiz mode: {mode}")
            return False

        mode_id = mode_mapping[mode]

        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
            0, 0, 0, 0, 0
        )

        msg = self.recv_message("COMMAND_ACK")

        if msg is None:
            print("Mode ACK alınamadı")
            return False

        if msg.command != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
            print("Gelen ACK mode değiştirme komutuna ait değil")
            return False

        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"Drone_{self.id} mode was switched!")
            return True

        print(f"Mode değiştirme başarısız: {msg.result}")
        return False

    def goto_global(self, lat: float, lon: float, alt: float):

        self.conn.mav.set_position_target_global_int_send(
            0,
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,

            0b0000111111111000,

            int(lat * 1e7),
            int(lon * 1e7),
            alt,

            0, 0, 0,
            0, 0, 0,
            0, 0
        )
