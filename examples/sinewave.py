import math
from typing import Tuple, Union
from gcodepy.gcode import Gcode


# maps from [0.0, 1.0] to sin([0.0, 6pi])
def pattern(
    i: float,
) -> Tuple[Tuple[float, float, float], Union[float, None], Union[int, None]]:
    # print(i, 10 * math.sin(i * 6 * math.pi))
    return (60 * i, 5 * math.sin(i * 6 * math.pi), 0), None, None


g = Gcode("sinewave.gcode")
g.home()
g.zero_extruder()
g.travel_absolute((0, 0, 0.2))

g.set_tool_temp(220)
g.wait_tool_temp(220)
g.set_bed_temp(60)
g.wait_bed_temp(60)

g.travel((10, 10, 0))
g.draw_func(pattern, nsamples=100)

g.set_tool_temp(0)
g.set_bed_temp(0)
g.travel_absolute((0, 0, g.get_z() + 20))

g.close()
print("done! check out sinewave.gcode")
