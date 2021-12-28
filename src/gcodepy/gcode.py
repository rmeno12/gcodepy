class Gcode:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.file = open(filename, "w")
        self.pos = [None] * 4

    def close(self):
        self.file.close()

    def home(self):
        self.file.write("G28\n")
        self.pos = [0, 0, 0] + [self.pos[-1]]

    def get_x(self):
        return self.pos[0]

    def get_y(self):
        return self.pos[1]

    def get_z(self):
        return self.pos[2]

    def get_e(self):
        return self.pos[3]

    def zero_extruder(self):
        self.file.write("G92 E0\n")
        self.pos[-1] = 0

    def set_tool_temp(self, temperature: int, tool_index=0):
        out = f"M104 S{temperature}"
        if tool_index != 0:
            out += f" T{tool_index}"
        self.file.write(out + "\n")

    def wait_tool_temp(self, temperature: int, tool_index=0, on_cool=False):
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

    def wait_bed_temp(self, temperature: int, on_cool=False):
        out = "M190"
        if on_cool:
            out += f" R{temperature}"
        else:
            out += f" S{temperature}"
        self.file.write(out + "\n")

    def travel(self, x=0.0, y=0.0, z=0.0, feedrate=2400):
        self.pos[0] += x
        self.pos[1] += y
        self.pos[2] += z
        self.file.write(
            f"G0 F{feedrate} X{self.pos[0]} Y{self.pos[1]} Z{self.pos[2]}\n"
        )

    def travel_arc(
        self,
        i: float,
        j: float,
        x=0.0,
        y=0.0,
        z=0.0,
        clockwise=True,
        feedrate=2400,
    ):
        self.draw_arc(0.0, i, j, x, y, z, clockwise, feedrate)

    def travel_arc_r(
        self,
        r: float,
        x=0.0,
        y=0.0,
        z=0.0,
        clockwise=True,
        feedrate=2400,
    ):
        self.draw_arc_r(0.0, r, x, y, z, clockwise, feedrate)

    def travel_absolute(self, x=0.0, y=0.0, z=0.0, feedrate=2400):
        self.pos[0] = x
        self.pos[1] = y
        self.pos[2] = z
        self.file.write(
            f"G0 F{feedrate} X{self.pos[0]} Y{self.pos[1]} Z{self.pos[2]}\n"
        )

    def draw(self, e: float, x=0.0, y=0.0, z=0.0, feedrate=2400):
        self.pos[0] += x
        self.pos[1] += y
        self.pos[2] += z
        self.pos[3] += e
        self.file.write(
            f"G1 F{feedrate} X{self.pos[0]} Y{self.pos[1]} Z{self.pos[2]} E{self.pos[3]}\n"
        )

    def draw_arc(
        self,
        e: float,
        i: float,
        j: float,
        x=0.0,
        y=0.0,
        z=0.0,
        clockwise=True,
        feedrate=2400,
    ):
        out = "G2" if clockwise else "G3"
        out += f" F{feedrate}"
        self.pos[0] += x
        self.pos[1] += y
        self.pos[2] += z
        self.pos[3] += e
        out += f" I{i} J{j} E{self.pos[3]}"
        if x != 0.0:
            out += f" X{self.pos[0]}"
        if y != 0.0:
            out += f" Y{self.pos[1]}"
        if z != 0.0:
            out += f" Z{self.pos[2]}"
        self.file.write(out + "\n")

    def draw_arc_r(
        self,
        e: float,
        r: float,
        x=0.0,
        y=0.0,
        z=0.0,
        clockwise=True,
        feedrate=2400,
    ):
        if x == 0.0 and y == 0.0:
            raise ValueError("Both x and y cannot be 0. Make sure to set at least one!")
        out = "G2" if clockwise else "G3"
        out += f" F{feedrate}"
        self.pos[0] += x
        self.pos[1] += y
        self.pos[2] += z
        self.pos[3] += e
        out += f" R{r} E{self.pos[3]}"
        if x != 0.0:
            out += f" X{self.pos[0]}"
        if y != 0.0:
            out += f" Y{self.pos[1]}"
        if z != 0.0:
            out += f" Z{self.pos[2]}"
        self.file.write(out + "\n")
