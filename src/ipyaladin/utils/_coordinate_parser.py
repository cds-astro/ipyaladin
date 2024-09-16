import warnings
from typing import Tuple

import requests
from astropy.coordinates import SkyCoord, Angle, Longitude, Latitude
import re

from ipyaladin.utils.exceptions import NameResolverWarning


def _parse_coordinate_string(
    string: str, body: str = "sky"
) -> Tuple[Longitude, Latitude]:
    """Parse a string containing coordinates.

    Parameters
    ----------
    string : str
        The string containing the coordinates.
    body : str
        The planetary body to use for the coordinates. Default
        is "sky" when there is no planetary body.

    Returns
    -------
    SkyCoord
        An `astropy.coordinates.SkyCoord` object representing the coordinates.

    """
    if not _is_coordinate_string(string):
        if body == "sky" or body is None:
            sesame = SkyCoord.from_name(string)
            return sesame.icrs.ra.deg, sesame.icrs.dec.deg
        return _from_name_on_planet(string, body)
    # coordinates should be parsed from the string
    coordinates = _split_coordinate_string(string)
    # Parse ra and dec to astropy Angle objects
    lat: Angle = Angle(coordinates[1], unit="deg")
    if _is_hour_angle_string(coordinates[0]):
        lon = Angle(coordinates[0], unit="hour")
    else:
        lon = Angle(coordinates[0], unit="deg")
    # Create SkyCoord object
    if string[0] == "B":
        coo = SkyCoord(ra=lon, dec=lat, equinox="B1950", frame="fk4")
    elif string[0] == "G":
        coo = SkyCoord(l=lon, b=lat, frame="galactic")
    else:
        coo = SkyCoord(ra=lon, dec=lat, frame="icrs")
    return coo.icrs.ra.deg, coo.icrs.dec.deg


def _from_name_on_planet(string: str, body: str) -> SkyCoord:
    """Get coordinates from a name on a planetary body.

    Parameters
    ----------
    string : str
        The name of the feature.
    body : str
        The planetary body to use for the coordinates.

    Returns
    -------
    SkyCoord
        An `astropy.coordinates.SkyCoord` object representing the coordinates.
    """
    url = (
        f"https://alasky.cds.unistra.fr/planetary-features/resolve"
        f"?identifier={string.replace(' ', '+')}&body={body}&threshold=0.7&format=json"
    )
    request = requests.get(url)
    if request.status_code != requests.codes.ok:
        raise ValueError(
            "No coordinates found for this requested planetary feature: " f"'{string}'"
        )
    data = request.json()["data"]
    # response is different for earth
    if body == "earth":
        return data[0][0], data[0][1]
    # case of every other planetary bodies
    identifier = data[0][1]
    lat = data[0][5]  # inverted lon and lat in response
    lon = data[0][6]
    system = data[0][11]
    if identifier != string:
        warnings.warn(
            f"Nothing found for '{string}' on {body}. However, a {identifier} exists. "
            f"Moving to {identifier}.",
            NameResolverWarning,
            stacklevel=2,
        )
    if "+West" in system:
        lon = 360 - lon
    return lon, lat


def _is_coordinate_string(string: str) -> bool:
    """Check if a string is a coordinate string.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    bool
        True if the string is a coordinate string, False otherwise.

    """
    regex = r"^[JGB]?\d[0-9: hmsd.°′'\"+-]+$"  # noqa RUF001
    return bool(re.match(regex, string))


def _split_coordinate_string(coo: str) -> Tuple[str, str]:
    """Split a string containing coordinates in two parts.

    Parameters
    ----------
    coo : str
        The string containing the coordinates.

    Returns
    -------
    tuple[str, str]
        A tuple containing the two parts of the coordinate as strings.

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
    """Check if a string is an hour angle string.

    Parameters
    ----------
    coo : str
        The string to check.

    Returns
    -------
    bool
        True if the string is an hour angle string, False otherwise.

    """
    regex = r"[hms°: ]"
    return bool(re.search(regex, coo))
