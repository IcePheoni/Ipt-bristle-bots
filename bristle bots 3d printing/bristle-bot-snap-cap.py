import os
import math
from build123d import *

os.makedirs("exports", exist_ok=True)

# ================= PARAMETERS =================
CORE_RADIUS        = 10.0   # 20 mm base diameter
CORE_HEIGHT        = 6.0    # Deck thickness
LEG_RADIUS         = 0.75   # 1.5 mm diameter solid peg
LEG_LENGTH         = 7.0    # Length in mm
LEG_ANGLE          = 15.0   # Slant angle in degrees from vertical
LEG_PITCH_R        = 7.5    # Radius of leg placement circle

MOTOR_RADIUS       = 5.2    # Cavity for 10 mm ERM coin motor
MOTOR_DEPTH        = 2.8
BATTERY_R          = 6.4    # CR1220 battery radius
WIRE_HOLE_R        = 1.0    # Radius of the wire conduit (1.0 = 2mm diameter)

# --- Wire Hole Placement ---
WIRE_HOLE_ANGLE    = 180.0  # Placed at the back, opposite Leg 1 (0 degrees)
WIRE_HOLE_PITCH_R  = 5.4    # Distance from center. (5.2 mm puts it flush with the motor pocket wall)

# --- Snap-Fit Tower ---
TOWER_HEIGHT       = 4.5    # Height of the battery compartment
LIP_RADIUS         = 8.2    # Outer radius of the locking lip
# ==============================================

# 1. Generate the Active Core with Snap-Lock Tower
with BuildPart() as core:
    # Solid cylindrical base and motor pocket
    Cylinder(radius=CORE_RADIUS, height=CORE_HEIGHT)
    with Locations((0, 0, -CORE_HEIGHT / 2)):
        Cylinder(radius=MOTOR_RADIUS, height=MOTOR_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    
    # Perimeter wiring conduit (placed using the new variables)
    wire_rad = math.radians(WIRE_HOLE_ANGLE)
    with Locations((WIRE_HOLE_PITCH_R * math.cos(wire_rad), WIRE_HOLE_PITCH_R * math.sin(wire_rad), 0)):
        Cylinder(radius=WIRE_HOLE_R, height=CORE_HEIGHT + TOWER_HEIGHT + 2, mode=Mode.SUBTRACT)

    # Three slanted tripod legs embedded into the floor
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        x = LEG_PITCH_R * math.cos(rad)
        y = LEG_PITCH_R * math.sin(rad)
        with Locations(Location((x, y, -CORE_HEIGHT / 2 + 0.8), (0, LEG_ANGLE, angle))):
            Cylinder(radius=LEG_RADIUS, height=LEG_LENGTH + 0.8, align=(Align.CENTER, Align.CENTER, Align.MAX))

    # --- The Snap-Lock Battery Tower ---
    with Locations((0, 0, CORE_HEIGHT / 2)):
        # Main tower cylinder (R=8.0)
        Cylinder(radius=8.0, height=TOWER_HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # The retaining lip at the very top (R=8.2)
        with Locations((0, 0, TOWER_HEIGHT - 0.5)):
            Cylinder(radius=LIP_RADIUS, height=0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # Hollow out the inside of the tower for the CR1220 battery
        Cylinder(radius=BATTERY_R, height=TOWER_HEIGHT + 1, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)


# 2. Generate the Push-On Cap
with BuildPart() as battery_cap:
    # Outer cap body
    Cylinder(radius=CORE_RADIUS, height=TOWER_HEIGHT + 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    
    with Locations((0, 0, -0.1)):
        # Main inner hollow (R=8.15 for a snug friction fit over the R=8.0 tower)
        Cylinder(radius=8.15, height=TOWER_HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Inner groove to receive the retaining lip (R=8.35)
        with Locations((0, 0, TOWER_HEIGHT - 0.7)):
            Cylinder(radius=8.35, height=0.9, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

# Export models
export_stl(core.part, "exports/core_tripod_snap.stl")
export_stl(battery_cap.part, "exports/battery_cap_snap.stl")
print("Success! Core and Cap saved to exports.")