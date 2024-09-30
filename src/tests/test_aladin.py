from typing import Callable, Dict

from astropy.coordinates import Angle, SkyCoord, Longitude, Latitude
import astropy.units as u
import numpy as np
import pytest

from ipyaladin import Aladin
from ipyaladin.utils._coordinate_parser import _parse_coordinate_string

from .test_coordinate_parser import test_is_coordinate_string_values

aladin = Aladin()


# monkeypatched sesame call to avoid remote access during tests
@pytest.fixture
def mock_sesame(monkeypatch: Callable) -> None:
    """Sesame calls mocked."""
    monkeypatch.setattr(SkyCoord, "from_name", lambda _: SkyCoord(0, 0, unit="deg"))


class MockResponse:
    """Mock response object for requests.get."""

    def __init__(self) -> None:
        self.status_code = 200

    def json(self) -> Dict:
        """Return a mock JSON response."""
        return {
            "data": [
                [
                    None,
                    None,
                    None,
                    None,
                    None,
                    0,
                    0,
                    None,
                    None,
                    None,
                    None,
                    "",
                ]
            ]
        }


test_aladin_string_target, _ = zip(*test_is_coordinate_string_values)


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_string_target_set(target: str, mock_sesame: Callable) -> None:  # noqa: ARG001
    """Test setting the target of an Aladin object with a string or a SkyCoord object.

    Parameters
    ----------
    target : str
        The target string.

    """
    aladin._survey_body = "sky"
    aladin.target = target
    parsed_target = _parse_coordinate_string(target)
    assert np.isclose(aladin.target.icrs.ra.deg, parsed_target[0])
    assert np.isclose(aladin.target.icrs.dec.deg, parsed_target[1])


def test_aladin_planetary_string_target_set() -> None:
    aladin._survey_body = "mars"
    parsed_target = _parse_coordinate_string("Olympus Mons", body="mars")
    print(parsed_target)


@pytest.mark.parametrize("target", test_aladin_string_target)
def test_aladin_sky_coord_target_set(target: str, mock_sesame: Callable) -> None:  # noqa: ARG001
    """Test setting and getting the target of an Aladin object with a SkyCoord object.

    Parameters
    ----------
    target : str
        The target string.

    """
    aladin._survey_body = "sky"
    sc_target = _parse_coordinate_string(target)
    aladin.target = (
        Longitude(sc_target[0], unit=u.deg),
        Latitude(sc_target[1], unit=u.deg),
    )
    assert np.isclose(aladin.target.icrs.ra.deg, sc_target[0])
    assert np.isclose(aladin.target.icrs.dec.deg, sc_target[1])


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
