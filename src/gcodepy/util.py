import math
from typing import Tuple


def dist(delta: Tuple[float, float, float]) -> float:
    return math.sqrt(sum(i ** 2 for i in delta))


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
