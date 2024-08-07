"""Top-level package for ipyaladin."""

from .elements.error_shape import CircleError, EllipseError  # noqa: F401
from .elements.marker import Marker  # noqa: F401
from .widget import Aladin  # noqa: F401
from .__about__ import __version__, __aladin_lite_version__  # noqa: F401
