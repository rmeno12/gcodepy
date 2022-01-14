from typing import Callable, Tuple, Union
import math
from . import util

# TODO:
# minimize feedrate output
# draw absolute
# travel func
# catch more invalid inputs
class Gcode:
    def __init__(
        self,
        filename: str,
        layer_height: float = 0.2,
        line_width: float = 0.4,
        filament_width: float = 1.75,
        home_position: Tuple[float, float, float] = (0, 0, 0),
        extrusion_length_calculator: Callable[
            [float, float, float, float], float
        ] = util.calculate_extrusion_length,
    ) -> None:
        self.filename = filename
        self.file = open(filename, "w")
        self.layer_height = layer_height
        self.line_width = line_width
        self.filament_width = filament_width
        self.home_pos = home_position
        self.extrusion_length_calculator = extrusion_length_calculator
        self.pos = [None] * 3
        self.e = None

    def close(self):
        self.file.close()

    def home(self):
        self.file.write("G28\n")
        self.pos = list(self.home_pos)

    def get_x(self) -> float:
        return self.pos[0]

    def get_y(self) -> float:
        return self.pos[1]

    def get_z(self) -> float:
        return self.pos[2]

    def get_e(self) -> float:
        return self.e

    def set_layer_height(self, layer_height: float):
        self.layer_height = layer_height

    def set_line_width(self, line_width: float):
        self.line_width = line_width

    def set_filament_width(self, filament_width: float):
        self.filament_width = filament_width

    def zero_extruder(self):
        self.file.write("G92 E0\n")
        self.e = 0

    def set_tool_temp(self, temperature: int, tool_index: int = 0):
        out = f"M104 S{temperature}"
        if tool_index != 0:
            out += f" T{tool_index}"
        self.file.write(out + "\n")

    def wait_tool_temp(
        self, temperature: int, tool_index: int = 0, on_cool: bool = False
    ):
        out = "M109"
        if on_cool:
            out += f" R{temperature}"
        else:
            out += f" S{temperature}"
        if tool_index != 0:
            out += f" T{tool_index}"
        self.file.write(out + "\n")

    def set_bed_temp(self, temperature: int):
        out = f"M140 S{temperature}"
        self.file.write(out + "\n")

    def wait_bed_temp(self, temperature: int, on_cool: bool = False):
        out = "M190"
        if on_cool:
            out += f" R{temperature}"
        else:
            out += f" S{temperature}"
        self.file.write(out + "\n")

    def travel(self, delta: Tuple[float, float, float], feedrate: int = 2400):
        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]
        out = f"G0 F{feedrate}"
        if delta[0] != 0.0:
            out += f" X{self.pos[0]}"
        if delta[1] != 0.0:
            out += f" Y{self.pos[1]}"
        if delta[2] != 0.0:
            out += f" Z{self.pos[2]}"
        self.file.write(out + "\n")

    def travel_arc(
        self,
        i: float,
        j: float,
        delta: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        clockwise: bool = True,
        feedrate: int = 2400,
    ):
        self.draw_arc(0.0, i, j, delta, clockwise, feedrate)

    def travel_arc_r(
        self,
        r: float,
        delta: Tuple[float, float, float],
        clockwise: bool = True,
        feedrate: int = 2400,
    ):
        self.draw_arc_r(0.0, r, delta, clockwise, feedrate)

    def travel_absolute(
        self, location: Tuple[float, float, float], feedrate: int = 2400
    ):
        self.pos[0] = location[0]
        self.pos[1] = location[1]
        self.pos[2] = location[2]
        self.file.write(
            f"G0 F{feedrate} X{self.pos[0]} Y{self.pos[1]} Z{self.pos[2]}\n"
        )

    def draw(
        self, delta: Tuple[float, float, float], e: float = None, feedrate: int = 2400
    ):
        if e is None:
            e = self.extrusion_length_calculator(
                util.dist(delta),
                self.line_width,
                self.layer_height,
                self.filament_width,
            )
        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]
        self.e += e
        out = f"G1 F{feedrate}"
        if delta[0] != 0.0:
            out += f" X{self.pos[0]}"
        if delta[1] != 0.0:
            out += f" Y{self.pos[1]}"
        if delta[2] != 0.0:
            out += f" Z{self.pos[2]}"
        out += f" E{e}"
        self.file.write(out + "\n")

    def draw_arc(
        self,
        i: float,
        j: float,
        delta: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        e: float = None,
        clockwise: bool = True,
        feedrate: int = 2400,
    ):
        if e is None:
            e = self.extrusion_length_calculator(
                util.arclen((i, j), delta[:2], clockwise),
                self.line_width,
                self.layer_height,
                self.filament_width,
            )
        out = "G2" if clockwise else "G3"
        out += f" F{feedrate}"
        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]
        self.e += e
        out += f" I{i} J{j} E{self.e}"
        if delta[0] != 0.0:
            out += f" X{self.pos[0]}"
        if delta[1] != 0.0:
            out += f" Y{self.pos[1]}"
        if delta[2] != 0.0:
            out += f" Z{self.pos[2]}"
        self.file.write(out + "\n")

    def draw_arc_r(
        self,
        r: float,
        delta: Tuple[float, float, float],
        e: float = None,
        clockwise: bool = True,
        feedrate: int = 2400,
    ):
        if r == 0 or r is None:
            raise ValueError("Radius r cannot be 0 or None.")
        if e is None:
            d2 = (delta[0] / 2, delta[1] / 2)
            m = -1 if clockwise ^ (r < 0) else 1
            l = util.dist(d2)
            h2 = (r - l) * (r + l)
            h = 0 if h2 < 0 else math.sqrt(h2)
            s = (-d2[1], d2[0])
            s = [s[i] / l * m * h for i in range(2)]
            center = tuple(d2[i] + s[i] for i in range(2))
            e = self.extrusion_length_calculator(
                util.arclen(center, delta[:2], clockwise),
                self.line_width,
                self.layer_height,
                self.filament_width,
            )
        if delta[0] == 0.0 and delta[1] == 0.0:
            raise ValueError("Both x and y cannot be 0. Make sure to set at least one!")
        out = "G2" if clockwise else "G3"
        out += f" F{feedrate}"
        self.pos[0] += delta[0]
        self.pos[1] += delta[1]
        self.pos[2] += delta[2]
        self.e += e
        out += f" R{r} E{self.e}"
        if delta[0] != 0.0:
            out += f" X{self.pos[0]}"
        if delta[1] != 0.0:
            out += f" Y{self.pos[1]}"
        if delta[2] != 0.0:
            out += f" Z{self.pos[2]}"
        self.file.write(out + "\n")

    def draw_func(
        self,
        func: Callable[
            [float],
            Tuple[Tuple[float, float, float], Union[float, None], Union[int, None]],
        ],
        start: float = 0.0,
        end: float = 1.0,
        nsamples: int = 1000,
    ):
        scale = (end - start) / nsamples
        start_pos = (self.get_x(), self.get_y(), self.get_z())
        last_pos = start_pos
        for i in range(0, nsamples):
            t = start + i * scale
            start_delta, e, feed = func(t)
            delta = [start_delta[i] + start_pos[i] - last_pos[i] for i in range(3)]
            if feed is not None:
                self.draw(delta, e=e, feedrate=feed)
            else:
                self.draw(delta, e=e)
            last_pos = (self.get_x(), self.get_y(), self.get_z())
