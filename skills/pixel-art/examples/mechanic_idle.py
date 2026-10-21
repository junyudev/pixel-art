"""Worked example: young mechanic, Eastward adult scale, front idle on a 48x64 canvas.
Contrapposto: weight on the screen-left leg, hips and shoulders counter-tilt by 1px. The arms do different
things (one hangs with the wrench, one hand on the hip) so the pose has attitude; the torso stays narrow so the
whole figure is ~32 px wide. The face uses bold, ink-free features (eyes are the only ink).
Shows region order, groups (no seams inside one form), tilts, casts, line policies and a hand pass."""
from kit.construct import Figure, Light, Region, arc_pts, band, limb
from kit.pixelkit import Shadow

# Shared Eastward colors (styles/eastward_palette.json) for ink, skin, shadow brown and cream, plus a few own colors.
# Most materials: base + one shadow; a highlight only on hair.
PALETTE = {
    "o": "#281913",
    "S": "#f9d18c", "s": "#d36d45",
    "H": "#f08c4f", "R": "#d4553a", "r": "#8e2f38",
    "w": "#e2d6ba", "v": "#a3968a",
    "C": "#3f8a84", "c": "#2a5562",
    "B": "#6a4c44", "b": "#5b3711",
    "X": "#eef0e8", "x": "#9aa3ad",
    "A": "#f9e9a5",
}

# material -> (hi, base, shade, deep). hi == base where a material gets no highlight.
RAMPS = {
    "skin": ("S", "S", "s", "s"), "hair": ("H", "R", "r", "r"), "tank": ("w", "w", "v", "v"),
    "pants": ("C", "C", "c", "c"), "leather": ("B", "B", "b", "b"), "metal": ("X", "x", "x", "x"),
    "canvas": ("A", "A", "v", "v"), "red": ("R", "R", "r", "r"),
}

# Gesture joints (canvas px): weight on the screen-left leg, right hand on the hip, left hand holds the wrench.
SHOULDER_L, ELBOW_L, WRIST_L = (17, 31), (15, 38), (15, 43)
SHOULDER_R, ELBOW_R, WRIST_R = (31, 31), (35, 37), (31, 42)
HIP_L, KNEE_L, ANKLE_L = (21, 46), (21, 52), (21, 56)
HIP_R, KNEE_R, ANKLE_R = (27, 46), (27, 52), (27, 56)

HAIR = ("hair",)
ARM_L, ARM_R, TORSO = ("arm_l",), ("arm_r",), ("torso",)

