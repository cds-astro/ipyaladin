from dataclasses import dataclass
from typing import Tuple, Union

from astropy.coordinates import SkyCoord, Longitude, Latitude
from ipyaladin.utils._coordinate_parser import _parse_coordinate_string


@dataclass
class Marker:
    """A class representing a marker in Aladin Lite."""

    def __init__(
        self,
        position: Union[str, SkyCoord, Tuple[Longitude, Latitude]],
        title: str,
        description: str,
    ) -> None:
        self.title = title
        self.description = description
        if isinstance(position, SkyCoord):
            self.lon = position.ra.deg
            self.lat = position.dec.deg
        elif isinstance(position, str):
            self.lon, self.lat = _parse_coordinate_string(position)
        elif (
            isinstance(position, Tuple)
            and isinstance(position[0], Longitude)
            and isinstance(position[1], Latitude)
        ):
            self.lon = position[0].deg
            self.lat = position[1].deg
