from astropy.coordinates import SkyCoord, Angle
import re


def parse_coordinate_string(string: str) -> SkyCoord:
    if string[0].isalpha():
        return SkyCoord.from_name(string)
    coordinates: tuple[str, str] = _split_coordinate_string(string)
    ra: Angle or None = None
    dec: Angle = Angle(coordinates[1], unit="deg")
    if _is_hour_angle_string(coordinates[0]):
        ra = Angle(coordinates[0], unit="hour")
    else:
        ra = Angle(coordinates[0], unit="deg")
    return SkyCoord(ra=ra, dec=dec, frame="icrs")


def _split_coordinate_string(coo: str) -> tuple[str, str]:
    regex = r"[\s°]"
    parts = re.split(regex, coo)
    parts = [part for part in parts if part]
    middle = len(parts) // 2
    first_part = " ".join(parts[:middle])
    second_part = " ".join(parts[middle:])
    return first_part, second_part


def _is_hour_angle_string(coo: str) -> bool:
    regex = r"[hms°: ]"
    return bool(re.search(regex, coo))
