import math
from typing import Tuple, Union
from gcodepy.gcode import Gcode


# moves in a spiral along the z axis with no extrusion
def zspiral(
    i: float,
) -> Tuple[Tuple[float, float, float], Union[float, None], Union[int, None]]:
    r = 20
    return (
        (r * math.cos(20 * math.pi * i), r * math.sin(20 * math.pi * i), 20 * i),
        0,
        None,
    )


g = Gcode("zspiral.gcode")
g.home()
g.zero_extruder()
g.travel_absolute((0, 0, 0.2))

g.travel((50, 50, 0))
g.draw_func(zspiral)

g.travel_absolute((0, 0, g.get_z() + 20))

g.close()
print("done! check out zspiral.gcode")
