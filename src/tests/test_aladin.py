from typing import Callable, Dict, Iterable, Union

from astropy.coordinates import Angle, SkyCoord, Longitude, Latitude
import astropy.units as u
from astropy.table import Column, Table
import numpy as np
import pytest
from unittest.mock import Mock

from ipyaladin import Aladin
from ipyaladin.elements.error_shape import EllipseError, CircleError
from ipyaladin.utils._coordinate_parser import _parse_coordinate_string

from .test_coordinate_parser import test_is_coordinate_string_values

aladin = Aladin()

# Tell python that the JS part is loaded
# so that adding overlay requests are sent
# through the events/traitlets system.
aladin._is_loaded = True


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


@pytest.mark.parametrize("coord", [(0.0, 0.0), (180.0, 90.0)])
def test_aladin_sky_coord_target_init(coord: tuple, mock_sesame: Callable) -> None:  # noqa: ARG001
    """Test setting the target of an Aladin object with a SkyCoord object at init.

    Parameters
    ----------
    target : astropy.coordinates.SkyCoord
        The target coordinate.
    """
    sky_coordinate = SkyCoord(*coord, unit=u.deg, frame="icrs")
    test_aladin = Aladin(target=sky_coordinate)
    assert test_aladin.target == sky_coordinate


test_aladin_fov = [
    0,
    360,
    180,
    -180,
    720,
    0 * u.deg,
    45 * u.deg,
]


@pytest.mark.parametrize("angle", test_aladin_fov)
def test_aladin_float_fov_set(angle: Union[float, u.Quantity]) -> None:
    """Test setting the angle of an Aladin object with a float.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    aladin.fov = angle
    if hasattr(angle, "unit"):
        angle = angle.to_value(u.deg)
    assert aladin.fov.deg == angle


@pytest.mark.parametrize("angle", test_aladin_fov)
def test_aladin_angle_fov_set(angle: Union[float, u.Quantity]) -> None:
    """Test setting the angle of an Aladin object with an Angle object.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    angle_fov = Angle(angle, unit="deg")
    aladin.fov = angle_fov
    assert aladin.fov.deg == angle_fov.deg


test_aladin_rotation = [
    0,
    360,
    180,
    -180,
    720,
    0 * u.deg,
    180 * u.deg,
]


