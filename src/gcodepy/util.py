import math
from typing import Iterable, Tuple


def dist(delta: Iterable[float]) -> float:
    return math.sqrt(sum(i ** 2 for i in delta))


def arclen(
    center: Tuple[float, float], other: Tuple[float, float], clockwise: bool
) -> float:
    radius = dist(center)
    if other == (0.0, 0.0):
        return math.pi * radius ** 2

    # using formula theta = atan2(||u x v||, u . v)
    rvec = tuple(-i for i in center)
    rt = tuple(other[i] - center[i] for i in range(2))
    uxv = rvec[0] * rt[1] - rvec[1] * rt[0]
    udv = rvec[0] * rt[0] + rvec[1] * rt[1]
    angle = math.atan2(uxv, udv)
    if abs(angle) < 1e-6:
        return 0

    if clockwise and angle > 0:
        angle = 2 * math.pi - angle
    elif not clockwise and angle < 0:
        angle += 2 * math.pi

    return angle * radius


def calculate_extrusion_length(
    path_length: float,
    line_width: float,
    layer_height: float,
    filament_width: float,
) -> float:
    # uses math from https://manual.slic3r.org/advanced/flow-math
    flat_area = (line_width - layer_height) * layer_height
    round_area = math.pi * (layer_height / 2) ** 2
    ext_area = flat_area + round_area
    ext_volume = ext_area * path_length
    return ext_volume / (math.pi * (filament_width / 2) ** 2)
