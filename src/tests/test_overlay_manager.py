from astropy.table import Table
from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
import pytest
from unittest.mock import Mock
import warnings
import re
from typing import Callable, Iterable, Union

from ipyaladin import Aladin
from ipyaladin.overlays.overlay import Overlay, OverlayType
from ipyaladin.elements.error_shape import EllipseError, CircleError
from regions import CircleSkyRegion
from ipyaladin import Marker


aladin = Aladin()
aladin._is_loaded = True


def test_overlay_manager_add_markers(
    monkeypatch: Callable,
) -> None:
    """Test _overlay_manager overlay info from adding markers."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    markers = []
    for i in range(1, 11):
        name = f"M{i}"
        markers.append(
            Marker(
                position=name,
                title=name,
                description=(
                    '<a href="https://simbad.cds.unistra.fr/simbad/'
                    f'sim-basic?Ident={name}&submit=SIMBAD+search"> '
                    "Read more on SIMBAD</a>"
                ),
            )
        )
    options = {"name": test_name, "color": "pink", "shape": "cross", "source_size": 15}

    aladin.add_markers(
        markers, name=test_name, color="pink", shape="cross", source_size=15
    )

    assert test_name in aladin._overlay_manager
    assert aladin._overlay_manager[test_name]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    assert sent_message["options"] == options

    # test handling for a catalog with existing name
    with warnings.catch_warnings(record=True) as w:
        aladin.add_markers(
            markers, name=test_name, color="pink", shape="cross", source_size=15
        )
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in aladin._overlay_manager
    assert aladin._overlay_manager[test_name + "_1"]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    options["name"] = test_name + "_1"
    assert sent_message["options"] == options

    # test handling for catalog with no given name
    options["name"] = "catalog_python"
    aladin.add_markers(markers, color="pink", shape="cross", source_size=15)

    assert "catalog_python" in aladin._overlay_manager
    assert aladin._overlay_manager["catalog_python"]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    assert sent_message["options"] == options

    # test removing these overlays, resetting for next functionality check
    aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not aladin._overlay_manager.keys()


def test_overlay_manager_add_catalog_from_URL(
    monkeypatch: Callable,
) -> None:
    """Test _overlay_manager overlay info from adding catalog using its URL."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    url = (
        "https://vizier.unistra.fr/viz-bin/votable?-source=HIP2&-c=LMC&-out.add=_RAJ,_"
        "DEJ&-oc.form=dm&-out.meta=DhuL&-out.max=9999&-c.rm=180"
    )
    options = {
        "source_size": 12,
        "color": "#f08080",
        "on_click": "showTable",
        "name": test_name,
    }
    aladin.add_catalog_from_URL(url, options)

    assert test_name in aladin._overlay_manager
    assert aladin._overlay_manager[test_name]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    assert sent_message["options"] == options

    # test handling for a catalog with existing name
    with warnings.catch_warnings(record=True) as w:
        aladin.add_catalog_from_URL(url, options)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in aladin._overlay_manager
    assert aladin._overlay_manager[test_name + "_1"]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    options["name"] = test_name + "_1"
    assert sent_message["options"] == options

    # test handling for catalog with no given name
    options.pop("name")
    aladin.add_catalog_from_URL(url, options)

    assert "catalog_python" in aladin._overlay_manager
    assert aladin._overlay_manager["catalog_python"]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    options["name"] = "catalog_python"
    assert sent_message["options"] == options

    # test removing these overlays, resetting for next functionality check
    aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not aladin._overlay_manager.keys()


