"""Worked example: Lawrence from Eastward, front idle on a 48x64 canvas, rebuilt pixel for pixel.
He stands square: the silhouette is a mirror image about x = 24 (level shoulders, both arms hanging, feet alike),
so every shape is written for the screen-left side and mirrored. The side parting, the only one-sided thing about
him, lives inside the silhouette.
Eastward shades with flat fills plus a few drawn shadow shapes, so the regions here are flat masses and the light
only casts the head's shadow on the neck. Everything else is the hand pass: the face, the hands and each fold.
Shows region order, mirrored shapes, groups, line policies, a cast and the hand pass."""
from kit.construct import Figure, Light, Region, block_pair, centred, pair

CX = 24  # centre line: x_right = 2 * CX - x_left
# Row budget (canvas y): head 8-29 with the mustache, shirt 30-45, belt 46-47, trousers 48-57, shoes 58-60.
# The hands hang to y = 53, level with the top of the thighs.

# The shared Eastward colors keep their letters from styles/eastward_palette.json: ink, skin and its shadow, ochre,
# the muted grey and violet, shadow brown. His own are the shirt, the shoes and the buckle.
PALETTE = {
    "o": "#271913",
    "S": "#f9d18c", "s": "#d36d45", "y": "#ca7819",
    "g": "#625847", "u": "#686090", "b": "#5a3611",
    "C": "#91c7be", "c": "#5e7c84",
    "L": "#b07a49",
    "X": "#efe7d3",
}

# material -> (hi, base, shade, deep). hi == base: no material here gets a highlight. deep is the color of a
# "shade" line drawn on that material.
RAMPS = {
    "skin": ("S", "S", "s", "b"), "hair": ("g", "g", "b", "b"), "shirt": ("C", "C", "c", "b"),
    "leather": ("b", "b", "b", "o"), "metal": ("X", "X", "X", "X"), "pants": ("u", "u", "b", "b"),
    "shoe": ("L", "L", "b", "b"),
}


# Shapes cover the pixels inside the outline; the kit inks the ring around their union.
HAIR = centred(((21, 9), (21, 10), (19, 10), (18, 11), (18, 12), (17, 13), (17, 16), (18, 17)), CX)
HEAD = ((26, 9), (27, 9), (28, 10), (29, 11), (29, 17), (30, 18), (30, 20), (28, 20), (28, 21), (27, 22), (27, 23),
        (28, 24), (28, 28), (27, 29), (21, 29), (20, 28), (20, 24), (21, 23), (21, 22), (20, 21), (20, 20), (18, 20),
        (18, 18), (19, 17), (19, 13), (23, 13), (24, 12), (25, 11), (26, 10))
MUSTACHE = centred(((21, 23), (20, 24), (20, 25)), CX)
NECK = centred(((21, 30), (21, 31), (22, 32), (23, 33)), CX)
SHIRT = centred(((20, 31), (19, 32), (18, 33), (17, 34), (17, 35), (16, 36), (16, 40), (15, 41), (14, 42), (14, 45)), CX)
BELT = ((18, 46), (30, 46), (30, 47), (18, 47))
BUCKLE = ((23, 46), (25, 46), (25, 47), (23, 47))
HIPS = ((18, 48), (30, 48), (30, 50), (18, 50))
LEG = ((19, 51), (22, 51), (21, 52), (21, 57), (20, 57), (20, 52))
SHOE = ((19, 58), (21, 58), (21, 59), (18, 59))
HAND = ((15, 46), (17, 46), (17, 51), (16, 52), (14, 52), (14, 49), (15, 48))

REGIONS = [
    Region("hair", "hair", HAIR),
    Region("shirt", "shirt", SHIRT),
    # The neck sits in front of the shirt: its "shade" line draws the open collar's V on the shirt.
    Region("neck", "skin", NECK, line="shade"),
    # One head, forehead to chin; the parting leaves the hair showing on the screen-left side. Its "shade" line
    # is the chin's edge on the neck, and its cast puts the whole neck in shadow.
    Region("head", "skin", HEAD, line=None, line_vs=(("neck", "shade"),), cast=(0, 4)),
    Region("mustache", "hair", MUSTACHE, line=None),
    Region("belt", "leather", BELT, line=None),
    Region("hips", "pants", HIPS, line=None, groups=("pants",)),
    *pair("leg", "pants", LEG, CX, line=None, groups=("pants",)),
    *pair("shoe", "shoe", SHOE, CX, line="shade"),
    # The buckle is inked against the belt and shaded against the cloth above and below it.
    Region("buckle", "metal", BUCKLE, line="shade", line_vs=(("belt", "ink"),)),
    # Hands hang in front of the hips: inked against them, shaded against the cuffs.
    *pair("hand", "skin", HAND, CX, line="ink", line_vs=(("shirt", "shade"),)),
]

# Hand pass: what the build can't know. "_" keeps the built pixel; every letter is a mark drawn by hand, in a
# window of at most 16x16 (print one with render_figure.py --window, rewrite it, paste it back).
# Hair clumps and the parting, the eyes in a band of skin shadow, the nose and the ears. Some letters sit on the
# outline itself ("b" beside the hair and jaw, "s" beside the chin): the game's outline is not ink everywhere.
FACE = """
    _____b__oss____
    _b__bb__osss_b_
    b_oob__o____s_b
    b_o___b_______b
    __sboo_________
    _______________
    ___bbsssssbb___
    __bbsssssssbb__
    __bssbsssbssb__
    _yo_bsssssb_oy_
    _yb___bbb___by_
    _yb__bsssb__by_
    __b__bsssb__b__
    ___s_______s___
"""
# The mustache's lower edge with the mouth between its tips, and the shadow under the lip.
MUSTACHE = """
    _oobbboo_
    _oss___o_
    ___sss___
    _________
    s_______s
"""
# Screen-left half of the shirt, centre column included: the collar wing, the placket, two shadow shapes under
# the arm, the line where the forearm overlaps the body, and the cuff.
SHIRT_L = """
    ______o____
    ______o____
    ____o__b___
    ____o______
    _____b__oob
    ______bbocb
    _______cccb
    _____c__ccb
    ____cc____b
    ____c_____c
    _bc_b_____c
    b___b_____c
    ____b_____c
    ____ob____b
    o__Coobbo__
"""
# A mitten: the wrist in the cuff's shadow, a finger line and a shadowed underside.
HAND_L = """
    _ssb
    _sss
    s___
    ____
    __s_
    s_b_
    ssb_
"""
# The shirt's shadow on the belt, then the trouser leg's inner shadow down to the knee.
TROUSERS_L = """
    ccc_
    ____
    b__o
    ____
    ____
    b__b
    __bb
    ___b
"""


OPS: list[tuple] = [
    ("block", (17, 9), FACE),
    ("block", (20, 25), MUSTACHE),
    *block_pair((14, 31), SHIRT_L, CX),
    *block_pair((14, 46), HAND_L, CX),
    *block_pair((19, 46), TROUSERS_L, CX),
    ("px", "b", [(21, 59), (27, 59)]),  # the shoes' inner shadow
    ("px", "o", [(17, 60), (31, 60)]),  # sole corners the ring can't reach
]


def figure() -> Figure:
    # Lit from the front and a little above, with no roll-off: every region stays one flat tone.
    return Figure((48, 64), PALETTE, RAMPS, REGIONS, Light(direction=(0, -0.7, 0.9), global_weight=0, local_weight=0), OPS)
