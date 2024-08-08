from typing import Tuple, Union

from astropy.coordinates import SkyCoord
from ipyaladin.utils._coordinate_parser import parse_coordinate_string


class Marker:
    """A class representing a marker in Aladin Lite."""

    def __init__(
        self,
        position: Union[str, SkyCoord, Tuple[float, float]],
        title: str,
        description: str,
    ) -> None:
        self.title = title
        self.description = description
        if isinstance(position, SkyCoord):
            self.position = f"{position.ra.deg} {position.dec.deg}"
        elif isinstance(position, str):
            sc = parse_coordinate_string(position)
            self.position = f"{sc.ra.deg} {sc.dec.deg}"
        else:
            self.position = f"{position[0]} {position[1]}"

    def to_dict(self) -> dict:
        """Convert the marker to a dictionary.

        Returns
        -------
        dict
            The marker as a dictionary
        """
        return {
            "position": self.position,
            "title": self.title,
            "description": self.description,
        }
