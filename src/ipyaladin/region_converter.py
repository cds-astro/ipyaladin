import numpy as np

from astropy.coordinates import SkyCoord, CartesianRepresentation, Angle
from astropy.coordinates.matrix_utilities import rotation_matrix
from astropy.units import Quantity

try:
    from regions import (
        RectangleSkyRegion,
        PolygonSkyRegion,
        Region,
        CircleSkyRegion,
        EllipseSkyRegion,
        LineSkyRegion,
    )
except ImportError:
    RectangleSkyRegion = None
    PolygonSkyRegion = None
    Region = None
    CircleSkyRegion = None
    EllipseSkyRegion = None
    LineSkyRegion = None
from typing import Union


def rectangle_to_polygon_region(region: RectangleSkyRegion) -> PolygonSkyRegion:
    """Convert a RectangleSkyRegion to a PolygonSkyRegion.

    Parameters
    ----------
    region : RectangleSkyRegion
        The region to convert.

    Returns
    -------
    PolygonSkyRegion
        The converted region.

    """
    bottom_left = (
        region.center.spherical_offsets_by(-region.width / 2, -region.height / 2)
        .represent_as("cartesian")
        .xyz
    )
    bottom_right = (
        region.center.spherical_offsets_by(-region.width / 2, region.height / 2)
        .represent_as("cartesian")
        .xyz
    )
    top_right = (
        region.center.spherical_offsets_by(region.width / 2, region.height / 2)
        .represent_as("cartesian")
        .xyz
    )
    top_left = (
        region.center.spherical_offsets_by(region.width / 2, -region.height / 2)
        .represent_as("cartesian")
        .xyz
    )
    center = region.center.represent_as("cartesian").xyz

    angle = region.angle
    if isinstance(region.angle, Quantity):
        angle = Angle(region.angle)
    rot_mat = rotation_matrix(Angle(-angle.deg, unit="deg"), center)

    corners = np.array(
        [
            bottom_left,
            bottom_right,
            top_right,
            top_left,
        ]
    )
    rotated_corners = np.dot(corners, rot_mat)
    vertices = [
        SkyCoord(CartesianRepresentation(*corner), frame="icrs")
        for corner in rotated_corners
    ]

    return PolygonSkyRegion(
        vertices=SkyCoord(
            [coord.icrs.ra.deg for coord in vertices],
            [coord.icrs.dec.deg for coord in vertices],
            unit="deg",
        ),
        visual=region.visual,
        meta=region.meta,
    )


class RegionInfos:
    """Extract information from a region.

    Attributes
    ----------
    region_type : str
        The type of the region.
    infos : dict
        The information extracted from the region.

    """

    def __init__(self, region: Union[str, Region]) -> None:
        self._region_parsers = {
            "str": self._from_stcs,
            "CircleSkyRegion": self._from_circle_sky_region,
            "EllipseSkyRegion": self._from_ellipse_sky_region,
            "LineSkyRegion": self._from_line_sky_region,
            "PolygonSkyRegion": self._from_polygon_sky_region,
            "RectangleSkyRegion": self._from_rectangle_sky_region,
        }
        self.options = {}
        self.from_region(region)

    def from_region(self, region: Union[str, Region]) -> None:
        """Parse a region to extract its information.

        Parameters
        ----------
        region : Union[str, Region]
            The region to parse.

        """
        if type(region).__name__ not in self._region_parsers:
            raise ValueError(f"Unsupported region type: {type(region).__name__}")
        region_parser = self._region_parsers[type(region).__name__]
        region_parser(region)
        if not isinstance(region, str):
            self._parse_visuals(region)

    def _from_stcs(self, stcs: str) -> None:
        self.region_type = "stcs"
        self.infos = {"stcs": stcs}

    def _from_circle_sky_region(self, region: CircleSkyRegion) -> None:
        self.region_type = "circle"
        radius = region.radius
        if isinstance(region.radius, Quantity):
            radius = Angle(region.radius)
        self.infos = {
            "ra": region.center.ra.deg,
            "dec": region.center.dec.deg,
            "radius": radius.deg,
        }

    def _from_ellipse_sky_region(self, region: EllipseSkyRegion) -> None:
        self.region_type = "ellipse"
        angle = region.angle
        if isinstance(region.angle, Quantity):
            angle = Angle(region.angle)
        angle = Angle(angle.deg - 90, unit="deg")
        a = region.width
        if isinstance(region.width, Quantity):
            a = Angle(region.width)
        b = region.height
        if isinstance(region.height, Quantity):
            b = Angle(region.height)
        self.infos = {
            "ra": region.center.ra.deg,
            "dec": region.center.dec.deg,
            "a": a.deg / 2,
            "b": b.deg / 2,
            "theta": angle.deg,
        }

    def _from_line_sky_region(self, region: LineSkyRegion) -> None:
        self.region_type = "line"
        self.infos = {
            "ra1": region.start.ra.deg,
            "dec1": region.start.dec.deg,
            "ra2": region.end.ra.deg,
            "dec2": region.end.dec.deg,
        }

    def _from_polygon_sky_region(self, region: PolygonSkyRegion) -> None:
        self.region_type = "polygon"
        vertices = [[coord.ra.deg, coord.dec.deg] for coord in region.vertices]
        self.infos = {"vertices": vertices}

    def _from_rectangle_sky_region(self, region: RectangleSkyRegion) -> None:
        # Rectangle is interpreted as a polygon in Aladin Lite
        self._from_polygon_sky_region(rectangle_to_polygon_region(region))

    def _parse_visuals(self, region: Region) -> None:
        visual = dict(region.visual)
        # Color parsing
        if "facecolor" in visual:
            visual["fill_color"] = visual.pop("facecolor")
        if "edgecolor" in visual:
            visual["color"] = visual.pop("edgecolor")
        if "color" in visual:
            visual["fill_color"] = visual["color"]

        # Other parsing
        if "alpha" in visual:
            visual["opacity"] = visual.pop("alpha")
        if "linewidth" in visual:
            visual["line_width"] = visual.pop("linewidth")
        self.options = visual

    def to_clean_dict(self) -> dict:
        """Return a clean dictionary representation of the region.

        Returns
        -------
        dict
            The dictionary representation of the region.

        """
        return {
            "region_type": self.region_type,
            "infos": self.infos,
            "options": self.options,
        }