@pytest.mark.parametrize("angle", test_aladin_rotation)
def test_aladin_rotation_set(angle: Union[float, u.Quantity]) -> None:
    """Test setting the rotation of an Aladin object with a float or Quantity.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    aladin.rotation = angle
    if hasattr(angle, "unit"):
        angle = angle.to_value(u.deg)
    assert aladin.rotation.deg == angle


@pytest.mark.parametrize("angle", test_aladin_rotation[:-2])
def test_aladin_angle_rotation_set(angle: Union[float, u.Quantity]) -> None:
    """Test setting the rotation of an Aladin object with an Angle object.

    Parameters
    ----------
    angle : float
        The angle to set.

    """
    angle_rotation = Angle(angle, unit="deg")
    aladin.rotation = angle_rotation
    assert aladin.rotation.deg == angle_rotation.deg


@pytest.mark.parametrize("angle", test_aladin_rotation)
def test_aladin_init_rotation(angle: Union[float, u.Quantity]) -> None:
    """Test initializing an Aladin object with rotation set.

    Parameters
    ----------
    angle : float, astropy.units.Quantity
        The angle to set.

    """
    test_aladin = Aladin(rotation=angle)
    if hasattr(angle, "unit"):
        angle = angle.to_value(u.deg)
    assert test_aladin.rotation.deg == angle


test_stcs_iterables = [
    "CIRCLE ICRS 258.93205686 43.13632863 0.625",
    [
        "POLYGON ICRS 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
        "CIRCLE ICRS 259.29230291 42.63394602 0.625",
    ],
    "POLYGON ICRS 259.254026 43.196761 259 43 259.202 43.118 259.254026 43.196761",
    (
        "POLYGON ICRS 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
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
    stcs_strings: Union[Iterable[str], str],
) -> None:
    """Test generating region overlay info from iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : non-Iterables
        The stcs strings to create region overlay info from.

    """
    with pytest.raises(TypeError) as info:
        aladin.add_graphic_overlay_from_stcs(stcs_strings)
    assert info.type is TypeError


test_multiple_overlays = [
    [
        [
            "POLYGON ICRS 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
            "CIRCLE ICRS 259.29230291 42.63394602 0.625",
        ],
        {
            "name": ["first", "second"],
            "color": ["blue", "pink"],
            "linewidth": [2, 3],
        },
    ],
    [
        (
            "CIRCLE ICRS 259.29230291 42.63394602 0.625",
            "POLYGON ICRS 257 38 261.005016 50.011125 278.305761 46.00127 257 38",
            "CIRCLE ICRS 259.29230291 42.63394602 0.625",
        ),
        {
            "name": ["circle", "polygon", "circle2"],
            "color": ["red", "blue", "yellow"],
            "linewidth": [4, 5, 6],
        },
    ],
]


@pytest.mark.parametrize("info", test_multiple_overlays)
def test_add_graphic_overlays_from_stcs_iterables(
    monkeypatch: Callable,
    info: Iterable,
) -> None:
    """Test generating multiple region overlay infos from iterable STC-S string(s).

    Parameters
    ----------
    info : Iterable[Iterable, dict]
        A list of the stcs strings to create region overlay infos from and the
        associated overlay options.

    """
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    stcs_strings = info[0]
    options = info[1]

    aladin.add_graphic_overlay_from_stcs(stcs_strings, **options)
    for x in range(len(mock_send.call_args_list)):
        regions_info = mock_send.call_args_list[x][0][0]["regions_infos"]
        assert isinstance(regions_info, list)
        assert regions_info[0]["infos"]["stcs"] == stcs_strings[x]
        assert regions_info[0]["options"]["name"] == options["name"][x]
        assert regions_info[0]["options"]["color"] == options["color"][x]
        assert regions_info[0]["options"]["linewidth"] == options["linewidth"][x]


def test_add_table(monkeypatch: Callable) -> None:
    """Test generating region overlay info from iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : Union[Iterable[str], str]
        The stcs strings to create region overlay info from.

    """
    table = Table({"a": [1, 2, 3]})
    table["a"].unit = "deg"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    # normal table call
    aladin.add_table(table)
    table_sent_message = mock_send.call_args[0][0]
    assert table_sent_message["event_name"] == "add_table"

    # circle error
    aladin.add_table(
        table, shape=CircleError(radius="a", default_shape="cross"), color="pink"
    )
    table_sent_message = mock_send.call_args[0][0]
    assert table_sent_message["options"]["circle_error"] == {
        "radius": "a",
        "conversion_radius": 1,
    }
    assert table_sent_message["options"]["shape"] == "cross"

    # ellipse error
    aladin.add_table(table, shape=EllipseError(maj_axis="a", min_axis="a", angle="a"))
    table_sent_message = mock_send.call_args[0][0]
    ellipse_options = {
        "maj_axis": "a",
        "min_axis": "a",
        "angle": "a",
        "conversion_angle": 1,
        "conversion_min_axis": 1,
        "conversion_maj_axis": 1,
    }
    assert table_sent_message["options"]["ellipse_error"] == ellipse_options


test_options_list = [
    {
        "name": ["polygon", "polygon2"],
        "color": ["blue", "pink"],
        "linewidth": [3, 7],
        "num_entries": 2,
    },
    {
        "name": ["circle", "poly", "circle_2"],
        "color": ["blue", "pink", "yellow"],
        "linewidth": [3, 4, 5],
        "num_entries": 3,
    },
]


@pytest.mark.parametrize("options", test_options_list)
def test_vectorize_kwargs(
    options: dict,
) -> None:
    """Test proper parsing for kwargs of lists.

    Parameters
    ----------
    options : dict
        The dictionary of overlay options.
    """
    num_entries = options.pop("num_entries")
    last_ind = num_entries - 1
    options_list = aladin._vectorize_kwargs(num_entries, **options)

    assert len(options_list) == num_entries
    assert options_list[0]["name"] == options["name"][0]
    assert options_list[last_ind]["name"] == options["name"][last_ind]
    assert options_list[0]["color"] == options["color"][0]
    assert options_list[last_ind]["linewidth"] == options["linewidth"][last_ind]


test_invalid_types_options_list = [
    {
        "name": ["polygon", "polygon2"],
        "color": ["blue", "pink"],
        "linewidth": 3,
        "num_entries": 2,
    },
    {
        "name": "polygon",
        "color": ["blue", "pink", "yellow"],
        "linewidth": [3, 4, 5],
        "num_entries": 3,
    },
]


@pytest.mark.parametrize("options", test_invalid_types_options_list)
def test_vectorize_kwargs_wrong_type(
    options: dict,
) -> None:
    """Test TypeError raised when parsing non-list/tuple kwargs.

    Parameters
    ----------
    options : dict
        The dictionary of overlay options.
    """
    num_entries = options.pop("num_entries")

    with pytest.raises(TypeError) as info:
        aladin._vectorize_kwargs(num_entries, **options)

    assert info.type is TypeError
    assert "but expected list/tuple" in str(info.value)


test_invalid_len_options_list = [
    {
        "name": ["polygon", "polygon2"],
        "color": ["blue", "pink"],
        "linewidth": [3],
        "num_entries": 2,
    },
    {
        "name": ["polygon"],
        "color": ["blue", "pink", "yellow"],
        "linewidth": [3, 4, 5],
        "num_entries": 3,
    },
]


@pytest.mark.parametrize("options", test_invalid_len_options_list)
def test_vectorize_kwargs_invalid_len(
    options: dict,
) -> None:
    """Test ValueError raised when parsing wrong length list for kwarg.

    Parameters
    ----------
    options : dict
        The dictionary of overlay options.
    """
    num_entries = options.pop("num_entries")

    with pytest.raises(ValueError) as info:
        aladin._vectorize_kwargs(num_entries, **options)

    assert info.type is ValueError
    assert f"but expected length {num_entries}" in str(info.value)