def test_overlay_manager_add_table(monkeypatch: Callable) -> None:
    """Test _overlay_manager overlay info from a table."""
    test_name = "test"
    table = Table({"a": [1, 2, 3]})
    table["a"].unit = "deg"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    # normal table call
    aladin.add_table(table, name=test_name)
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_table"

    assert test_name in aladin._overlay_manager
    assert aladin._overlay_manager[test_name]["type"] == "table"
    assert all(aladin._overlay_manager[test_name]["table"] == table)

    # circle error
    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        aladin.add_table(
            table,
            shape=CircleError(radius="a", default_shape="cross"),
            color="pink",
            name=test_name,
        )
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    sent_message = mock_send.call_args[0][0]
    assert sent_message["options"]["circle_error"] == {
        "radius": "a",
        "conversion_radius": 1,
    }
    assert sent_message["options"]["shape"] == "cross"

    assert test_name + "_1" in aladin._overlay_manager
    assert aladin._overlay_manager[test_name + "_1"]["type"] == "table"
    assert all(aladin._overlay_manager[test_name + "_1"]["table"] == table)
    assert aladin._overlay_manager[test_name + "_1"]["options"]["color"] == "pink"
    assert "circle_error" in aladin._overlay_manager[test_name + "_1"]["options"]

    # ellipse error
    aladin.add_table(table, shape=EllipseError(maj_axis="a", min_axis="a", angle="a"))
    sent_message = mock_send.call_args[0][0]
    ellipse_options = {
        "maj_axis": "a",
        "min_axis": "a",
        "angle": "a",
        "conversion_angle": 1,
        "conversion_min_axis": 1,
        "conversion_maj_axis": 1,
    }
    assert sent_message["options"]["ellipse_error"] == ellipse_options

    assert "catalog_python" in aladin._overlay_manager
    assert aladin._overlay_manager["catalog_python"]["type"] == "table"
    assert all(aladin._overlay_manager["catalog_python"]["table"] == table)

    # test removing these overlays, resetting for next functionality check
    aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not aladin._overlay_manager.keys()


