"""
Aladin Lite widget for Jupyter Notebook.

This module provides a Python wrapper around the Aladin Lite JavaScript library.
It allows to display astronomical images and catalogs in an interactive way.
"""

import math
from collections.abc import Callable
import io
import pathlib
from copy import deepcopy
from json import JSONDecodeError
from pathlib import Path
from typing import ClassVar, Dict, Final, List, Optional, Tuple, Union
import warnings

import anywidget
from astropy.coordinates import SkyCoord, Angle
from astropy.table.table import QTable
from astropy.table import Table
from astropy.io import fits as astropy_fits
from astropy.io.fits import HDUList
import astropy.units as u
from astropy.wcs import WCS
import numpy as np
import traitlets

from .utils.exceptions import WidgetCommunicationError
from .utils._coordinate_parser import parse_coordinate_string

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

SupportedRegion = Union[
    List[
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
    _height = Int(400).tag(sync=True, init_option=True)
    _target = Unicode(
        "0 0",
        help="A private trait that stores the current target of the widget in a string."
        " Its public version is the 'target' property that returns an "
        "`astropy.coordinates.SkyCoord` object",
    ).tag(sync=True, init_option=True)
    _fov = Float(
        60.0,
        help="A private trait that stores the current field of view of the widget."
        " Its public version is the 'fov' property that returns an "
        "`astropy.units.Angle` object",
    ).tag(sync=True, init_option=True)
    survey = Unicode(
        "https://alaskybis.unistra.fr/DSS/DSSColor",
        help="The lowest HiPS in the stack of HiPS.",
    ).tag(
        sync=True,
        init_option=True,
    )
    coo_frame = Unicode(
        "ICRS",
        help="The frame coordinate. Can be either 'ICRS', 'ICRSd', or 'Galactic'.",
    ).tag(sync=True, init_option=True)
    projection = Unicode(
        "SIN",
        help=("The projection for the view. The keywords follow the FITS standard."),
    ).tag(sync=True, init_option=True)
    samp = Bool(False, help="Wether to allow sending data via the SAMP protocol.").tag(
        sync=True, init_option=True, only_init=True
    )
    # Buttons on/off
    background_color = Unicode(
        "rgb(60, 60, 60)", help="The color behind the surveys in RGB format."
    ).tag(sync=True, init_option=True, only_init=True)
    show_zoom_control = Bool(
        False, help="Whether to show the zoom control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    show_layers_control = Bool(
        True, help="Whether to show the layers control button."
    ).tag(sync=True, init_option=True, only_init=True)
    show_fullscreen_control = Bool(
        True, help="Whether to show the fullscreen control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    show_simbad_pointer_control = Bool(
        True, help="Whether to show the Simbad pointer control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    show_settings_control = Bool(
        True, help="Whether to show the settings control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    show_share_control = Bool(
        False, help="Whether to show the share control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    show_status_bar = Bool(True, help="Whether to show the status bar.").tag(
        sync=True, init_option=True, only_init=True
    )
    show_frame = Bool(True, help="Whether to show the viewport frame.").tag(
        sync=True, init_option=True, only_init=True
    )
    show_fov = Bool(True, help="Whether to show the field of view indicator.").tag(
        sync=True, init_option=True, only_init=True
    )
    show_coo_location = Bool(True, help="Whether to show the coordinates bar.").tag(
        sync=True, init_option=True, only_init=True
    )
    show_projection_control = Bool(
        True, help="Whether to show the coordinate location indicator."
    ).tag(sync=True, init_option=True, only_init=True)
    show_context_menu = Bool(
        True, help="Whether the right click should start the contextual menu."
    ).tag(sync=True, init_option=True, only_init=True)
    show_catalog = Bool(True, help="Whether to show the catalog.").tag(
        sync=True, init_option=True, only_init=True
    )
    full_screen = Bool(False, help="Whether to start in full-screen mode.").tag(
        sync=True, init_option=True, only_init=True
    )
    # reticle
    show_reticle = Bool(
        True, help="Whether to show the reticle in the middle of the view."
    ).tag(sync=True, init_option=True, only_init=True)
    reticle_color = Unicode("rgb(178, 50, 178)", help="The color of the reticle.").tag(
        sync=True, init_option=True, only_init=True
    )
    reticle_size = Int(20, help="Whether to show the reticle in the middle.").tag(
        sync=True, init_option=True, only_init=True
    )
    # grid
    show_coo_grid = Bool(
        False, help="Whether the coordinates grid should be shown at startup."
    ).tag(sync=True, init_option=True, only_init=True)
    show_coo_grid_control = Bool(
        True, help="Whether to show the coordinate grid control toolbar."
    ).tag(sync=True, init_option=True, only_init=True)
    grid_color = Unicode(
        "rgb(178, 50, 178)",
        help="Color of the grid. Can be specified as a named color "
        "(see html named colors), as rgb (ex: 'rgb(178, 50, 178)'), "
        "or as a hex color (ex: '#86D6AE').",
    ).tag(sync=True, init_option=True, only_init=True)
    grid_opacity = Float(
        0.5, help="Opacity of the grid and labels. It is comprised between 0 and 1."
    ).tag(sync=True, init_option=True, only_init=True)
    grid_options = traitlets.Dict(help="More options for the grid.").tag(
        sync=True, init_option=True, only_init=True
    )

    # Values
    _wcs = traitlets.Dict().tag(sync=True)
    _fov_xy = traitlets.Dict().tag(sync=True)

    # content of the last click
    clicked_object = traitlets.Dict().tag(sync=True)
    _selected_objects = traitlets.List(
        trait=traitlets.List(trait=traitlets.Any()),
        help="A list of catalogs selected by the user.",
    ).tag(sync=True)
    # listener callback is on the python side and contains functions to link to events
    listener_callback: ClassVar[Dict[str, callable]] = {}

    # overlay survey
    overlay_survey = Unicode("").tag(sync=True, init_option=True)
    overlay_survey_opacity = Float(0.0).tag(sync=True, init_option=True)
    _base_layer_last_view = Unicode(
        survey.default_value,
        help="A private trait for the base layer of the last view. It is useful "
        "to convert the view to an astropy.HDUList",
    ).tag(sync=True)

    init_options = traitlets.List(trait=Any()).tag(sync=True)

    @default("init_options")
    def _init_options(self) -> List[str]:
        return list(self.traits(init_option=True))

    def __init__(self, *args: any, **kwargs: any) -> None:
        super().__init__(*args, **kwargs)
        self.height = kwargs.get("height", 400)
        self.target = kwargs.get("target", "0 0")
        self.fov = kwargs.get("fov", 60.0)
        self.on_msg(self._handle_custom_message)

    def _handle_custom_message(self, _: any, message: dict, buffers: any) -> None:
        event_type = message["event_type"]
        if (
            event_type == "object_clicked"
            and "object_clicked" in self.listener_callback
        ):
            self.listener_callback["object_clicked"](message["content"])
        elif (
            event_type == "object_hovered"
            and "object_hovered" in self.listener_callback
        ):
            self.listener_callback["object_hovered"](message["content"])
        elif event_type == "click" and "click" in self.listener_callback:
            self.listener_callback["click"](message["content"])
        elif event_type == "select" and "select" in self.listener_callback:
            self.listener_callback["select"](message["content"])
        elif event_type == "save_view_as_image":
            self._save_file(message["path"], buffers[0])

    @property
    def selected_objects(self) -> List[Table]:
        """The list of catalogs selected by the user.

        Returns
        -------
        list[Table]
            A list of astropy.table.Table objects representing the selected catalogs.

        """
        catalogs = []
        for selected_object in self._selected_objects:
            objects_data = [obj["data"] for obj in selected_object]
            catalogs.append(Table(objects_data))
        return catalogs

    @property
    def height(self) -> int:
        """The height of the Aladin Lite widget.

        Returns
        -------
        int
            The height of the widget in pixels.

        """
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        if np.isclose(self._height, height):
            return
        self._wcs = {}
        self._fov_xy = {}
        self._height = height

    @property
    def wcs(self) -> WCS:
        """The world coordinate system of the Aladin Lite widget.

        Returns
        -------
        WCS
            An astropy WCS object representing the world coordinate system.

        """
        if self._wcs == {}:
            raise WidgetCommunicationError(
                "The world coordinate system is not available. This often happens when "
                "the WCS is modified and read in the same cell. "
                "Please recover it from another cell."
            )
        if "RADECSYS" in self._wcs:  # RADECSYS keyword is deprecated for astropy.WCS
            self._wcs["RADESYS"] = self._wcs.pop("RADECSYS")
        return WCS(self._wcs)

    @property
    def fov_xy(self) -> Tuple[Angle, Angle]:
        """The field of view of the Aladin Lite along the two axes.

        Returns
        -------
        tuple[Angle, Angle]
            A tuple of astropy.units.Angle objects representing the field of view.

        """
        if self._fov_xy == {}:
            raise WidgetCommunicationError(
                "The field of view along the two axes is not available. This often "
                "happens when the FOV is modified and read in the same cell. "
                "Please recover it from another cell."
            )
        return (
            Angle(self._fov_xy["x"], unit="deg"),
            Angle(self._fov_xy["y"], unit="deg"),
        )

    @property
    def fov(self) -> Angle:
        """The field of view of the Aladin Lite widget along the horizontal axis.

        It can be set with either a float number in degrees
        or an astropy.coordinates.Angle object.

        Returns
        -------
        astropy.coordinates.Angle
            An astropy.coordinates.Angle object representing the field of view.

        See Also
        --------
        fov_xy

        """
        return Angle(self._fov, unit="deg")

    @fov.setter
    def fov(self, fov: Union[float, Angle]) -> None:
        if isinstance(fov, Angle):
            fov = fov.deg
        if np.isclose(fov, self._fov):
            return
        self._fov = fov
        self.send({"event_name": "change_fov", "fov": fov})
        self._fov_xy = {}
        self._wcs = {}

    @property
    def target(self) -> SkyCoord:
        """The target of the Aladin Lite widget.

        It can be set with either a string or an `astropy.coordinates.SkyCoord` object.

        Returns
        -------
        astropy.coordinates.SkyCoord
            An `astropy.coordinates.SkyCoord` object representing the target.

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
        self._wcs = {}
        self.send(
            {
                "event_name": "goto_ra_dec",
                "ra": target.icrs.ra.deg,
                "dec": target.icrs.dec.deg,
            }
        )

    def _save_file(self, path: str, buffer: bytes) -> None:
        """Save a file from a buffer.

        Parameters
        ----------
        path : str
            The path where the file will be saved.
        buffer : bytes
            The buffer containing the file.

        """
        with Path(path).open("wb") as file:
            file.write(buffer)

    def save_view_as_image(
        self, path: Union[str, Path], image_format: str = "png", with_logo: bool = True
    ) -> None:
        """Save the current view of the widget as an image file.

        Parameters
        ----------
        path : Union[str, Path]
            The path where the image will be saved.
        image_format : str
            The format of the image. Can be 'png', 'jpeg' or 'webp'.
        with_logo : bool
            Whether to include the Aladin Lite logo in the image.

        See Also
        --------
        get_view_as_fits

        """
        if image_format not in {"png", "jpeg", "webp"}:
            raise ValueError("image_format must be 'png', 'jpeg' or 'webp")
        self.send(
            {
                "event_name": "save_view_as_image",
                "path": str(path),
                "format": image_format,
                "with_logo": with_logo,
            }
        )

    def get_view_as_fits(self) -> HDUList:
        """Get the base layer of the widget as an astropy HDUList object.

        The output FITS image will have the same shape as the
        current view of the widget. This uses `astroquery.hips2fits` internally.
        This method currently only exports the bottom/base layer.

        Returns
        -------
        astropy.io.fits.HDUList
            The FITS object containing the image.

        See Also
        --------
        save_view_as_image

        """
        try:
            from astroquery.hips2fits import hips2fits
        except ImportError as imp:
            raise ValueError(
                "To use the 'get_view_as_fits' method, you need to install astroquery "
                "with 'pip install astroquery -U --pre'."
            ) from imp
        try:
            fits = hips2fits.query_with_wcs(
                hips=self._base_layer_last_view,
                wcs=self.wcs,
            )
        except JSONDecodeError as e:
            raise ValueError(
                "The FITS image could not be retrieved from the view. "
                "This can happen when the widget is scrolled out of the "
                "screen."
            ) from e
        return fits

    def get_JPEG_thumbnail(self) -> None:
        """Create a new tab with the current Aladin view.

        This method will only work if you are running a notebook in a browser (for
        example, it won't do anything in VSCode).

        See Also
        --------
        save_view_as_image: will save the image on disk instead

        """
        self.send({"event_name": "get_JPG_thumbnail"})

    def add_catalog_from_URL(
        self, votable_URL: str, votable_options: Optional[dict] = None
    ) -> None:
        """Load a VOTable table from an url and load its data into the widget.

        Parameters
        ----------
        votable_URL : str
        votable_options : dict

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

    def add_fits(self, fits: Union[str, Path, HDUList], **image_options: any) -> None:
        """Load a FITS file into the widget.

        Parameters
        ----------
        fits : Union[str, Path, HDUList]
            The FITS image to load in the widget. It can be given as a path (either a
            string or a `pathlib.Path` object), or as an `astropy.io.fits.HDUList`.
        image_options : any
            The options for the image. See the `Aladin Lite image options
            <https://cds-astro.github.io/aladin-lite/global.html#ImageOptions>`_

        """
        is_path = isinstance(fits, (Path, str))
        if is_path:
            with astropy_fits.open(fits) as fits_file:
                fits_bytes = io.BytesIO()
                fits_file.writeto(fits_bytes)
        else:
            fits_bytes = io.BytesIO()
            fits.writeto(fits_bytes)

        self._wcs = {}
        self.send(
            {"event_name": "add_fits", "options": image_options},
            buffers=[fits_bytes.getvalue()],
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
        moc_options :
            Keyword arguments. The possible values are documented in `Aladin Lite's MOC
            options <https://cds-astro.github.io/aladin-lite/global.html#MOCOptions>`_

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
        moc_options :
            Keyword arguments. The possible values are documented in `Aladin Lite's MOC
            options <https://cds-astro.github.io/aladin-lite/global.html#MOCOptions>`_

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
        moc_options :
            Keyword arguments. The possible values are documented in `Aladin Lite's MOC
            options <https://cds-astro.github.io/aladin-lite/global.html#MOCOptions>`_

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

    def _convert_table_units(
        self, table: Union[QTable, Table], error_dict: Dict, unit_to: u.Unit = u.deg
    ) -> Union[QTable, Table]:
        """Convert the units of a table according to the error_dict.

        Parameters
        ----------
        table : astropy.table.table.QTable or astropy.table.table.Table
            The table to convert.
        error_dict : dict
            The dictionary containing the error specifications.
        unit_to : astropy.units.Unit
            The unit to convert to. Default is degrees.

        Returns
        -------
        astropy.table.table.QTable or astropy.table.table.Table
            The table with the units converted.

        """
        table = table.copy()
        for error_spec in error_dict.values():
            if not isinstance(error_spec, dict):
                continue
            col_name = error_spec["col"]
            unit_from = error_spec["unit"]
            table[col_name].unit = unit_from
            table[col_name] = table[col_name].astype(float)
            for row in table:
                if row[col_name] != "--" and not np.isnan(row[col_name]):
                    row[col_name] = (
                        Angle(row[col_name], unit=unit_from).to(unit_to).value
                    )
            table[col_name].unit = unit_to

        return table

    def _update_ellipse_enclosed_probability(
        self, table: Union[QTable, Table], error_dict: Dict
    ) -> Union[QTable, Table]:
        """Update the table according to the ellipse_enclosed_probability.

        Parameters
        ----------
        table : astropy.table.table.QTable or astropy.table.table.Table
            The table to update.
        error_dict : dict
            The dictionary containing the error specifications.

        Returns
        -------
        astropy.table.table.QTable or astropy.table.table.Table
            The updated table.

        """
        table = table.copy()
        r = math.sqrt(-2 * math.log(1 - error_dict["ellipse_enclosed_probability"]))
        impacted_keys = {"smin", "smaj", "r"}
        for key in impacted_keys:
            if not error_dict.get(key):
                continue
            # Multiply table column by r
            table[error_dict[key]["col"]] = table[error_dict[key]["col"]] * r

        return table

    def add_table(self, table: Union[QTable, Table], **table_options: any) -> None:
        """Load a table into the widget.

        Parameters
        ----------
        table : astropy.table.table.QTable or astropy.table.table.Table
            table that must contain coordinates information
        table_options
            Keyword arguments. The possible values are documented in `Aladin Lite's
            table options
            <https://cds-astro.github.io/aladin-lite/global.html#CatalogOptions>`_

        """
        if table_options.get("error_dict"):
            table_options["error_dict"] = deepcopy(table_options["error_dict"])
            table = self._convert_table_units(table, table_options["error_dict"])
            # if dict contains ellipse_enclosed_probability, update the table
            if table_options["error_dict"].get("ellipse_enclosed_probability"):
                table = self._update_ellipse_enclosed_probability(
                    table, table_options["error_dict"]
                )
            # Remove unit sub-key for all the keys
            for key in table_options["error_dict"]:
                if key == "ellipse_enclosed_probability":
                    continue
                table_options["error_dict"][key].pop("unit")
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
            `regions package <https://astropy-regions.readthedocs.io>`_.
        graphic_options: keyword arguments
            The options for the graphic overlay. Use Region visual for region options.
            See `Aladin Lite's graphic overlay options
            <https://cds-astro.github.io/aladin-lite/A.html>`_

        See Also
        --------
        add_graphic_overlay_from_stcs: for shapes described as STC-S strings.

        Notes
        -----
        The possible `~regions.RegionVisual` options correspond to the
        Aladin Lite / ipyaladin parameters:

        .. table:: Correspondence between options
            :widths: auto

            ============== ===================== ======================
            RegionVisual        AladinLite              ipyaladin
            ============== ===================== ======================
            edgecolor      color                 color
            facecolor      fillColor             fill_color
            color          color and fillColor   color and fill_color
            alpha          opacity               opacity
            linewidth      lineWidth             line_width
            ============== ===================== ======================

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

            from .utils._region_converter import RegionInfos

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
        self, stc_string: Union[List[str], str], **overlay_options: any
    ) -> None:
        """Add an overlay layer defined by an STC-S string.

        Parameters
        ----------
        stc_string : str, list[str]
            The STC-S string or a list of STC-S strings.
        overlay_options : keyword arguments
            The overlay options for all the STC-S strings
            See `Aladin Lite's graphic overlay options
            <https://cds-astro.github.io/aladin-lite/A.html>`_

        """
        warnings.warn(
            "'add_overlay_from_stcs' is deprecated, "
            "use 'add_graphic_overlay_from_stcs' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_graphic_overlay_from_stcs(stc_string, **overlay_options)

    def add_graphic_overlay_from_stcs(
        self, stc_string: Union[List[str], str], **overlay_options: any
    ) -> None:
        """Add an overlay layer defined by an STC-S string.

        Parameters
        ----------
        stc_string : str, list[str]
            The STC-S string or a list of STC-S strings.
        overlay_options : keyword arguments
            The overlay options for all the STC-S strings.
            See `Aladin Lite's graphic overlay options
            <https://cds-astro.github.io/aladin-lite/A.html>`_

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

    def set_color_map(self, color_map_name: str) -> None:
        """Change the color map of the Aladin Lite widget.

        Parameters
        ----------
        color_map_name: str
            The name of the color map to use.

        """
        self.send({"event_name": "change_colormap", "colormap": color_map_name})

    def selection(self, selection_type: str = "rectangle") -> None:
        """Trigger the selection tool.

        Parameters
        ----------
        selection_type: str
            The type of selection tool to trigger. Can be 'circle' or 'rectangle'.
            Default is 'rect'.

        """
        # Note: Polygon selection exists but is not supported by Aladin Lite
        if selection_type not in {"circle", "rectangle"}:
            raise ValueError("selection_type must be 'circle' or 'rectangle'")
        self.send({"event_name": "trigger_selection", "selection_type": selection_type})

    def rectangular_selection(self) -> None:
        """Trigger the rectangular selection tool.

        Notes
        -----
        This method is deprecated, use selection instead
        """
        warnings.warn(
            "rectangular_selection is deprecated, use selection('rectangle') instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.selection()

    # Adding a listener

    def set_listener(self, listener_type: str, callback: Callable) -> None:
        """Set a listener for an event to the widget.

        Parameters
        ----------
        listener_type : str
            Can either be 'object_hovered', 'object_clicked', 'click' or 'select'
        callback : Callable
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

    def add_listener(self, listener_type: str, callback: Callable) -> None:
        """Add a listener to the widget. Use set_listener instead.

        Parameters
        ----------
        listener_type: str
            Can either be 'object_hovered', 'object_clicked', 'click' or 'select'
        callback: Callable
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