REGIONS = [
    Region("ponytail", "hair", ((28, 11), (31, 10), (34, 10), (36, 13), (36, 17), (34, 21), (33, 24), (32, 21), (31, 17), (29, 14)), groups=HAIR, tilt=(0.35, 0.1)),
    Region("hair_back", "hair", ((15, 25), (14, 18), (16, 14), (18, 12), (22, 10), (26, 10), (30, 12), (33, 15), (34, 19), (33, 25), (30, 25), (30, 20), (18, 20), (18, 25)), groups=HAIR, tilt=(0, -0.2)),
    # Body from gesture joints. Limbs are slim and taper (limb(start, end, w_start, w_end)); seen from slightly
    # above, the figure is widest across the shoulders/hands band and narrows to small feet close together.
    Region("thigh_r", "pants", limb(HIP_R, KNEE_R, 5, 4), line=None, groups=("pants",), tilt=(0.2, 0)),
    Region("shin_r", "pants", limb(KNEE_R, ANKLE_R, 4, 3), line=None, groups=("pants",), tilt=(0.2, 0)),
    Region("thigh_l", "pants", limb(HIP_L, KNEE_L, 5, 4), line=None, groups=("pants",), tilt=(-0.1, 0)),
    Region("shin_l", "pants", limb(KNEE_L, ANKLE_L, 4, 3), line=None, groups=("pants",), tilt=(-0.1, 0)),
    Region("boot_r", "leather", (*arc_pts(25, 29, 55, 1), (29, 59), (28, 60), (26, 60), (25, 59)), line="shade",
           tilt=(0.1, -0.4)),
    Region("boot_l", "leather", (*arc_pts(19, 23, 55, 1), (23, 59), (22, 60), (20, 60), (19, 59)), line="shade",
           tilt=(0, -0.4)),
    Region("hips", "pants", ((18, 43), (30, 44), (30, 48), (18, 47)), line=None, groups=("pants",), volume=0.5),
    Region("torso_skin", "skin", ((16, 31), (20, 29), (28, 29), (32, 30), (32, 34), (16, 34)),
           line=None, groups=("arm_l", "arm_r", "torso", "neck"), tilt=(0, -0.4)),
    Region("neck", "skin", ((21, 25), (27, 25), (27, 30), (21, 30)), line=None, groups=("neck",), volume=0.4),
    # Seen from in front and above, every ring around the body (hem, belt, boot tops, head strap) is an arc
    # that dips toward the viewer: arc_pts / band, never a flat horizontal edge.
    Region("tank", "tank", ((18, 31), (20, 31), (21, 33), (24, 34), (27, 33), (28, 31), (30, 31), (31, 35),
                            (29, 39), *arc_pts(29, 19, 41, 2), (19, 38), (17, 35)), line=None, groups=TORSO),
    Region("belt", "leather", band(19, 29, 41, 2, 2), line="shade", volume=0.3),
    Region("rag", "red", ((20, 43), (22, 43), (22, 47), (21, 48), (20, 47)), line="shade", volume=0.5),
    Region("pouch", "leather", ((25, 44), (28, 45), (28, 48), (25, 48)), line="shade", volume=0.5),
    Region("wrench", "metal", ((14, 46), (15, 46), (15, 50), (17, 50), (17, 54), (16, 54), (16, 52), (13, 52),
                               (13, 54), (12, 54), (12, 50), (14, 50)), volume=0.3),
    Region("arm_l_upper", "skin", limb(SHOULDER_L, ELBOW_L, 4, 3), groups=ARM_L, cast=(1, 1), tilt=(-0.2, 0)),
    Region("arm_l_fore", "skin", limb(ELBOW_L, WRIST_L, 3, 3), groups=ARM_L, cast=(1, 1)),
    Region("glove_l", "canvas", ((13, 43), (17, 43), (17, 46), (16, 47), (14, 47), (13, 46)), groups=ARM_L),
    Region("arm_r_upper", "skin", limb(SHOULDER_R, ELBOW_R, 4, 3), groups=ARM_R, cast=(1, 1), tilt=(0.3, -0.2)),
    Region("arm_r_fore", "skin", limb(ELBOW_R, WRIST_R, 3, 3), groups=ARM_R, tilt=(0.2, 0.3)),
    Region("glove_r", "canvas", ((29, 41), (32, 41), (33, 43), (32, 44), (29, 44)), groups=ARM_R),
    Region("face", "skin", ((18, 18), (30, 18), (30, 23), (28, 26), (26, 27), (22, 27), (20, 26), (18, 23)),
           cast=(1, 2), line_vs=(("hair_back", "shade"),), groups=("neck",)),
    Region("fringe", "hair", ((17, 14), (31, 14), (31, 18), (30, 18), (28, 19), (26, 18), (24, 20), (22, 18), (20, 21), (18, 18), (17, 19)), line="shade", groups=HAIR, cast=(0, 1), tilt=(0, -0.3)),
    Region("strap", "leather", band(15, 33, 14, 2, 1), line="shade", volume=0),
    Region("lens_l", "metal", ((19, 15), (22, 16)), ellipse=True, volume=0.5),
    Region("lens_r", "metal", ((26, 15), (29, 16)), ellipse=True, volume=0.5),
]

# Hand pass: decisions made by eye on the whole canvas. Face and hands are drawn as ("block", ...) windows
# (print the area with render_figure.py --window, rewrite it, paste it back); small marks as px/line ops.
FACE = """
    __rrr___rrr__
    __sossssos___
    ______ss_____
    _RR__bbb__RR_
    _____________
    _____bbb_____
"""

OPS: list[tuple] = [
    ("block", (18, 21), FACE),
    # hair clumps + tie
    ("line", "r", [(21, 12), (18, 14)]), ("line", "r", [(26, 11), (27, 14)]), ("line", "r", [(30, 12), (31, 14)]),
    ("px", "H", [(18, 12), (19, 12), (18, 13), (22, 11), (22, 11), (18, 17), (18, 16)]),
    ("line", "r", [(31, 14), (32, 18)]),
    ("px", "A", [(30, 12), (31, 12)]),
    # tank fold, buckle, pouch flap, knee crease, wrench glint
    ("line", "v", [(22, 37), (23, 39)]),
    ("px", "A", [(23, 43), (24, 43)]),
    ("line", "b", [(25, 46), (28, 46)]), ("px", "A", [(27, 46)]),
    ("px", "c", [(27, 52)]),
    ("line", "X", [(14, 47), (14, 50)]),
]

def figure() -> Figure:
    return Figure((48, 64), PALETTE, RAMPS, REGIONS, Light(), OPS, Shadow(24, 60.5, 8.5, 2.5))
