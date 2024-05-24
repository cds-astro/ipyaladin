"""
Aladin Lite widget for Jupyter Notebook.

This module provides a Python wrapper around the Aladin Lite JavaScript library.
It allows to display astronomical images and catalogs in an interactive way.
"""

import pathlib
import typing
from typing import ClassVar, Union, Final, Optional
import warnings

import anywidget
from astropy.table.table import QTable
from astropy.table import Table
from astropy.coordinates import SkyCoord, Angle
import traitlets

try:
    from regions import (
        CircleSkyRegion,
        EllipseSkyRegion,
        LineSkyRegion,
        PolygonSkyRegion,
        RectangleSkyRegion,
        Region,
        Regions,
    )
except ImportError:
    CircleSkyRegion = None
    EllipseSkyRegion = None
    LineSkyRegion = None
    PolygonSkyRegion = None
    RectangleSkyRegion = None
    Region = None
    Regions = None
from traitlets import (
    Float,
    Int,
    Unicode,
    Bool,
    Any,
    default,
)

from .coordinate_parser import parse_coordinate_string

SupportedRegion = Union[
    typing.List[
        Union[
            CircleSkyRegion,
            EllipseSkyRegion,
            LineSkyRegion,
            PolygonSkyRegion,
            RectangleSkyRegion,
        ]
    ],
    CircleSkyRegion,
    EllipseSkyRegion,
    LineSkyRegion,
    PolygonSkyRegion,
    RectangleSkyRegion,
    Regions,
]


