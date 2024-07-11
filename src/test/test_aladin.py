from astropy.coordinates import Angle, SkyCoord
import pytest
from typing import Callable

from ipyaladin import Aladin
from ipyaladin.coordinate_parser import parse_coordinate_string

aladin = Aladin()


# monkeypatched sesame call to avoid remote access during tests
@pytest.fixture
def mock_sesame(monkeypatch: Callable) -> None:
    """Sesame calls mocked."""
    monkeypatch.setattr(SkyCoord, "from_name", lambda _: SkyCoord(0, 0, unit="deg"))


test_aladin_string_target = [
    "M 31",
    "sgr a*",
    "α Centauri",  # noqa RUF001
    "* 17 Com",
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
    "0 0",
    "J42.67 25.48",
    "G42.67 25.48",
    "B42.67 25.48",
    "J12 30 45 +45 30 15",
    "J03 15 20 -10 20 30",
    "G120.5 -45.7",
    "G90 0",
    "B60 30",
    "B120 -45",
    "Galactic Center",
]


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_string_target_set(target: str, mock_sesame: Callable) -> None:  # noqa: ARG001
    """Test setting the target of an Aladin object with a string or a SkyCoord object.

    Parameters
    ----------
    target : str
        The target string.

    """
    aladin.target = target
    parsed_target = parse_coordinate_string(target)
    assert aladin.target.icrs.ra.deg == parsed_target.icrs.ra.deg
    assert aladin.target.icrs.dec.deg == parsed_target.icrs.dec.deg


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_sky_coord_target_set(target: str, mock_sesame: Callable) -> None:  # noqa: ARG001
    """Test setting and getting the target of an Aladin object with a SkyCoord object.

    Parameters
    ----------
    target : str
        The target string.

    """
    sc_target = parse_coordinate_string(target)
    aladin.target = sc_target
    assert aladin.target.icrs.ra.deg == sc_target.icrs.ra.deg
    assert aladin.target.icrs.dec.deg == sc_target.icrs.dec.deg


test_aladin_float_fov = [
    0,
    360,
    180,
    -180,
    720,
]


@pytest.mark.parametrize("angle", test_aladin_float_fov)
def test_aladin_float_fov_set(angle: float) -> None:
    """Test setting the angle of an Aladin object with a float.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    aladin.fov = angle
    assert aladin.fov.deg == angle


@pytest.mark.parametrize("angle", test_aladin_float_fov)
def test_aladin_angle_fov_set(angle: float) -> None:
    """Test setting the angle of an Aladin object with an Angle object.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    angle_fov = Angle(angle, unit="deg")
    aladin.fov = angle_fov
    assert aladin.fov.deg == angle_fov.deg
