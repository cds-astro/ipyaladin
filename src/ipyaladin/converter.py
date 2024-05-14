import math
from regions import RectangleSkyRegion, PolygonSkyRegion
from astropy.coordinates import SkyCoord

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
        """Create a rotation matrix.

        Parameters
        ----------
        r11-r33 : float
            The elements of the rotation matrix.

        """
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
        return xyz_to_lonlat(x, y, z)


def xyz_to_lonlat(x: float, y: float, z: float) -> tuple[float, float]:
    """Convert cartesian coordinates to spherical coordinates.

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
    r2 = x * x + y * y
    lat = math.atan2(z, math.sqrt(r2))
    lon = math.atan2(y, x)
    if lon < 0:
        lon += TWICE_PI
    return lon, lat


def box2polygon(region: RectangleSkyRegion) -> PolygonSkyRegion:
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

    return PolygonSkyRegion(vertices=SkyCoord(vertices, unit="rad", frame="icrs"))
