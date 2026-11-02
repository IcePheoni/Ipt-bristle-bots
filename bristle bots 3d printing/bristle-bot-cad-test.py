import os
import math
from build123d import *

# 1. Create the output folder if it doesn't exist yet
os.makedirs("exports", exist_ok=True)

# ================= PARAMETERS =================
CORE_RADIUS  = 10.0   # 20 mm base diameter
CORE_HEIGHT  = 6.0    # Deck thickness
LEG_RADIUS   = 0.75   # 1.5 mm diameter solid peg
LEG_LENGTH   = 7.0    # Length in mm
LEG_ANGLE    = 15.0   # Slant angle in degrees from vertical
LEG_PITCH_R  = 7.5    # Radius of leg placement circle

MOTOR_RADIUS = 5.2    # Cavity for 10 mm ERM coin motor (+0.2 mm clearance)
MOTOR_DEPTH  = 2.8
BATTERY_R    = 6.4    # Cavity for CR1220 battery (+0.2 mm clearance)
BATTERY_D    = 2.2
WIRE_HOLE_R  = 1.0    # Center conduit for lead wires
# ==============================================

# 2. Build the 3D part (this creates the 'core' object)
with BuildPart() as core:
    # Solid cylindrical base
    Cylinder(radius=CORE_RADIUS, height=CORE_HEIGHT)

    # Bottom cavity for ERM vibration motor
    with Locations((0, 0, -CORE_HEIGHT / 2)):
        Cylinder(
            radius=MOTOR_RADIUS, 
            height=MOTOR_DEPTH, 
            align=(Align.CENTER, Align.CENTER, Align.MIN), 
            mode=Mode.SUBTRACT
        )

    # Top cavity for CR1220 coin cell
    with Locations((0, 0, CORE_HEIGHT / 2)):
        Cylinder(
            radius=BATTERY_R, 
            height=BATTERY_D, 
            align=(Align.CENTER, Align.CENTER, Align.MAX), 
            mode=Mode.SUBTRACT
        )

    # Central wiring pass-through
    Cylinder(radius=WIRE_HOLE_R, height=CORE_HEIGHT + 2, mode=Mode.SUBTRACT)

    # Three slanted tripod legs (120° symmetric spacing)
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        x = LEG_PITCH_R * math.cos(rad)
        y = LEG_PITCH_R * math.sin(rad)
        with Locations(Location((x, y, -CORE_HEIGHT / 2), (0, LEG_ANGLE, angle))):
            Cylinder(
                radius=LEG_RADIUS, 
                height=LEG_LENGTH, 
                align=(Align.CENTER, Align.CENTER, Align.MAX)
            )

# 3. Export the finished part (now 'core' exists)
export_stl(core.part, "exports/core_tripod.stl")
export_step(core.part, "exports/core_tripod.step")

print("Success! File saved to exports/core_tripod.stl")