from typing import Callable, Dict, Iterable, Union

from astropy.coordinates import Angle, SkyCoord, Longitude, Latitude
import astropy.units as u
from astropy.table import Column
import numpy as np
import pytest
from unittest.mock import Mock

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


test_stcs_iterables = [
    "CIRCLE ICRS 258.93205686 43.13632863 0.625",
    [
        "POLYGON 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
        "CIRCLE ICRS 259.29230291 42.63394602 0.625",
    ],
    "POLYGON 259.254026 43.196761 259 43 259.202134 43.118653 259.254026 43.196761",
    (
        "POLYGON 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
        "CIRCLE ICRS 259.29230291 42.63394602 0.625",
    ),
    Column(
        name="s_regions",
        data=[
            "CIRCLE ICRS 259.29230291 42.63394602 0.625",
            "CIRCLE ICRS 259.22668619 42.76082126 0.625",
            "CIRCLE ICRS 258.93205686 43.13632863 0.625",
        ],
    ),
]


@pytest.mark.parametrize("stcs_strings", test_stcs_iterables)
def test_add_graphic_overlay_from_stcs_iterables(
    monkeypatch: Callable,
    stcs_strings: Union[Iterable[str], str],
) -> None:
    """Test generating region overlay info from iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : Union[Iterable[str], str]
        The stcs strings to create region overlay info from.

    """
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)
    aladin.add_graphic_overlay_from_stcs(stcs_strings)
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert isinstance(regions_info, list)
    assert regions_info[0]["infos"]["stcs"] in stcs_strings


test_stcs_noniterables = [
    0,
    1000,
    -100,
    np.nan,
]


@pytest.mark.parametrize("stcs_strings", test_stcs_noniterables)
def test_add_graphic_overlay_from_stcs_noniterables(
    monkeypatch: Callable,
    stcs_strings: Union[Iterable[str], str],
) -> None:
    """Test generating region overlay info from iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : non-Iterables
        The stcs strings to create region overlay info from.

    """
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)
    with pytest.raises(TypeError) as info:
        aladin.add_graphic_overlay_from_stcs(stcs_strings)
    assert info.type is TypeError
