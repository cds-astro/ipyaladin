from typing import Tuple
from ipyaladin.utils._coordinate_parser import (
    _parse_coordinate_string,
    _split_coordinate_string,
    _is_hour_angle_string,
    _is_coordinate_string,
)
from astropy.coordinates import SkyCoord
import pytest

test_is_coordinate_string_values = [
    ("M 31", False),
    ("sgr a*", False),
    ("α Centauri", False),  # noqa RUF001
    ("* 17 Com", False),
    ("1:12:43.2 31:12:43", True),
    ("1:12:43.2 +31:12:43", True),
    ("1:12:43.2 -31:12:43", True),
    ("1 12 43.2 31 12 43", True),
    ("1 12 43.2 +31 12 43", True),
    ("1 12 43.2 -31 12 43", True),
    ("1h12m43.2s 1d12m43s", True),
    ("1h12m43.2s +1d12m43s", True),
    ("1h12m43.2s -1d12m43s", True),
    ("42.67 25.48", True),
    ("42.67 +25.48", True),
    ("42.67 -25.48", True),
    ("0 0", True),
    ("J12 30 45 +45 30 15", True),
    ("J42.67 25.48", True),
    ("G42.67 25.48", True),
    ("B42.67 25.48", True),
    ("Galactic Center", False),
]


@pytest.mark.parametrize(("inp", "expected"), test_is_coordinate_string_values)
def test_is_coordinate_string(inp: str, expected: bool) -> None:
    """Test the function _is_coordinate_string.

    Parameters
    ----------
    inp : str
        A string with an object name or coordinates to check.
    expected : bool
        The expected result as a boolean.

    """
    assert _is_coordinate_string(inp) == expected


test_split_coordinate_string_values = [
    ("1:12:43.2 31:12:43", ("1:12:43.2", "31:12:43")),
    ("1:12:43.2 +31:12:43", ("1:12:43.2", "+31:12:43")),
    ("1:12:43.2 -31:12:43", ("1:12:43.2", "-31:12:43")),
    ("1 12 43.2 31 12 43", ("1 12 43.2", "31 12 43")),
    ("1 12 43.2 +31 12 43", ("1 12 43.2", "+31 12 43")),
    ("1 12 43.2 -31 12 43", ("1 12 43.2", "-31 12 43")),
    ("1h12m43.2s 1d12m43s", ("1h12m43.2s", "1d12m43s")),
    ("1h12m43.2s +1d12m43s", ("1h12m43.2s", "+1d12m43s")),
    ("1h12m43.2s -1d12m43s", ("1h12m43.2s", "-1d12m43s")),
    ("42.67 25.48", ("42.67", "25.48")),
    ("42.67 +25.48", ("42.67", "+25.48")),
    ("42.67 -25.48", ("42.67", "-25.48")),
    ("0 0", ("0", "0")),
    ("J42.67 25.48", ("42.67", "25.48")),
    ("G42.67 25.48", ("42.67", "25.48")),
    ("B42.67 25.48", ("42.67", "25.48")),
]


@pytest.mark.parametrize(("inp", "expected"), test_split_coordinate_string_values)
def test_split_coordinate_string(inp: str, expected: Tuple[str, str]) -> None:
    """Test the function _split_coordinate_string.

    Parameters
    ----------
    inp : str
        A string with coordinates to split.
    expected : tuple of str
        The expected result as a tuple of strings.

    """
    assert _split_coordinate_string(inp) == expected


test_is_hour_angle_string_values = [
    ("1:12:43.2", True),
    ("1 12 43.2", True),
    ("1h12m43.2s", True),
    ("42.67", False),
    ("0", False),
]


@pytest.mark.parametrize(("inp", "expected"), test_is_hour_angle_string_values)
def test_is_hour_angle_string(inp: str, expected: bool) -> None:
    """Test the function _is_hour_angle_string.

    Parameters
    ----------
    inp : str
        A coordinate part as a string.
    expected : bool
        The expected result as a boolean.

    """
    assert _is_hour_angle_string(inp) == expected


