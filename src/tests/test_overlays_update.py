from astropy.table import Table
from astropy.coordinates import SkyCoord, Angle

from ipyaladin import Aladin
from ipyaladin.overlays.overlay import Overlay
from ipyaladin.elements.error_shape import CircleError
from regions import CircleSkyRegion
from ipyaladin import Marker


def test_overlays_dict_add_markers() -> None:
    """Test overlays_dict overlay info from adding markers."""
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

    assert test_name not in aladin._overlays_dict
    assert test_name + "_1" in aladin._overlays_dict
    assert marker_overlay.name == updated_options["name"]
    assert marker_overlay.options == updated_options


def test_overlays_dict_add_catalog_from_URL() -> None:
    """Test overlays_dict overlay info from adding catalog using its URL."""
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

    assert test_name not in aladin._overlays_dict
    assert test_name + "_1" in aladin._overlays_dict
    assert url_overlay.name == updated_options["name"]
    assert url_overlay.options == updated_options


def test_overlays_dict_add_table() -> None:
    """Test overlays_dict overlay info from a table."""
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

    assert test_name not in aladin._overlays_dict
    assert test_name + "_1" in aladin._overlays_dict
    assert table_overlay.name == updated_options["name"]
    assert table_overlay.options == updated_options


def test_overlays_dict_add_graphic_overlay_from_region() -> None:
    """Test overlays_dict overlay info from adding region overlay."""
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

    assert test_name not in aladin._overlays_dict
    assert test_name + "_1" in aladin._overlays_dict
    assert region_overlay.name == updated_options["name"]
    assert region_overlay.options["color"] == updated_options["color"]
    assert region_overlay.options == updated_options


def test_overlays_dict_add_graphic_overlay_from_stcs_() -> None:
    """Test overlays_dict overlay info from adding iterable STC-S string(s)."""
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

    assert test_name not in aladin._overlays_dict
    assert test_name + "_1" in aladin._overlays_dict
    assert stcs_overlay.name == updated_options["name"]
    assert stcs_overlay.options["color"] == updated_options["color"]
    assert stcs_overlay.options == updated_options
