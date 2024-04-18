from ipyaladin import Aladin
from ipyaladin.coordinate_parser import (
    parse_coordinate_string,
    _split_coordinate_string,
    _is_hour_angle_string,
)
from astropy.coordinates import SkyCoord
import pytest

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
]


@pytest.mark.parametrize(("inp", "expected"), test_split_coordinate_string_values)
def test_split_coordinate_string(inp, expected):
    assert _split_coordinate_string(inp) == expected


test_is_hour_angle_string_values = [
    ("1:12:43.2", True),
    ("1 12 43.2", True),
    ("1h12m43.2s", True),
    ("42.67", False),
]


@pytest.mark.parametrize(("inp", "expected"), test_is_hour_angle_string_values)
def test_is_hour_angle_string(inp, expected):
    assert _is_hour_angle_string(inp) == expected


test_parse_coordinate_string_values = [
    ("M 31", SkyCoord.from_name("M 31")),
    ("sgr a*", SkyCoord.from_name("sgr a*")),
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
]


@pytest.mark.parametrize(("inp", "expected"), test_parse_coordinate_string_values)
def test_parse_coordinate_string(inp, expected):
    assert parse_coordinate_string(inp) == expected


test_aladin_string_target = [
    "M 31",
    "sgr a*",
    "1:12:43.2 31:12:43",
    "1:12:43.2 +31:12:43",
    "1:12:43.2 -31:12:43",
    "1 12 43.2 31 12 43",
    "1 12 43.2 +31 12 43",
    "1 12 43.2 -31 12 43",
    "1h12m43.2s 1d12m43s",
    "1h12m43.2s +1d12m43s",
    "1h12m43.2s -1d12m43s",
    "42.67 25.48",
    "42.67 +25.48",
    "42.67 -25.48",
]


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_string_target_set(target):
    aladin = Aladin()
    aladin.target = target
    assert aladin.target == parse_coordinate_string(target)


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_sky_coord_target_set(target):
    sc_target = parse_coordinate_string(target)
    aladin = Aladin()
    aladin.target = sc_target
    assert aladin.target == sc_target
