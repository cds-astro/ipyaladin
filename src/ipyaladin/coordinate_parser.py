from astropy.coordinates import SkyCoord, Angle
import re


def parse_coordinate_string(string: str) -> SkyCoord:
    """
    Parse a string containing coordinates.
    :param string: The string containing the coordinates.
    :return: A SkyCoord object representing the coordinates.
    """
    if not _is_coordinate_string(string):
        return SkyCoord.from_name(string)
    coordinates: tuple[str, str] = _split_coordinate_string(string)
    # Determine frame
    if string[0] == "J" or string[0] not in ["J", "G", "B"]:
        frame = "icrs"
    elif string[0] == "G":
        frame = "galactic"
    elif string[0] == "B":
        frame = "fk4"
    else:
        raise ValueError(f"Invalid coordinate string: {string}")
    # Parse ra and dec to astropy Angle objects
    dec: Angle = Angle(coordinates[1], unit="deg")
    if _is_hour_angle_string(coordinates[0]):
        ra = Angle(coordinates[0], unit="hour")
    else:
        ra = Angle(coordinates[0], unit="deg")
    # Return SkyCoord object
    match frame:
        case "icrs":
            return SkyCoord(ra=ra, dec=dec, frame="icrs")
        case "galactic":
            return SkyCoord(l=ra, b=dec, frame="galactic")
        case "fk4":
            return SkyCoord(ra=ra, dec=dec, equinox="B1950", frame="fk4")


def _is_coordinate_string(string: str) -> bool:
    """
    Check if a string is a coordinate string.
    :param string: The string to check.
    :return: True if the string is a coordinate string, False otherwise.
    """
    regex = r"^([JGB].*|[0-9][0-9: hmsd.°′'\"+-]+)$"  # noqa RUF001
    return bool(re.match(regex, string))


def _split_coordinate_string(coo: str) -> tuple[str, str]:
    """
    Split a string containing coordinates in two parts.
    :param coo: The string containing the coordinates.
    :return: A tuple containing the two parts of the coordinate as strings.
    """
    # Remove first char if it is J, G or B
    jgb_regex = r"^[JGB].*"
    if bool(re.match(jgb_regex, coo)):
        coo = coo[1:]
    # Split string in two parts
    split_regex = r"[\s°]"
    parts = re.split(split_regex, coo)
    parts = [part for part in parts if part]
    middle = len(parts) // 2
    first_part = " ".join(parts[:middle])
    second_part = " ".join(parts[middle:])
    return first_part, second_part


def _is_hour_angle_string(coo: str) -> bool:
    """
    Check if a string is an hour angle string.
    :param coo: The string to check.
    :return: True if the string is an hour angle string, False otherwise.
    """
    regex = r"[hms°: ]"
    return bool(re.search(regex, coo))
