from enum import Enum


class OverlayType(Enum):
    """Overlay types enum."""

    MARKER = "marker"
    CATALOG = "catalog"
    TABLE = "table"
    OVERLAY_REGION = "overlay_region"
    OVERLAY_STCS = "overlay_stcs"
    JAVASCRIPT = "javascript"


class Overlay(dict):
    """Overlay class.

    This creates a dictionary with overlay properties for easy reference and
    interaction.
    """

    def __init__(self, overlay_info: dict, aladin: object) -> None:
        self.app = aladin
        overlay_type = overlay_info.get("type")
        if overlay_type not in {t.value for t in OverlayType}:
            raise ValueError(
                f"Invalid overlay type '{overlay_type}'. "
                f"Must be one of {[t.value for t in OverlayType]}."
            )
        super().__init__(overlay_info)

    @property
    def type(self) -> OverlayType:
        """Returns OverlayType."""
        return self.get("type")

    @property
    def options(self) -> dict:
        """Returns overlay options."""
        return self.get("options")

    @property
    def name(self) -> str:
        """Returns overlay name."""
        return self.options.get("name")

    @property
    def data(self) -> dict:
        """Returns overlay data."""
        ignored = ["type", "options"]
        return {key: value for key, value in self.items() if key not in ignored}

    def update(self, **new_options: any) -> dict:
        """Update overlay with new options.

        Parameters
        ----------
        new_options : any
            The arguments to update on the overlay.
        """
        if not new_options:
            raise ValueError(
                f"Cannot update overlayer `{self.name}` since no options to "
                "update were provided."
            )

        self.app.remove_overlay(self)
        updated_options = {**self.options, **new_options}

        if self.type == OverlayType.MARKER.value:
            markers = self.get("update_info")
            overlay_info = self.app.add_markers(markers, **updated_options)
        elif self.type == OverlayType.CATALOG.value:
            overlay_info = self.app.add_catalog_from_URL(
                self["votable_URL"], updated_options
            )
        elif self.type == OverlayType.TABLE.value:
            shape = updated_options.pop("shape", self.options.get("shape", "cross"))

            overlay_info = self.app.add_table(
                self["table"], shape=shape, **updated_options
            )
        elif self.type == OverlayType.OVERLAY_REGION.value:
            regions = self["update_info"]
            new_regions = []
            for region in regions:
                style = self.options.copy()
                if "color" in style:
                    style["edgecolor"] = style["color"]
                style.pop("name", None)
                region.visual.update(style)
                new_regions.append(region)
            overlay_info = self.app.add_graphic_overlay_from_region(
                regions, **updated_options
            )
        elif self.type == OverlayType.OVERLAY_STCS.value:
            update_info = self["update_info"]
            overlay_info = self.app.add_graphic_overlay_from_stcs(
                update_info, **updated_options
            )

        return overlay_info
