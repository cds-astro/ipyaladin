import math
from regions import (
    RectangleSkyRegion,
    PolygonSkyRegion,
    Region,
    CircleSkyRegion,
    EllipseSkyRegion,
    LineSkyRegion,
    CirclePixelRegion,
    EllipsePixelRegion,
    LinePixelRegion,
    PolygonPixelRegion,
    RectanglePixelRegion,
    PixCoord,
)
from astropy.coordinates import SkyCoord
from typing import Union

TWICE_PI = 2 * math.pi


class RefToLocalRotMatrix:
    """A rotation matrix from the reference frame to the local frame.

    The reference frame is the ICRS frame. The local frame is
    defined by the center of the local reference frame.

    Attributes
    ----------
    r11-r33 : float
        The elements of the rotation matrix.

    """

    def __init__(
        self,
        r11: float,
        r12: float,
        r13: float,
        r21: float,
        r22: float,
        r23: float,
        r31: float,
        r32: float,
        r33: float,
    ) -> None:
        self.r11 = r11
        self.r12 = r12
        self.r13 = r13
        self.r21 = r21
        self.r22 = r22
        self.r23 = r23
        self.r31 = r31
        self.r32 = r32
        self.r33 = r33

    @classmethod
    def from_center(cls: any, lon: float, lat: float) -> "RefToLocalRotMatrix":
        """Create a rotation matrix from the center of the local reference frame.

        Parameters
        ----------
        lon : float
            The longitude of the center.
        lat : float
            The latitude of the center.

        Returns
        -------
        RefToLocalRotMatrix
            The rotation matrix.

        """
        ca, sa = math.cos(lon), math.sin(lon)
        cd, sd = math.cos(lat), math.sin(lat)
        return cls(ca * cd, sa * cd, sd, -sa, ca, 0.0, -ca * sd, -sa * sd, cd)

    def to_global_xyz(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        """Convert local cartesian coordinates to global cartesian coordinates.

        Parameters
        ----------
        x : float
            The x coordinate.
        y : float
            The y coordinate.
        z : float
            The z coordinate.

        Returns
        -------
        tuple[float, float, float]
            The x, y, and z coordinates.

        """
        return (
            self.r11 * x + self.r21 * y + self.r31 * z,
            self.r12 * x + self.r22 * y + self.r32 * z,
            self.r13 * x + self.r23 * y + self.r33 * z,
        )

    def to_global_coo(self, x: float, y: float, z: float) -> tuple[float, float]:
        """Convert local cartesian coordinates to global spherical coordinates.

        Parameters
        ----------
        x : float
            The x coordinate.
        y : float
            The y coordinate.
        z : float
            The z coordinate.

        Returns
        -------
        tuple[float, float]
            The longitude and latitude.

        """
        x, y, z = self.to_global_xyz(x, y, z)
        # Convert cartesian coordinates to spherical coordinates.
        r2 = x * x + y * y
        lat = math.atan2(z, math.sqrt(r2))
        lon = math.atan2(y, x)
        if lon < 0:
            lon += TWICE_PI
        return lon, lat


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
    longitude, latitude = region.center.icrs.ra.rad, region.center.icrs.dec.rad
    width = region.width.rad
    height = region.height.rad
    position_angle = region.angle.rad

    assert (
        0.0 <= longitude < TWICE_PI
    ), f"Expected: lon in [0, 2pi[. Actual: {longitude}"
    assert (
        -math.pi / 2 <= latitude <= math.pi / 2
    ), f"Expected: lat in [-pi/2, pi/2]. Actual: {latitude}"
    assert 0.0 < width <= math.pi / 2, f"Expected: a in ]0, pi/2]. Actual: {width}"
    assert 0.0 < height <= width, f"Expected: b in ]0, a]. Actual: {height}"
    assert (
        0.0 <= position_angle < math.pi
    ), f"Expected: pa in [0, pi[. Actual: {position_angle}"

    frame_rotation = RefToLocalRotMatrix.from_center(longitude, latitude)

    sin_lon, cos_lon = math.sin(width), math.cos(width)
    latitude = math.atan(cos_lon * math.tan(height))
    sin_lat, cos_lat = math.sin(latitude), math.cos(latitude)
    sin_pa, cos_pa = math.sin(position_angle), math.cos(position_angle)

    x1, y1, z1 = cos_lon * cos_lat, sin_lon * cos_lat, sin_lat

    y2 = y1 * sin_pa - z1 * cos_pa
    z2 = y1 * cos_pa + z1 * sin_pa
    vertices = [frame_rotation.to_global_coo(x1, y2, z2)]

    y2 = y1 * sin_pa + z1 * cos_pa
    z2 = y1 * cos_pa - z1 * sin_pa
    vertices.append(frame_rotation.to_global_coo(x1, y2, z2))

    y2 = -y1 * sin_pa + z1 * cos_pa
    z2 = -y1 * cos_pa - z1 * sin_pa
    vertices.append(frame_rotation.to_global_coo(x1, y2, z2))

    y2 = -y1 * sin_pa - z1 * cos_pa
    z2 = -y1 * cos_pa + z1 * sin_pa
    vertices.append(frame_rotation.to_global_coo(x1, y2, z2))

    return PolygonSkyRegion(
        vertices=SkyCoord(vertices, unit="rad", frame="icrs"),
        visual=region.visual,
        meta=region.meta,
    )


def rectangle_pixel_to_polygon_pixel(
    region: RectanglePixelRegion,
) -> PolygonPixelRegion:
    """Convert a RectanglePixelRegion to a PolygonPixelRegion.

    Parameters
    ----------
    region : RectanglePixelRegion
        The region to convert.

    Returns
    -------
    PolygonPixelRegion
        The converted region.

    """
    center = region.center
    vertices = [
        [center.x - region.width / 2, center.y - region.height / 2],
        [center.x + region.width / 2, center.y - region.height / 2],
        [center.x + region.width / 2, center.y + region.height / 2],
        [center.x - region.width / 2, center.y + region.height / 2],
    ]
    rotation = region.angle.deg
    if rotation != 0:
        rotation = math.radians(rotation)
        cos_rot = math.cos(rotation)
        sin_rot = math.sin(rotation)
        for vertex in vertices:
            x = vertex[0] - center.x
            y = vertex[1] - center.y
            vertex[0] = x * cos_rot - y * sin_rot + center.x
            vertex[1] = x * sin_rot + y * cos_rot + center.y
    vertices = {
        "x": [vertex[0] for vertex in vertices],
        "y": [vertex[1] for vertex in vertices],
    }
    vertices = PixCoord(x=vertices["x"], y=vertices["y"])
    return PolygonPixelRegion(vertices=vertices, visual=region.visual, meta=region.meta)


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
            "CirclePixelRegion": self._from_circle_pixel_region,
            "EllipseSkyRegion": self._from_ellipse_sky_region,
            "EllipsePixelRegion": self._from_ellipse_pixel_region,
            "LineSkyRegion": self._from_line_sky_region,
            "LinePixelRegion": self._from_line_pixel_region,
            "PolygonSkyRegion": self._from_polygon_sky_region,
            "PolygonPixelRegion": self._from_polygon_pixel_region,
            "RectangleSkyRegion": self._from_rectangle_sky_region,
            "RectanglePixelRegion": self._from_rectangle_pixel_region,
        }
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

    def _from_stcs(self, stcs: str) -> None:
        self.region_type = "stcs"
        self.infos = {"stcs": stcs}

    def _from_circle_sky_region(self, region: CircleSkyRegion) -> None:
        self.region_type = "circle_sky"
        self.infos = {
            "ra": region.center.ra.deg,
            "dec": region.center.dec.deg,
            "radius": region.radius.deg,
        }

    def _from_circle_pixel_region(self, region: CirclePixelRegion) -> None:
        self.region_type = "circle_pixel"
        self.infos = {
            "x": region.center.x,
            "y": region.center.y,
            "radius": region.radius,
        }

    def _from_ellipse_sky_region(self, region: EllipseSkyRegion) -> None:
        self.region_type = "ellipse_sky"
        self.infos = {
            "ra": region.center.ra.deg,
            "dec": region.center.dec.deg,
            "a": region.width.deg,
            "b": region.height.deg,
            "theta": region.angle.deg,
        }

    def _from_ellipse_pixel_region(self, region: EllipsePixelRegion) -> None:
        self.region_type = "ellipse_pixel"
        self.infos = {
            "x": region.center.x,
            "y": region.center.y,
            "a": region.width,
            "b": region.height,
            "theta": region.angle.deg,
        }

    def _from_line_sky_region(self, region: LineSkyRegion) -> None:
        self.region_type = "line_sky"
        self.infos = {
            "ra1": region.start.ra.deg,
            "dec1": region.start.dec.deg,
            "ra2": region.end.ra.deg,
            "dec2": region.end.dec.deg,
        }

    def _from_line_pixel_region(self, region: LinePixelRegion) -> None:
        self.region_type = "line_pixel"
        self.infos = {
            "x1": region.start.x,
            "y1": region.start.y,
            "x2": region.end.x,
            "y2": region.end.y,
        }

    def _from_polygon_sky_region(self, region: PolygonSkyRegion) -> None:
        self.region_type = "polygon_sky"
        vertices = [[coord.ra.deg, coord.dec.deg] for coord in region.vertices]
        self.infos = {"vertices": vertices}

    def _from_polygon_pixel_region(self, region: PolygonPixelRegion) -> None:
        self.region_type = "polygon_pixel"
        vertices = [[coord.x, coord.y] for coord in region.vertices]
        self.infos = {"vertices": vertices}

    def _from_rectangle_sky_region(self, region: RectangleSkyRegion) -> None:
        # Rectangle is interpreted as a polygon in Aladin Lite
        self._from_polygon_sky_region(rectangle_to_polygon_region(region))

    def _from_rectangle_pixel_region(self, region: RectanglePixelRegion) -> None:
        # Rectangle is interpreted as a polygon in Aladin Lite
        self._from_polygon_pixel_region(rectangle_pixel_to_polygon_pixel(region))
