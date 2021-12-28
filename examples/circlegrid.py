from gcodepy.gcode import Gcode

g = Gcode("circlegrid.gcode")
g.home()
g.zero_extruder()
g.travel_absolute(0, 0, 0)

g.set_tool_temp(220)
g.wait_tool_temp(220)
g.set_bed_temp(60)
g.wait_bed_temp(60)

g.travel(10, 10, 0.2)
for i in range(3):
    g.travel(0, 20)
    for j in range(3):
        g.travel(20)
        g.draw_arc(5, 0, -10)
    g.travel(-60)

g.set_tool_temp(0)
g.set_bed_temp(0)
g.travel_absolute(0, 0, g.get_z() + 20)

g.close()
print("done! check out circlegrid.gcode")
