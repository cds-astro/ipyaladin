import math

import astropy.units as u
import numpy as np

from ipyaladin.elements.error_shape import _error_radius_conversion_factor


def test_error_radius_conversion_factor() -> None:
    # degrees and 1 sigma should give 1
    assert np.isclose(_error_radius_conversion_factor(u.deg, 1 - math.exp(-1 / 2)), 1)
