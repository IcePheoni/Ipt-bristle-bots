import os
import math
from build123d import *

# 1. Output directory setup
os.makedirs("exports", exist_ok=True)

# ==================== PARAMETERS ====================
# --- Chassis Dimensions ---
CORE_RADIUS        = 10.0   # 20 mm base diameter
CORE_HEIGHT        = 6.0    # Deck height in mm

# --- Tripod Leg Mechanics ---
LEG_RADIUS         = 0.75   # 1.5 mm diameter peg (stiff elastic beam)
LEG_LENGTH         = 7.0    # Exposed leg length beneath core (mm)
LEG_ANGLE          = 15.0   # Slant angle in degrees from vertical
LEG_PITCH_R        = 7.5    # Radial distance of legs from chassis center
LEG_EMBED          = 0.8    # Depth buried inside core to eliminate notch gaps

# --- Motor Pocket (Bottom) ---
MOTOR_RADIUS       = 5.2    # 10 mm coin motor cavity (+0.2 mm fit tolerance)
MOTOR_DEPTH        = 2.8    # Recess depth in mm

# --- Battery Pocket (Top) ---
BATTERY_R          = 6.4    # CR1220 coin cell cavity (+0.2 mm fit tolerance)
BATTERY_D          = 2.2    # Recess depth in mm

# --- Wiring Conduit (Perimeter Pass-Through) ---
WIRE_HOLE_R        = 1.0    # Hole radius (2.0 mm diameter for 2 motor leads)
WIRE_HOLE_PITCH_R  = 5.4    # Radial distance from center (5.2 mm sits at motor wall)
WIRE_HOLE_ANGLE    = 180.0   # Degrees (60° is midpoint between Leg 1 at 0° and Leg 2 at 120°)
# ====================================================

# 2. Build Geometry
with BuildPart() as core:
    # 2.1 Solid chassis base
    Cylinder(radius=CORE_RADIUS, height=CORE_HEIGHT)

    # 2.2 Motor cavity bored upward from bottom face
    with Locations((0, 0, -CORE_HEIGHT / 2)):
        Cylinder(
            radius=MOTOR_RADIUS,
            height=MOTOR_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT
        )

    # 2.3 Battery pocket recessed downward from top deck
    with Locations((0, 0, CORE_HEIGHT / 2)):
        Cylinder(
            radius=BATTERY_R,
            height=BATTERY_D,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
            mode=Mode.SUBTRACT
        )

    # 2.4 Perimeter wire conduit connecting motor and battery cavities
    wire_rad = math.radians(WIRE_HOLE_ANGLE)
    wire_x = WIRE_HOLE_PITCH_R * math.cos(wire_rad)
    wire_y = WIRE_HOLE_PITCH_R * math.sin(wire_rad)

    with Locations((wire_x, wire_y, 0)):
        Cylinder(radius=WIRE_HOLE_R, height=CORE_HEIGHT + 2, mode=Mode.SUBTRACT)

    # 2.5 Three slanted tripod legs embedded into bottom face
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        x = LEG_PITCH_R * math.cos(rad)
        y = LEG_PITCH_R * math.sin(rad)
        with Locations(Location((x, y, -CORE_HEIGHT / 2 + LEG_EMBED), (0, LEG_ANGLE, angle))):
            Cylinder(
                radius=LEG_RADIUS,
                height=LEG_LENGTH + LEG_EMBED,
                align=(Align.CENTER, Align.CENTER, Align.MAX)
            )

# 3. Export Manufacturing Files
export_stl(core.part, "exports/core_tripod.stl")
export_step(core.part, "exports/core_tripod.step")

print("Success! File saved to exports/core_tripod.stl")