class Aladin(anywidget.AnyWidget):
    """Aladin Lite widget.

    This widget is a Python wrapper around the Aladin Lite JavaScript library.
    It allows to display astronomical images and catalogs in an interactive way.
    """

    _esm: Final = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css: Final = pathlib.Path(__file__).parent / "static" / "widget.css"

    # Options for the view initialization
    height = Int(400).tag(sync=True, init_option=True)
    _target = Unicode(
        "0 0",
        help="A private trait that stores the current target of the widget in a string."
        " Its public version is the 'target' property that returns an "
        "`~astropy.coordinates.SkyCoord` object",
    ).tag(sync=True, init_option=True)
    _fov = Float(
        60.0,
        help="A private trait that stores the current field of view of the widget."
        " Its public version is the 'fov' property that returns an "
        "`~astropy.units.Angle` object",
    ).tag(sync=True, init_option=True)
    survey = Unicode("https://alaskybis.unistra.fr/DSS/DSSColor").tag(
        sync=True, init_option=True
    )
    coo_frame = Unicode("J2000").tag(sync=True, init_option=True)
    projection = Unicode("SIN").tag(sync=True, init_option=True)
    samp = Bool(False).tag(sync=True, init_option=True)
    # Buttons on/off
    background_color = Unicode("rgb(60, 60, 60)").tag(sync=True, init_option=True)
    show_zoom_control = Bool(False).tag(sync=True, init_option=True)
    show_layers_control = Bool(True).tag(sync=True, init_option=True)
    show_overlay_stack_control = Bool(True).tag(sync=True, init_option=True)
    show_fullscreen_control = Bool(True).tag(sync=True, init_option=True)
    show_simbad_pointer_control = Bool(True).tag(sync=True, init_option=True)
    show_settings_control = Bool(True).tag(sync=True, init_option=True)
    show_share_control = Bool(False).tag(sync=True, init_option=True)
    show_status_bar = Bool(True).tag(sync=True, init_option=True)
    show_frame = Bool(True).tag(sync=True, init_option=True)
    show_fov = Bool(True).tag(sync=True, init_option=True)
    show_coo_location = Bool(True).tag(sync=True, init_option=True)
    show_projection_control = Bool(True).tag(sync=True, init_option=True)
    show_context_menu = Bool(True).tag(sync=True, init_option=True)
    show_catalog = Bool(True).tag(sync=True, init_option=True)
    full_screen = Bool(False).tag(sync=True, init_option=True)
    # reticle
    show_reticle = Bool(True).tag(sync=True, init_option=True)
    reticle_color = Unicode("rgb(178, 50, 178)").tag(sync=True, init_option=True)
    reticle_size = Int(20).tag(sync=True, init_option=True)
    # grid
    show_coo_grid = Bool(False).tag(sync=True, init_option=True)
    show_coo_grid_control = Bool(True).tag(sync=True, init_option=True)
    grid_color = Unicode("rgb(178, 50, 178)").tag(sync=True, init_option=True)
    grid_opacity = Float(0.5).tag(sync=True, init_option=True)
    grid_options = traitlets.Dict().tag(sync=True, init_option=True)

    # content of the last click
    clicked_object = traitlets.Dict().tag(sync=True)
    # listener callback is on the python side and contains functions to link to events
    listener_callback: ClassVar[typing.Dict[str, callable]] = {}

    # overlay survey
    overlay_survey = Unicode("").tag(sync=True, init_option=True)
    overlay_survey_opacity = Float(0.0).tag(sync=True, init_option=True)

    init_options = traitlets.List(trait=Any()).tag(sync=True)

    @default("init_options")
    def _init_options(self) -> typing.List[str]:
        return list(self.traits(init_option=True))

    def __init__(self, *args: any, **kwargs: any) -> None:
        super().__init__(*args, **kwargs)
        self.target = kwargs.get("target", "0 0")
        self.fov = kwargs.get("fov", 60.0)
        self.on_msg(self._handle_custom_message)

    def _handle_custom_message(self, _: any, message: dict, __: any) -> None:
        event_type = message["event_type"]
        message_content = message["content"]
        if (
            event_type == "object_clicked"
            and "object_clicked" in self.listener_callback
        ):
            self.listener_callback["object_clicked"](message_content)
        elif (
            event_type == "object_hovered"
            and "object_hovered" in self.listener_callback
        ):
            self.listener_callback["object_hovered"](message_content)
        elif event_type == "click" and "click" in self.listener_callback:
            self.listener_callback["click"](message_content)
        elif event_type == "select" and "select" in self.listener_callback:
            self.listener_callback["select"](message_content)

    @property
    def fov(self) -> Angle:
        """The field of view of the Aladin Lite widget along the horizontal axis.

        It can be set with either a float in degrees
        or an `~astropy.units.Angle` object.

        Returns
        -------
        Angle
            An astropy.units.Angle object representing the field of view.

        """
        return Angle(self._fov, unit="deg")

    @fov.setter
    def fov(self, fov: Union[float, Angle]) -> None:
        if isinstance(fov, Angle):
            fov = fov.deg
        self._fov = fov
        self.send({"event_name": "change_fov", "fov": fov})

    @property
    def target(self) -> SkyCoord:
        """The target of the Aladin Lite widget.

        It can be set with either a string or an `~astropy.coordinates.SkyCoord` object.

        Returns
        -------
        SkyCoord
            An astropy.coordinates.SkyCoord object representing the target.

        """
        ra, dec = self._target.split(" ")
        return SkyCoord(
            ra=ra,
            dec=dec,
            frame="icrs",
            unit="deg",
        )

    @target.setter
    def target(self, target: Union[str, SkyCoord]) -> None:
        if isinstance(target, str):  # If the target is str, parse it
            target = parse_coordinate_string(target)
        elif not isinstance(target, SkyCoord):  # If the target is not str or SkyCoord
            raise ValueError(
                "target must be a string or an astropy.coordinates.SkyCoord object"
            )
        self._target = f"{target.icrs.ra.deg} {target.icrs.dec.deg}"
        self.send(
            {
                "event_name": "goto_ra_dec",
                "ra": target.icrs.ra.deg,
                "dec": target.icrs.dec.deg,
            }
        )

    def add_catalog_from_URL(
        self, votable_URL: str, votable_options: Optional[dict] = None
    ) -> None:
        """Load a VOTable table from an url and load its data into the widget.

        Parameters
        ----------
        votable_URL: str
        votable_options: dict

        """
        if votable_options is None:
            votable_options = {}
        self.send(
            {
                "event_name": "add_catalog_from_URL",
                "votable_URL": votable_URL,
                "options": votable_options,
            }
        )

    # MOCs

    def add_moc(self, moc: any, **moc_options: any) -> None:
        """Add a MOC to the Aladin-Lite widget.

        Parameters
        ----------
        moc : `~mocpy.MOC` or str or dict
            The MOC can be provided as a `mocpy.MOC` object, as a string containing an
            URL where the MOC can be retrieved, or as a dictionary where the keys are
            the HEALPix orders and the values are the pixel indices
            (ex: {"1":[1,2,4], "2":[12,13,14,21,23,25]}).

        """
        if isinstance(moc, dict):
            self.send(
                {
                    "event_name": "add_MOC_from_dict",
                    "moc_dict": moc,
                    "options": moc_options,
                }
            )
        elif isinstance(moc, str) and "://" in moc:
            self.send(
                {
                    "event_name": "add_MOC_from_URL",
                    "moc_URL": moc,
                    "options": moc_options,
                }
            )
        else:
            try:
                from mocpy import MOC

                if isinstance(moc, MOC):
                    self.send(
                        {
                            "event_name": "add_MOC_from_dict",
                            "moc_dict": moc.serialize("json"),
                            "options": moc_options,
                        }
                    )
            except ImportError as imp:
                raise ValueError(
                    "A MOC can be given as an URL, a dictionnary, or a mocpy.MOC "
                    "object. To read mocpy.MOC objects, you need to install the mocpy "
                    "library with 'pip install mocpy'."
                ) from imp

    def add_moc_from_URL(
        self, moc_URL: str, moc_options: Optional[dict] = None
    ) -> None:
        """Load a MOC from a URL and display it in Aladin Lite widget.

        Parameters
        ----------
        moc_URL: str
            An URL to retrieve the MOC from
        moc_options: dict

        """
        warnings.warn(
            "add_moc_from_URL is replaced by add_moc that detects automatically"
            "that the MOC was given as an URL.",
            DeprecationWarning,
            stacklevel=2,
        )
        if moc_options is None:
            moc_options = {}
        self.add_moc(moc_URL, **moc_options)

    def add_moc_from_dict(
        self, moc_dict: dict, moc_options: Optional[dict] = None
    ) -> None:
        """Load a MOC from a dict object and display it in Aladin Lite widget.

        Parameters
        ----------
        moc_dict: dict
            It contains the MOC cells. Key are the HEALPix orders, values are the pixel
            indexes, eg: {"1":[1,2,4], "2":[12,13,14,21,23,25]}
        moc_options: dict

        """
        warnings.warn(
            "add_moc_from_dict is replaced by add_moc that detects automatically"
            "that the MOC was given as a dictionary.",
            DeprecationWarning,
            stacklevel=2,
        )
        if moc_options is None:
            moc_options = {}
        self.add_moc(moc_dict, **moc_options)

    def add_table(self, table: Union[QTable, Table], **table_options: any) -> None:
        """Load a table into the widget.

        Parameters
        ----------
        table : astropy.table.table.QTable or astropy.table.table.Table
                table that must contain coordinates information

        Examples
        --------
        Cell 1:
        >>> from ipyaladin import Aladin
        >>> from astropy.table import QTable
        >>> aladin = Aladin(fov=2, target='M1')
        >>> aladin
        Cell 2:
        >>> ra = [83.63451584700, 83.61368056017, 83.58780251600]
        >>> dec = [22.05652591227, 21.97517807639, 21.99277764451]
        >>> name = ["Gaia EDR3 3403818589184411648",
                    "Gaia EDR3 3403817661471500416",
                    "Gaia EDR3 3403817936349408000",
                   ]
        >>> table = QTable([ra, dec, name],
                            names=("ra", "dec", "name"),
                            meta={"name": "my sample table"})
        >>> aladin.add_table(table)
        And the table should appear in the output of Cell 1!

        """
        import io

        table_bytes = io.BytesIO()
        table.write(table_bytes, format="votable")
        self.send(
            {"event_name": "add_table", "options": table_options},
            buffers=[table_bytes.getvalue()],
        )

    def add_graphic_overlay_from_region(
        self,
        region: SupportedRegion,
        **graphic_options: any,
    ) -> None:
        """Add an overlay graphic layer to the Aladin Lite widget.

        Parameters
        ----------
        region: `~regions.CircleSkyRegion`, `~regions.EllipseSkyRegion`,
        `~regions.LineSkyRegion`,`~regions.PolygonSkyRegion`,
        `~regions.RectangleSkyRegion`, `~regions.Regions`, or a list of these.
            The region(s) to add in Aladin Lite. It can be given as a supported region
            or a list of regions from the
            `regions package<https://astropy-regions.readthedocs.io>`_.
        graphic_options: keyword arguments
            The options for the graphic overlay. Use Region visual for region options.
            See the Aladin Lite
            `graphicOverlay options<https://cds-astro.github.io/aladin-lite/A.html>`_

        See Also
        --------
        add_graphic_overlay_from_stcs: for shapes described as STC-S strings.

        Notes
        -----
        The possible `~regions.RegionVisual` options correspond to the
        Aladin Lite / ipyaladin parameters:

        | RegionVisual |      AladinLite     |        ipyaladin     |
        |--------------|---------------------|----------------------|
        | edgecolor    | color               | color                |
        | facecolor    | fillColor           | fill_color           |
        | color        | color and fillColor | color and fill_color |
        | alpha        | opacity             | opacity              |
        | linewidth    | lineWidth           | line_width           |

        """
        if Region is None:
            raise ModuleNotFoundError(
                "To read regions objects, you need to install the regions library with "
                "'pip install regions'."
            )

        # Check if the region is a list of regions or a single
        # Region and convert it to a list of Regions
        if isinstance(region, Regions):
            region_list = region.regions
        elif not isinstance(region, list):
            region_list = [region]
        else:
            region_list = region

        regions_infos = []
        for region_element in region_list:
            # Check if the regions library is installed and raise an error if not
            if not isinstance(region_element, Region):
                raise ValueError(
                    "region must a `~regions` object or a list of `~regions` objects. "
                    "See the documentation for the supported region types."
                )

            from .region_converter import RegionInfos

            # Define behavior for each region type
            regions_infos.append(RegionInfos(region_element).to_clean_dict())

        self.send(
            {
                "event_name": "add_overlay",
                "regions_infos": regions_infos,
                "graphic_options": graphic_options,
            }
        )

    def add_overlay_from_stcs(
        self, stc_string: Union[typing.List[str], str], **overlay_options: any
    ) -> None:
        """Add an overlay layer defined by an STC-S string.

        Parameters
        ----------
        stc_string: str, list[str]
            The STC-S string or a list of STC-S strings.
        overlay_options: keyword arguments
            The overlay options for all the STC-S strings

        """
        warnings.warn(
            "'add_overlay_from_stcs' is deprecated, "
            "use 'add_graphic_overlay_from_stcs' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_graphic_overlay_from_stcs(stc_string, **overlay_options)

    def add_graphic_overlay_from_stcs(
        self, stc_string: Union[typing.List[str], str], **overlay_options: any
    ) -> None:
        """Add an overlay layer defined by an STC-S string.

        Parameters
        ----------
        stc_string: str, list[str]
            The STC-S string or a list of STC-S strings.
        overlay_options: keyword arguments
            The overlay options for all the STC-S strings.

        See Also
        --------
        add_graphic_overlay_from_region: if the shape is in an astropy `~regions`
        object.

        """
        region_list = [stc_string] if not isinstance(stc_string, list) else stc_string

        regions_infos = [
            {
                "region_type": "stcs",
                "infos": {"stcs": region_element},
                "options": overlay_options,
            }
            for region_element in region_list
        ]
        self.send(
            {
                "event_name": "add_overlay",
                "regions_infos": regions_infos,
                "graphic_options": {},
            }
        )

    def get_JPEG_thumbnail(self) -> None:
        """Create a popup window with the current Aladin view."""
        self.send({"event_name": "get_JPG_thumbnail"})

    def set_color_map(self, color_map_name: str) -> None:
        """Change the color map of the Aladin Lite widget.

        Parameters
        ----------
        color_map_name: str
            The name of the color map to use.

        """
        self.send({"event_name": "change_colormap", "colormap": color_map_name})

    def rectangular_selection(self) -> None:
        """Trigger the rectangular selection tool."""
        self.send({"event_name": "trigger_rectangular_selection"})

    # Adding a listener

    def set_listener(self, listener_type: str, callback: callable) -> None:
        """Set a listener for an event to the widget.

        Parameters
        ----------
        listener_type: str
            Can either be 'object_hovered', 'object_clicked', 'click' or 'select'
        callback: callable
            A python function to be called when the event corresponding to the
            listener_type is detected

        """
        if listener_type in {"objectHovered", "object_hovered"}:
            self.listener_callback["object_hovered"] = callback
        elif listener_type in {"objectClicked", "object_clicked"}:
            self.listener_callback["object_clicked"] = callback
        elif listener_type == "click":
            self.listener_callback["click"] = callback
        elif listener_type == "select":
            self.listener_callback["select"] = callback
        else:
            raise ValueError(
                "listener_type must be 'object_hovered', "
                "'object_clicked', 'click' or 'select'"
            )

    def add_listener(self, listener_type: str, callback: callable) -> None:
        """Add a listener to the widget. Use set_listener instead.

        Parameters
        ----------
        listener_type: str
            Can either be 'object_hovered', 'object_clicked', 'click' or 'select'
        callback: callable
            A python function to be called when the event corresponding to the
            listener_type is detected

        Notes
        -----
        This method is deprecated, use set_listener instead

        """
        warnings.warn(
            "add_listener is deprecated, use set_listener instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.set_listener(listener_type, callback)
