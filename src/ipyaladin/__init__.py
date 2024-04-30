"""Top-level package for ipyaladin."""

import importlib.metadata

from .aladin import Aladin  # noqa: F401


try:
    __version__ = importlib.metadata.version("ipyaladin")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
