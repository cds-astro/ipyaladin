"""
Aladin Lite widget for Jupyter Notebook.

This module provides a Python wrapper around the Aladin Lite JavaScript library.
It allows to display astronomical images and catalogs in an interactive way.
"""

from collections.abc import Callable
import functools
from json import JSONDecodeError
import io
import pathlib
from pathlib import Path
import time
from typing import ClassVar, Dict, Final, List, Optional, Tuple, Union
import warnings

import anywidget
from astropy.coordinates import SkyCoord, Angle, Longitude, Latitude
from astropy.coordinates.name_resolve import NameResolveError
from astropy.table.table import QTable
from astropy.table import Table
from astropy.io import fits as astropy_fits
from astropy.io.fits import HDUList
from astropy.wcs import WCS
import numpy as np
import traitlets

from .utils.exceptions import WidgetReducedError, WidgetNotReadyError
from .utils._coordinate_parser import _parse_coordinate_string
from .elements.marker import Marker

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


def widget_should_be_loaded(function: Callable) -> Callable:
    """Check if the widget is ready to execute a function.

    Parameters
    ----------
    function : Callable
        The function to decorate.

    Returns
    -------
    Callable
        The decorated function.

    """

    @functools.wraps(function)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        """Check if the widget is ready to execute a function.

        Parameters
        ----------
        self : any
            The widget object.
        *args : any
            The arguments of the function.
        **kwargs : any
            The keyword arguments of the function.

        Returns
        -------
        any
            The result of the function if the widget is ready.

        """
        if not getattr(self, "_is_loaded", False):
            # this is an arbitrary waiting time
            # it should correspond to the downloading time of the npm package
            duration = 0.1
            time.sleep(duration)
            # set ready to True to avoid waiting twice
            self._is_loaded = True
        return function(self, *args, **kwargs)

    return wrapper