test_parse_coordinate_string_values = [
    ("M 31", SkyCoord.from_name("M 31")),
    ("sgr a*", SkyCoord.from_name("sgr a*")),
    ("α Centauri", SkyCoord.from_name("α Centauri")),  # noqa RUF001
    ("* 17 Com", SkyCoord.from_name("* 17 Com")),
    (
        "1:12:43.2 31:12:43",
        SkyCoord(ra="1:12:43.2", dec="31:12:43", unit=("hour", "deg")),
    ),
    (
        "1:12:43.2 +31:12:43",
        SkyCoord(ra="1:12:43.2", dec="+31:12:43", unit=("hour", "deg")),
    ),
    (
        "1:12:43.2 -31:12:43",
        SkyCoord(ra="1:12:43.2", dec="-31:12:43", unit=("hour", "deg")),
    ),
    (
        "1 12 43.2 31 12 43",
        SkyCoord(ra="1 12 43.2", dec="31 12 43", unit=("hour", "deg")),
    ),
    (
        "1 12 43.2 +31 12 43",
        SkyCoord(ra="1 12 43.2", dec="+31 12 43", unit=("hour", "deg")),
    ),
    (
        "1 12 43.2 -31 12 43",
        SkyCoord(ra="1 12 43.2", dec="-31 12 43", unit=("hour", "deg")),
    ),
    (
        "1h12m43.2s 1d12m43s",
        SkyCoord(ra="1h12m43.2s", dec="1d12m43s", unit=("hour", "deg")),
    ),
    (
        "1h12m43.2s +1d12m43s",
        SkyCoord(ra="1h12m43.2s", dec="+1d12m43s", unit=("hour", "deg")),
    ),
    (
        "1h12m43.2s -1d12m43s",
        SkyCoord(ra="1h12m43.2s", dec="-1d12m43s", unit=("hour", "deg")),
    ),
    ("42.67 25.48", SkyCoord(ra=42.67, dec=25.48, unit="deg")),
    ("42.67 +25.48", SkyCoord(ra=42.67, dec=25.48, unit="deg")),
    ("42.67 -25.48", SkyCoord(ra=42.67, dec=-25.48, unit="deg")),
    ("0 0", SkyCoord(ra=0, dec=0, unit="deg")),
    ("J42.67 25.48", SkyCoord(ra=42.67, dec=25.48, unit="deg")),
    (
        "G42.67 25.48",
        SkyCoord(l=42.67, b=25.48, unit="deg", frame="galactic"),
    ),
    (
        "B42.67 25.48",
        SkyCoord(ra=42.67, dec=25.48, unit="deg", frame="fk4", equinox="B1950"),
    ),
    (
        "J12 30 45 +45 30 15",
        SkyCoord(ra="12 30 45", dec="45 30 15", unit=("hour", "deg")),
    ),
    (
        "J03 15 20 -10 20 30",
        SkyCoord(ra="03 15 20", dec="-10 20 30", unit=("hour", "deg")),
    ),
    ("G120.5 -45.7", SkyCoord(l=120.5, b=-45.7, unit="deg", frame="galactic")),
    ("G90 0", SkyCoord(l=90, b=0, unit="deg", frame="galactic")),
    ("B60 30", SkyCoord(ra=60, dec=30, unit="deg", frame="fk4", equinox="B1950")),
    ("B120 -45", SkyCoord(ra=120, dec=-45, unit="deg", frame="fk4", equinox="B1950")),
]


@pytest.mark.parametrize(("inp", "coordinates"), test_parse_coordinate_string_values)
def test_parse_coordinate_string(inp: str, coordinates: SkyCoord) -> None:
    """Test the function parse_coordinate_string.

    Parameters
    ----------
    inp : str
        The string to parse.
    expected : SkyCoord
        The expected result as a SkyCoord object.

    """
    assert _parse_coordinate_string(inp) == (
        coordinates.icrs.ra.deg,
        coordinates.icrs.dec.deg,
    )
