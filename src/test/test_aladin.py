from astropy.coordinates import Angle, SkyCoord
import numpy as np
import pytest
from typing import Callable

from ipyaladin import Aladin
from ipyaladin.coordinate_parser import parse_coordinate_string

from .test_coordinate_parser import test_is_coordinate_string_values

aladin = Aladin()


# monkeypatched sesame call to avoid remote access during tests
@pytest.fixture
def mock_sesame(monkeypatch: Callable) -> None:
    """Sesame calls mocked."""
    monkeypatch.setattr(SkyCoord, "from_name", lambda _: SkyCoord(0, 0, unit="deg"))


test_aladin_string_target, _ = zip(*test_is_coordinate_string_values)


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
    assert np.isclose(aladin.target.icrs.ra.deg, parsed_target.icrs.ra.deg)
    assert np.isclose(aladin.target.icrs.dec.deg, parsed_target.icrs.dec.deg)


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
    assert np.isclose(aladin.target.icrs.ra.deg, sc_target.icrs.ra.deg)
    assert np.isclose(aladin.target.icrs.dec.deg, sc_target.icrs.dec.deg)


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