def test_overlay_manager_add_graphic_overlay_from_region(
    monkeypatch: Callable,
) -> None:
    """Test _overlay_manager overlay info from adding region overlay."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    center = SkyCoord.from_name("M31")
    radius = Angle(0.5, "deg")
    circle = CircleSkyRegion(
        center=center, radius=Angle(0.5, "deg"), visual={"edgecolor": "yellow"}
    )
    aladin.add_graphic_overlay_from_region([circle], name=test_name)

    assert test_name in aladin._overlay_manager
    assert aladin._overlay_manager[test_name]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager[test_name]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        aladin.add_graphic_overlay_from_region([circle], name=test_name)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in aladin._overlay_manager
    assert aladin._overlay_manager[test_name + "_1"]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager[test_name + "_1"]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test handling for overlay with no given name
    aladin.add_graphic_overlay_from_region([circle])

    assert "overlay_python" in aladin._overlay_manager
    assert aladin._overlay_manager["overlay_python"]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager["overlay_python"]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test removing these overlays, resetting for next functionality check
    aladin.remove_overlay([test_name, test_name + "_1", "overlay_python"])
    assert not aladin._overlay_manager.keys()


test_stcs_iterables = [
    "CIRCLE ICRS 258.93205686 43.13632863 0.625",
]


@pytest.mark.parametrize("stcs_strings", test_stcs_iterables)
def test_overlay_manager_add_graphic_overlay_from_stcs_(
    monkeypatch: Callable,
    stcs_strings: Union[Iterable[str], str],
) -> None:
    """Test _overlay_manager overlay info from adding iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : Union[Iterable[str], str]
        The stcs strings to create region overlay info from.

    """
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)
    aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)

    assert test_name in aladin._overlay_manager
    assert aladin._overlay_manager[test_name]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager[test_name]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in aladin._overlay_manager
    assert aladin._overlay_manager[test_name + "_1"]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager[test_name + "_1"]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test handling for overlay with no given name
    aladin.add_graphic_overlay_from_stcs(stcs_strings)

    assert "overlay_python" in aladin._overlay_manager
    assert aladin._overlay_manager["overlay_python"]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == aladin._overlay_manager["overlay_python"]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test removing these overlays, resetting for next functionality check
    aladin.remove_overlay([test_name, test_name + "_1", "overlay_python"])
    assert not aladin._overlay_manager.keys()


def test_invalid_overlay_type(
    monkeypatch: Callable,
) -> None:
    """Test proper error sent for adding invalid overlay type."""
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    test_invalid_overlay = {"type": "not_valid", "options": {"name": "test_invalid"}}

    # try creating invalid layer to confirm error is raised
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid overlay type 'not_valid'. "
            f"Must be one of {[t.value for t in OverlayType]}."
        ),
    ):
        Overlay(test_invalid_overlay, aladin)


@pytest.mark.parametrize("stcs_strings", test_stcs_iterables)
def test_existing_overlay_name(
    monkeypatch: Callable,
    stcs_strings: Union[Iterable[str], str],
) -> None:
    """Test proper messages sent for existing overlays.

    Parameters
    ----------
    stcs_strings : Union[Iterable[str], str]
        The stcs strings to create region overlay info from.

    """
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)
    aladin.add_graphic_overlay_from_stcs(stcs_strings)
    aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)

    # no name specified, no warning triggered
    aladin.add_graphic_overlay_from_stcs(stcs_strings)

    # name specified, warning triggered
    with pytest.warns(match="is already in use. Name `test_1`"):
        aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)

    assert test_name in aladin._overlay_manager
    assert "overlay_python" in aladin._overlay_manager
    assert "overlay_python_1" in aladin._overlay_manager
    expected_count = 4
    assert len(aladin._overlay_manager.keys()) == expected_count


test_marker_overlay = Overlay(
    {"type": "marker", "options": {"name": "test_markers"}},
    aladin,
)


test_catalog_overlay = Overlay(
    {"type": "catalog", "options": {"name": "test_catalog"}},
    aladin,
)


test_overlays = [
    "overlay",
    test_marker_overlay,
    ["overlay", "overlay_1", "2MASS"],
    "catalog",
    ["overlay_1", "2MASS", test_catalog_overlay],
]


@pytest.mark.parametrize("overlays", test_overlays)
def test_remove_overlay(
    monkeypatch: Callable,
    overlays: Union[Iterable[Union[str, Overlay]], str, Overlay],
) -> None:
    """Test proper messages sent for removing overlays.

    Parameters
    ----------
    overlays : Union[Iterable[Union[str, Overlay]], str, Overlay]
        The name strings of overlays.
    """
    mock_send = Mock()
    monkeypatch.setattr(Aladin, "send", mock_send)

    # generate expected _overlay_manager to remove names from
    if isinstance(overlays, Overlay):
        overlay_names = [overlays.name]
    elif isinstance(overlays, str):
        overlay_names = [overlays]
    elif isinstance(overlays, (list, tuple)):
        overlay_names = [o.name if isinstance(o, Overlay) else o for o in overlays]

    aladin._overlay_manager = {name: {} for name in overlay_names}

    aladin.remove_overlay(overlay_names)

    event_name = mock_send.call_args[0][0]["event_name"]
    assert isinstance(event_name, str)
    assert event_name == "remove_overlay"

    name_info = mock_send.call_args[0][0]["overlay_names"]
    assert isinstance(name_info, list)
    assert name_info[0] in overlay_names

    if isinstance(overlay_names, list):
        assert name_info == overlay_names

    # confirm each overlay was removed from the dict as expected
    assert not aladin._overlay_manager.keys()

    # try removing non-existent layer to confirm error is raised
    with pytest.raises(
        ValueError,
        match=(
            r"Cannot remove overlay `does_not_exist` since this layer does not exist."
        ),
    ):
        aladin.remove_overlay("does_not_exist")


def test_update_add_markers() -> None:
    """Test update overlay info from adding markers."""
    aladin = Aladin()
    aladin._is_loaded = True

    test_name = "test"

    markers = []
    for i in range(1, 11):
        name = f"M{i}"
        markers.append(
            Marker(
                position=name,
                title=name,
                description=(
                    '<a href="https://simbad.cds.unistra.fr/simbad/'
                    f'sim-basic?Ident={name}&submit=SIMBAD+search"> '
                    "Read more on SIMBAD</a>"
                ),
            )
        )
    options = {"name": test_name, "color": "pink", "shape": "cross", "source_size": 15}
    marker_overlay = aladin.add_markers(markers, **options)

    assert type(marker_overlay) is Overlay
    assert marker_overlay.options == options

    updated_options = options.copy()
    updated_options.update(
        {"name": test_name + "_1", "color": "red", "shape": "random", "source_size": 20}
    )

    marker_overlay = marker_overlay.update(**updated_options)

    assert test_name not in aladin._overlay_manager
    assert test_name + "_1" in aladin._overlay_manager
    assert marker_overlay.name == updated_options["name"]
    assert marker_overlay.options == updated_options


def test_update_add_catalog_from_URL() -> None:
    """Test update overlay info from adding catalog using its URL."""
    aladin = Aladin()
    aladin._is_loaded = True

    test_name = "test"

    url = (
        "https://vizier.unistra.fr/viz-bin/votable?-source=HIP2&-c=LMC&-out.add=_RAJ,_"
        "DEJ&-oc.form=dm&-out.meta=DhuL&-out.max=9999&-c.rm=180"
    )
    options = {
        "source_size": 12,
        "color": "#f08080",
        "on_click": "showTable",
        "name": test_name,
    }
    url_overlay = aladin.add_catalog_from_URL(url, options)

    assert type(url_overlay) is Overlay
    assert url_overlay.options == options

    updated_options = options.copy()
    updated_options.update(
        {"name": test_name + "_1", "color": "#66FF00", "source_size": 20}
    )

    url_overlay = url_overlay.update(**updated_options)

    assert test_name not in aladin._overlay_manager
    assert test_name + "_1" in aladin._overlay_manager
    assert url_overlay.name == updated_options["name"]
    assert url_overlay.options == updated_options


def test_update_add_table() -> None:
    """Test update overlay info from a table."""
    aladin = Aladin()
    aladin._is_loaded = True

    test_name = "test"
    table = Table({"a": [1, 2, 3]})
    table["a"].unit = "deg"

    options = {
        "color": "pink",
        "name": test_name,
        "circle_error": {"radius": "a", "conversion_radius": 1},
    }
    table_overlay = aladin.add_table(
        table,
        shape=CircleError(radius="a", default_shape="cross"),
        **options,
    )
    options["shape"] = "cross"

    assert type(table_overlay) is Overlay
    assert table_overlay.options == options

    options.pop("shape")
    updated_options = options.copy()
    updated_options.update({"name": test_name + "_1"})

    table_overlay = table_overlay.update(**updated_options)
    updated_options["shape"] = "cross"

    assert test_name not in aladin._overlay_manager
    assert test_name + "_1" in aladin._overlay_manager
    assert table_overlay.name == updated_options["name"]
    assert table_overlay.options == updated_options


def test_update_add_graphic_overlay_from_region() -> None:
    """Test update overlay info from adding region overlay."""
    aladin = Aladin()
    aladin._is_loaded = True

    test_name = "test"

    circle = CircleSkyRegion(
        center=SkyCoord.from_name("M31"),
        radius=Angle(0.5, "deg"),
        visual={"edgecolor": "yellow"},
    )
    options = {"name": test_name}
    region_overlay = aladin.add_graphic_overlay_from_region([circle], **options)

    assert type(region_overlay) is Overlay
    assert region_overlay.options == options

    updated_options = options.copy()
    updated_options.update({"name": test_name + "_1", "color": "#66FF00"})

    region_overlay = region_overlay.update(**updated_options)

    assert test_name not in aladin._overlay_manager
    assert test_name + "_1" in aladin._overlay_manager
    assert region_overlay.name == updated_options["name"]
    assert region_overlay.options["color"] == updated_options["color"]
    assert region_overlay.options == updated_options


def test_update_add_graphic_overlay_from_stcs_() -> None:
    """Test update overlay info from adding iterable STC-S string(s)."""
    aladin = Aladin()
    aladin._is_loaded = True

    stcs_strings = "CIRCLE ICRS 258.93205686 43.13632863 0.625"
    test_name = "test"
    options = {"name": test_name, "color": "red"}
    stcs_overlay = aladin.add_graphic_overlay_from_stcs(stcs_strings, **options)

    assert type(stcs_overlay) is Overlay
    assert stcs_overlay.options == options

    updated_options = options.copy()
    updated_options.update({"name": test_name + "_1", "color": "#66FF00"})

    stcs_overlay = stcs_overlay.update(**updated_options)

    assert test_name not in aladin._overlay_manager
    assert test_name + "_1" in aladin._overlay_manager
    assert stcs_overlay.name == updated_options["name"]
    assert stcs_overlay.options["color"] == updated_options["color"]
    assert stcs_overlay.options == updated_options
