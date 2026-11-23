import os
import math
from build123d import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)
MODEL_VERSION = "v12"

# ================= PARAMETERS (SNAP-FIT MEMBRANE V10) =================
BATTERY_DIAM        = 20.0   
BATTERY_DIAM_BUFFER = 1.5    
BATTERY_D           = 3.2    

MOTOR_DIAM          = 10.0   
MOTOR_DIAM_BUFFER   = 1.2    
MOTOR_DEPTH         = 3.0    

BATTERY_R           = (BATTERY_DIAM + BATTERY_DIAM_BUFFER) / 2.0  # 10.75 mm
MOTOR_RADIUS        = (MOTOR_DIAM + MOTOR_DIAM_BUFFER) / 2.0      # 5.60 mm

# --- Wire Tunnel & Bottom Trench ---
WIRE_HOLE_R         = 1.5    
WIRE_HOLE_ANGLE     = 180.0  
WIRE_HOLE_PITCH_R   = 9.3    # Shifted inward to 9.3 mm
TRENCH_WIDTH        = 2.8    
MEMBRANE_THICKNESS  = 0.2    # Leaves a 0.2mm solid skin over the hole for perfect bridging

# --- Snap-Lock Tower & Cap ---
TOWER_WALL          = 1.6    
TOWER_OUTER_R       = BATTERY_R + TOWER_WALL                      # 12.35 mm
TOWER_HEIGHT        = BATTERY_D + 0.4                             # 3.60 mm
LIP_RADIUS          = TOWER_OUTER_R + 0.35                        # Slightly stronger snap retaining lip
CAP_CLEARANCE       = 0.2   
CAP_WALL            = 1.4    
CAP_ROOF_THICK      = 1.2
CONTACT_BOSS_H      = 0.35   
CONTACT_BOSS_R      = 3.2

# --- Chassis & Tripod Legs ---
CORE_RADIUS         = 15.0   
CORE_HEIGHT         = 4.5    
LEG_RADIUS          = 0.85    
LEG_ROOT_RADIUS     = 1.25
LEG_TIP_RADIUS      = 0.85
LEG_LENGTH          = 9.0    
LEG_ANGLE           = 15.0   
LEG_PITCH_R         = 13.5   
LEG_EMBED           = 0.8    
# ======================================================================

wire_rad = math.radians(WIRE_HOLE_ANGLE)

# 1. Active Drive Core with Snap-Lock Tower
with BuildPart() as core:
    Cylinder(radius=CORE_RADIUS, height=CORE_HEIGHT)

    # Bottom motor pocket (Center)
    with Locations((0, 0, -CORE_HEIGHT / 2)):
        Cylinder(radius=MOTOR_RADIUS, height=MOTOR_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # Horizontal bottom trench connecting the center motor to the outer perimeter hole
    with Locations((WIRE_HOLE_PITCH_R/2 * math.cos(wire_rad), WIRE_HOLE_PITCH_R/2 * math.sin(wire_rad), -CORE_HEIGHT / 2)):
        Box(length=WIRE_HOLE_PITCH_R + WIRE_HOLE_R, width=TRENCH_WIDTH, height=MOTOR_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # The vertical wire hole stops 0.2mm short of piercing the battery pocket floor
    with Locations((WIRE_HOLE_PITCH_R * math.cos(wire_rad), WIRE_HOLE_PITCH_R * math.sin(wire_rad), -MEMBRANE_THICKNESS)):
        Cylinder(radius=WIRE_HOLE_R, height=CORE_HEIGHT + TOWER_HEIGHT, mode=Mode.SUBTRACT)

    # Three embedded slanted tripod legs
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        x = LEG_PITCH_R * math.cos(rad)
        y = LEG_PITCH_R * math.sin(rad)
        with Locations(Location((x, y, -CORE_HEIGHT / 2 + LEG_EMBED), (0, LEG_ANGLE, 0))):
            Cone(
                bottom_radius=LEG_TIP_RADIUS,
                top_radius=LEG_ROOT_RADIUS,
                height=LEG_LENGTH + LEG_EMBED,
                align=(Align.CENTER, Align.CENTER, Align.MAX)
            )

    # Snap-lock battery tower on top deck
    with Locations((0, 0, CORE_HEIGHT / 2)):
        Cylinder(radius=TOWER_OUTER_R, height=TOWER_HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, TOWER_HEIGHT - 0.5)):
            Cylinder(radius=LIP_RADIUS, height=0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Battery pocket subtracts down to Z=0, leaving the 0.2mm membrane intact over the hole
        Cylinder(radius=BATTERY_R, height=TOWER_HEIGHT + 1, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Floor channel on the top side for the negative lead to reach the center
        with Locations((0, 0, 0)):
            Box(length=WIRE_HOLE_PITCH_R * 2, width=2.5, height=0.6, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

# 2. Snap Cap with Internal Contact Boss
with BuildPart() as battery_cap:
    Cylinder(radius=CORE_RADIUS, height=TOWER_HEIGHT + CAP_ROOF_THICK, align=(Align.CENTER, Align.CENTER, Align.MIN))

    with Locations((0, 0, -0.1)):
        Cylinder(radius=TOWER_OUTER_R + CAP_CLEARANCE, height=TOWER_HEIGHT + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, 0, TOWER_HEIGHT - 0.65)):
            Cylinder(radius=LIP_RADIUS + CAP_CLEARANCE, height=0.85, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    with Locations((0, 0, TOWER_HEIGHT)):
        Cylinder(radius=CONTACT_BOSS_R, height=CONTACT_BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MAX))

export_stl(core.part, os.path.join(EXPORT_DIR, f"core_tripod_snap_{MODEL_VERSION}.stl"))
export_stl(battery_cap.part, os.path.join(EXPORT_DIR, f"battery_cap_snap_{MODEL_VERSION}.stl"))
print(f"Success! Snap-Fit Core with Membrane {MODEL_VERSION} saved.")