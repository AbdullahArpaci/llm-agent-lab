import math

R = 6378137.0


def geodetic_to_enu(lat, lon, alt,ref_lat, ref_lon, ref_alt):

    n = math.radians(lat - ref_lat) * R
    e = (math.radians(lon - ref_lon)* R* math.cos(math.radians(ref_lat)))
    u = alt - ref_alt

    return e, n, u


def enu_to_geodetic(e, n, u,ref_lat, ref_lon, ref_alt):

    lat = ref_lat + math.degrees(n / R)
    lon = (ref_lon+ math.degrees(e / (R * math.cos(math.radians(ref_lat)))))
    alt = ref_alt + u

    return lat, lon, alt


def yaw_ned_to_enu(yaw):
    yaw_enu = math.pi / 2 - yaw
    yaw_enu = (yaw_enu + math.pi) % (2 * math.pi) - math.pi

    return yaw_enu


def ned_to_enu(vn, ve, vd):
    e = ve
    n = vn
    u = -vd

    return e, n, u