class Aladin(anywidget.AnyWidget):
    """Aladin Lite widget.

    This widget is a Python wrapper around the Aladin Lite JavaScript library.
    It allows to display astronomical images and catalogs in an interactive way.
    """

    _esm: Final = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css: Final = pathlib.Path(__file__).parent / "static" / "widget.css"

    # Options for the view initialization
    _init_options = traitlets.Dict().tag(sync=True)
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
        help="The frame coordinate. Can be either 'ICRS', 'ICRSd', or 'galactic'.",
    ).tag(sync=True, init_option=True)
    projection = Unicode(
        "SIN",
        help="The projection for the view. The keywords follow the FITS standard.",
    ).tag(sync=True, init_option=True)
    # Values
    _ready = Bool(
        False,
        help="A private trait that stores the readiness of the widget.",
    ).tag(sync=True)
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
    _survey_body = Unicode(
        "sky",
        help="The body name of the base layer survey, 'sky' for the sky survey",
    ).tag(sync=True, init_option=True)
    overlay_survey = Unicode("").tag(sync=True, init_option=True)
    overlay_survey_opacity = Float(0.0).tag(sync=True, init_option=True)
    _base_layer_last_view = Unicode(
        survey.default_value,
        help="A private trait for the base layer of the last view. It is useful "
        "to convert the view to an astropy.HDUList",
    ).tag(sync=True)

    _is_loaded = Bool(
        False,
        help="A private trait that stores whether the widget is loaded.",
    ).tag(
        sync=True,
    )

    # Temporary traitlet for widget size problem
    _is_reduced = Bool(
        False,
        help="A private trait that stores if the widget "
        "is reduced in size when hidden.",
    ).tag(sync=True)

    def __init__(self, *args: any, **init_options: any) -> None:
        super().__init__(*args, **init_options)
        # pop init options of ipywidgets.DOMWidget that would choke ipyaladin
        # https://github.com/jupyter-widgets/ipywidgets/blob/main/python/ipywidgets/ipywidgets/widgets/domwidget.py
        for key in ["layout", "tabbable", "tooltip"]:
            init_options.pop(key, None)
        # some init options are properties here
        self.height = init_options.get("height", self._height)
        self.target = init_options.get("target", self._target)
        self.fov = init_options.get("fov", self._fov)
        # apply different default options from Aladin-Lite
        ipyaladin_default = {
            "show_simbad_pointer_control": True,
            "show_coo_grid_control": True,
            "show_settings_control": True,
            "show_context_menu": True,
        }
        init_options = {**ipyaladin_default, **init_options}
        # set the traitlet
        self._init_options = init_options
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
        """The height of the widget.

        Returns
        -------
        int
            The height of the widget in pixels.
            Setting the height to -1 will expand the widget at 100% height of its
            container. This is generally a bad idea in a notebook but can be usefull
            for dashbord applications.
            The default height is 400 pixels.
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
        """The world coordinate system corresponding to the current view of ipyaladin.

        Returns
        -------
        `~astropy.wcs.WCS`
            An astropy WCS object representing the world coordinate system.

        """
        if self._is_reduced:
            # this is the bug that https://github.com/jupyterlab/jupyterlab/issues/16630
            # will solve.
            raise WidgetReducedError(
                "Jupyter reduces the size of the widget when it is out of the view. "
                "This leads to wrong WCS. Either scroll up to the widget, and query "
                "the WCS from there, or use the right click menu 'Create New View for "
                "Cell Output' to keep the widget in the screen."
            )
        if self._wcs == {}:
            raise WidgetNotReadyError(
                "The WCS is not available. There are two reasons for that: either the "
                "widget was not ready, in this case, try running the cell again. Or "
                "the state of the widget was changed in the same cell than the "
                "calculation of the WCS. In this second case, please move the "
                "manipulations of the widget in an other cell (this can be changes of "
                "target, projection, or fov)."
            )
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
            raise WidgetNotReadyError(
                "The field of view along the two axes is not available. This often "
                "happens when the FoV is modified and read in the same cell. "
                "Please read it from a new cell."
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
    def target(self) -> Union[SkyCoord, Tuple[float, float]]:
        """The target of the Aladin Lite widget.

        The target can be provided as coordinates (either
        `~astropy.coordinates.SkyCoord` or (`~astropy.coordinates.Longitude`,
        `~astropy.coordinates.Latitude`)) or as a name (as a string).

        The conversion from a name to coordinates does call different online services
        depending on the base layer of the widget:
        - for the sky: it uses CDS's
        `Sesame <https://vizier.cds.unistra.fr/viz-bin/Sesame>`_  name resolver. This
        looks first in SIMBAD, then in VizieR, and then in NED for the object's
        coordinates.
        - for Earth: it uses `Nominatim
        <https://nominatim.openstreetmap.org/ui/search.html>`_, OpenStreetMap's
        search bar
        - for other solar system bodies: it calls the `Gazetteer of Planetary
        Nomenclature <https://planetarynames.wr.usgs.gov/Nomenclature>`_

        Returns
        -------
        `~astropy.coordinates.SkyCoord` or Tuple[Longitude, Latitude]
            If ipyaladin has a sky survey, returns a `~astropy.coordinates.SkyCoord`
            object. Otherwise, if ipyaladin is currently on a planetary body, returns
            a tuple with the Longitude and the Latitude of the current position of the
            widget.

        """
        lon, lat = self._target.split(" ")
        lon, lat = float(lon), float(lat)
        if self._survey_body == "sky":
            return SkyCoord(
                ra=lon,
                dec=lat,
                frame="icrs",
                unit="deg",
            )
        return Longitude(lon, unit="deg"), Latitude(lat, unit="deg")

    @target.setter
    def target(self, target: Union[str, SkyCoord, Tuple[float, float]]) -> None:
        if isinstance(target, Tuple):
            lon, lat = target[0].deg, target[1].deg
        elif isinstance(target, str):  # If the target is a string, parse it
            try:
                lon, lat = _parse_coordinate_string(target, self._survey_body)
            except NameResolveError as e:
                # If the widget is not ready, we don't know if the base survey is
                # celestial or planetary so the error can be caused by two factors
                if not self._ready:
                    raise WidgetNotReadyError(
                        f"Either '{target}' is not a valid celestial object name, "
                        f"or the survey body type is not yet defined so you "
                        f"need to wait for the widget to be fully loaded."
                    ) from e
                # If the widget is ready, the error is caused by the target name
                # that is not a valid celestial object name
                raise e
        elif not isinstance(target, SkyCoord) and not isinstance(target, Tuple):
            raise ValueError(
                "target must be a string, an astropy.coordinates.SkyCoord "
                "object or a tuple of two angle-like astropy quantities."
            )
        self._wcs = {}
        if isinstance(target, SkyCoord):
            lon, lat = target.icrs.ra.deg, target.icrs.dec.deg

        self._target = f"{lon} {lat}"
        self.send(
            {
                "event_name": "goto_ra_dec",
                "ra": lon,
                "dec": lat,
            }
        )

    def add_markers(
        self, markers: Union[Marker, List[Marker]], **catalog_options: any
    ) -> None:
        """Add markers to the Aladin Lite widget.

        Markers have a popup window that appear when they're clicked on.

        Parameters
        ----------
        markers : Marker or list[Marker]
            The marker(s) to add to the widget. It can be given as a single `Marker`
            object or as a list of `Marker` objects.
        catalog_options : any
            The options for the catalog. See the `Aladin Lite catalog options
            <https://cds-astro.github.io/aladin-lite/global.html#CatalogOptions>`_

        See Also
        --------
        add_table: also adds points, but without popup window.
        """
        if not isinstance(markers, list):
            markers = [markers]
        self.send(
            {
                "event_name": "add_marker",
                "markers": [marker.__dict__ for marker in markers],
                "options": catalog_options,
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

    @widget_should_be_loaded
    def save_view_as_image(
        self, path: Union[str, Path], image_format: str = "png", with_logo: bool = True
    ) -> None:
        """Save the current view of the widget as an image file.

        This should be used as quick previews, or illustrations. For scientific-quality
        pixels, use 'get_view_as_fits'.

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
        get_view_as_fits: conserves the photometry

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

    @widget_should_be_loaded
    def get_view_as_fits(self) -> HDUList:
        """Get the base layer of the widget as an astropy HDUList object.

        The output FITS image will have the same shape as the
        current view of the widget. This uses `astroquery.hips2fits` internally.
        This method currently only exports the bottom/base layer.

        Returns
        -------
        `~astropy.io.fits.HDUList`
            The FITS object containing the image.

        See Also
        --------
        save_view_as_image

        """
        try:
            from astroquery.hips2fits import hips2fits
        except ImportError as imp:
            raise ValueError(
                "To use 'get_view_as_fits', you need astroquery. "
                "Install it with 'pip install astroquery -U --pre'."
            ) from imp
        try:
            fits = hips2fits.query_with_wcs(
                hips=self._base_layer_last_view,
                wcs=self.wcs,
            )
        # there is a JSONDecodeError when NAXIS=[1,1]. This happens when the widget is
        # reduced. See more explanation in the wcs property.
        except JSONDecodeError as e:
            raise ValueError(
                "The FITS image could not be retrieved from the view. "
                "This happens when the widget is scrolled out of the "
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

    @widget_should_be_loaded
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

    @widget_should_be_loaded
    def add_fits(self, fits: Union[str, Path, HDUList], **image_options: any) -> None:
        """Load a FITS image into the widget.

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

    @widget_should_be_loaded
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
                    "A MOC can be given as an URL, a dictionary, or a mocpy.MOC "
                    "object. To read mocpy.MOC objects, you need to install the mocpy "
                    "library with 'pip install mocpy'."
                ) from imp

    @widget_should_be_loaded
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
            "that the MOC was given as an URL."
            "This will be removed in version 1.0.0 (coming after 0.5).",
            DeprecationWarning,
            stacklevel=2,
        )
        if moc_options is None:
            moc_options = {}
        self.add_moc(moc_URL, **moc_options)

    @widget_should_be_loaded
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
            "that the MOC was given as a dictionary."
            "This will be removed in version 1.0.0 (coming after 0.5).",
            DeprecationWarning,
            stacklevel=2,
        )
        if moc_options is None:
            moc_options = {}
        self.add_moc(moc_dict, **moc_options)

    @widget_should_be_loaded
    def add_table(self, table: Union[QTable, Table], **table_options: any) -> None:
        """Load a table into the widget.

        Parameters
        ----------
        table : `~astropy.table.table.QTable` or `~astropy.table.table.Table`
            table that must contain coordinates information
        table_options
            Keyword arguments. The possible values are documented in `Aladin Lite's
            table options
            <https://cds-astro.github.io/aladin-lite/global.html#CatalogOptions>`_

        See Also
        --------
        add_markers: adds markers with a popup window when clicked

        """
        table_bytes = io.BytesIO()
        table.write(table_bytes, format="votable")
        self.send(
            {"event_name": "add_table", "options": table_options},
            buffers=[table_bytes.getvalue()],
        )

    @widget_should_be_loaded
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

    @widget_should_be_loaded
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
            "use 'add_graphic_overlay_from_stcs' instead. "
            "This will be removed in version 1.0.0 (coming after 0.5).",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_graphic_overlay_from_stcs(stc_string, **overlay_options)

    @widget_should_be_loaded
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

    @widget_should_be_loaded
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
            "rectangular_selection is deprecated, use selection('rectangle') instead"
            "This will be removed in version 1.0.0 (coming after 0.5).",
            DeprecationWarning,
            stacklevel=2,
        )
        self.selection()

    # Adding a listener

    @widget_should_be_loaded
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

    @widget_should_be_loaded
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
            "add_listener is deprecated, use set_listener instead"
            "This will be removed in version 1.0.0 (coming after 0.5).",
            DeprecationWarning,
            stacklevel=2,
        )
        self.set_listener(listener_type, callback)
