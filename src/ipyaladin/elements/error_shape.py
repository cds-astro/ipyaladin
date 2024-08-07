from dataclasses import dataclass
import math
from typing import Iterable, Optional

from astropy.coordinates import Angle
import astropy.units as u


def _error_radius_conversion_factor(
    column_unit: u.Unit, probability: Optional[float] = None
) -> Iterable:
    """Return the product of Mahalanobis distance and unit conversion factor.

    Parameters
    ----------
    column: `~astropy.units.core.Unit`
        The unit of the column containing the standard deviations. Should be an
        angle unit.
    probability: float, optional
        Probability that will be enclosed in the error shape.

    Returns
    -------
    float
    """
    unit_factor = Angle(1 * column_unit).to("deg").value
    if probability:
        mahalanobis_distance = math.sqrt(-2 * math.log(1 - probability))
    else:
        mahalanobis_distance = 1
    return unit_factor * mahalanobis_distance


@dataclass
class CircleError:
    r"""Circular error shape, accepted as `~ipyaladin.Aladin.add_table`'s shape.

    Attributes
    ----------
    radius: str
        Name of the column containing the radius of the error circle. The
        column's unit should be an angle-like unit.
    default_shape: str, default: "square"
        Can be "square", "circle", "plus", "cross", "rhomb", "triangle". This will be
        the fallback shape if the radius in None for a source.
    probability_threshold: float
        The confidence level contained in the drawn circle. Should be in ]0; 1[.
        When this is not given, the 1 sigma contour is plotted.

    Notes
    -----
    Correspondence table between sigmas and probability threshold:

    =================   ======================
    :math::`n_\sigma`        probability
    =================   ======================
    1                   :math::`1 - e^{-1/2}`
    2                   :math::`1 - e^{-2}`
    3                   :math::`1 - e^{-9/2}`
    =================   ======================
    """

    radius: str
    default_shape: str = "square"
    probability_threshold: float = 0


@dataclass
class EllipseError:
    r"""Elliptical error shape, accepted as `~ipyaladin.Aladin.add_table`'s shape.

    Attributes
    ----------
    maj_axis: str
        Name of the column containing the major axis of the error ellipse. The
        column's unit should be an angle-like unit.
    min_axis: str
        Name of the column containing the minor axis of the error ellipse. The
        column's unit should be an angle-like unit.
    angle: str
        Name of the column containing the angle of the error ellipse. The
        column's unit should be an angle-like unit.
    default_shape: str
        Can be "square", "circle", "plus", "cross", "rhomb", "triangle". This will be
        the fallback shape if one of the ellipse's axis in None for a source.
    probability_threshold: float
        The confidence level contained in the drawn circle. Should be in ]0; 1[.
        When this is not given, the 1 sigma contour is plotted.

    Notes
    -----
    Correspondence table between sigmas and probability threshold:

    =================   ======================
    :math::`n_\sigma`        probability
    =================   ======================
    1                   :math::`1 - e^{-1/2}`
    2                   :math::`1 - e^{-2}`
    3                   :math::`1 - e^{-9/2}`
    =================   ======================
    """

    maj_axis: str
    min_axis: str
    angle: str
    default_shape: str = "square"
    probability_threshold: float = 0
