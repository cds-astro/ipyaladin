import warnings
from .overlay import Overlay


class OverlayManager:
    """OverlayManager class.

    This creates standard handling for Overlay objects.
    """

    def __init__(self, aladin: object) -> None:
        self.app = aladin
        self._overlays_dict = {}

    def __setitem__(self, key: str, value: any) -> None:
        self._overlays_dict[key] = value

    def __getitem__(self, key: str) -> str:
        return self._overlays_dict[key]

    def __contains__(self, key: str) -> bool:
        return key in self._overlays_dict

    def items(self) -> dict:
        """Return overlays in manager."""
        return self._overlays_dict.items()

    def pop(self, key: str) -> None:
        """Remove overlay from manager."""
        self._overlays_dict.pop(key)

    def keys(self) -> list:
        """Return names of overlays in manager."""
        return self._overlays_dict.keys()

    def make_unique_name(self, name: str) -> str:
        """Create a unique layer name.

        Parameters
        ----------
        name : str
            The current name of the layer to be added to the widget.

        Returns
        -------
        unique_name
            A string that is a unique name for the layer being added.
        """
        unique_name = name
        i = 1

        while unique_name in self._overlays_dict:
            unique_name = f"{name}_{i}"
            i += 1

        return unique_name

    def common_overlay_handling(self, overlay_options: dict, default_name: str) -> dict:
        """Handle common functionality across added overlay methods.

        Parameters
        ----------
        overlay_options : dict
            The dictionary of overlay options for the layer being added to the widget.
        default_name : str
            The default name of the overlay being added.

        Returns
        -------
        overlay_options
            The updated dictionary of overlay options for the layer being added
            to the widget.
        """
        name = overlay_options.get("name", default_name)
        unique_name = self.make_unique_name(name=name)
        overlay_options["name"] = unique_name

        if unique_name != name:
            warnings.warn(
                f"Overlayer name `{name}` is already in use. Name `{unique_name}` "
                "will be used instead.",
                stacklevel=2,
            )

        return overlay_options

    def add_overlay(self, overlay_info: dict) -> dict:
        """Add overlay to overlay dictionary.

        Parameters
        ----------
        overlay_info : dict
            The dictionary of overlay info for the layer being added to the widget.
            Includes overlay options and specific overlay info (URLs, coords, etc.).

        Returns
        -------
        overlay_info
            The overlay options for the layer being added to the widget.
        """
        overlay_info = Overlay(overlay_info, self.app)

        self[overlay_info["options"]["name"]] = overlay_info

        return overlay_info
