"""Worked example: Sayuri from Eastward, front idle on a 48x64 canvas, rebuilt pixel for pixel.
A slim woman with two big hair buns, an off-shoulder blouse and a narrow dress. She is 30 px wide, an even number,
so her centre line runs between two pixel columns (x = 23.5) and x_right = 47 - x_left. She stands square, as most
idle sprites in the game do, and each shape is written for the screen-left side and mirrored.
The hair is one mass wider than the body; the dress is a straight column whose hem dips toward the viewer; the
legs are single pixel columns. Regions are flat masses, two casts place the game's own contact shadows, and the
hand pass draws the rest."""
from kit.construct import Figure, Light, Region, block_pair, centred, pair

CX = 23.5
# Row budget (canvas y): hair and head 8-31, shoulders and blouse 31-41, dress 39-52, legs 53-57, shoes 58-60.
# The hands hang to y = 51, beside the hem.

# The shared Eastward colors keep their letters from styles/eastward_palette.json: ink, shadow brown, a skin
# variant and its shadow, cream, sage and ochre. Her own are the hair's lighter brown, the blouse, the dress and
# the shoes.
PALETTE = {
    "o": "#281913",
    "b": "#5a3611", "h": "#95633d",
    "K": "#f9c972", "s": "#d16b46",
    "W": "#f9e9a5", "e": "#7c8775",
    "y": "#f8b838",
    "B": "#dee0a0",
    "P": "#c56593",
    "L": "#836d3f",
}

# material -> (hi, base, shade, deep). Her hair's base is the shadow brown itself, so a cast leaves it unchanged.
RAMPS = {
    "hair": ("h", "b", "b", "o"), "skin": ("K", "K", "s", "b"), "gold": ("y", "y", "y", "y"),
    "blouse": ("B", "B", "B", "b"), "dress": ("P", "P", "b", "b"), "stocking": ("b", "b", "b", "o"),
    "shoe": ("L", "L", "L", "o"),
}

# Shapes cover the pixels inside the outline; the kit inks the ring around their union.
HAIR = centred(((21, 9), (21, 10), (19, 10), (18, 11), (18, 14), (17, 15), (16, 16), (16, 17), (14, 17), (14, 18),
                (12, 18), (11, 19), (11, 20), (10, 21), (10, 26), (11, 27), (11, 28), (12, 29), (16, 29), (16, 30),
                (18, 30), (18, 31)), CX)
FACE = centred(((23, 13), (22, 14), (22, 15), (20, 15), (20, 16), (18, 16), (18, 22), (19, 23), (20, 24), (20, 27),
                (21, 28), (22, 29)), CX)
EARRING = ((16, 24), (17, 24), (17, 27), (16, 27))
ARM = ((15, 42), (18, 42), (18, 50), (15, 50), (14, 49), (14, 48), (15, 47), (16, 46), (16, 43))
BLOUSE = centred(((17, 35), (16, 36), (16, 39), (15, 40), (15, 41)), CX)
CHEST = centred(((22, 31), (21, 32), (21, 33), (19, 33), (18, 34), (19, 35), (21, 35), (21, 36)), CX)
DRESS = ((19, 40), (28, 40), (28, 49), (19, 49))
HEM = ((19, 50), (28, 50), (28, 51), (27, 52), (20, 52), (19, 51))
LEG = ((21, 54), (21, 57), (21, 57), (21, 54))
SHOE = ((19, 58), (21, 58), (20, 59), (18, 59))

ARMS = (("arm_l", "ink"), ("arm_r", "ink"))

REGIONS = [
    Region("hair", "hair", HAIR),
    *pair("earring", "gold", EARRING, CX, line=None),
    # Bare arms, listed before the clothes that overlap them: the sleeve and the dress ink their edges on the arm.
    *pair("arm", "skin", ARM, CX),
    # The blouse's cast is the shadow the puffed sleeve drops on the upper arm.
    Region("blouse", "blouse", BLOUSE, line="ink", cast=(0, 2)),
    # Shoulders and neck in front of the blouse: their ink line is the neckline.
    Region("chest", "skin", CHEST, line="ink"),
    # The face is inked against the hair around it, and its cast is the shadow under the chin.
    Region("face", "skin", FACE, line="ink", cast=(0, 4)),
    Region("dress", "dress", DRESS, line=None, line_vs=ARMS),
    Region("hem", "blouse", HEM, line=None, line_vs=ARMS),
    *pair("leg", "stocking", LEG, CX, line=None),
    *pair("shoe", "shoe", SHOE, CX, line=None),
]

# Hand pass: what the build can't know. "_" keeps the built pixel; every letter is a mark drawn by hand, in a
# window of at most 16x16.
# The hair's top: highlight clumps on the screen-left side, the shadowed parting, and the fringe's edge in brown.
HAIR_TOP = """
    ___h__h_______
    __hhhhh__hh___
    _hhhhh____hh__
    _h____ss______
    _____ssss_____
    _bb________bb_
    b__bbb__bbb__b
"""
# Brows and lashes in brown, two-pixel eyes (cream and sage), the nose as one shadow line, the mouth, the jaw's
# shadow beside each cheek, and the hair's strands down to the neck.
FACE = """
    _____ssb_ss_____
    ___sbbsb_sbbs___
    o__bbb_s__bbb__o
    sb__We_s__eW__bs
    sb__We_b__eW__bs
    sb_____bb_____bs
    _ob__________bo_
    ___b_s____s_b___
    _____sbbbbs_____
    ______ssss______
    ________________
    ________________
    o___ob____bo___o
    o___oobbbboo___o
    ____o______o____
"""
# One highlight shape on each bun and the ink line where it meets the cheek.
BUN_L = """
    __hhhh
    _hhhh_
    _hhhho
    _hhhho
    ___hho
    _____o
"""
# The sleeve's brown top edge, its pink trim, the dress's straps and the line between sleeve and bodice.
SLEEVE_L = """
    _b____
    b_____
    b_____
    ____b_
    ___bPP
    PP_b__
    ___b__
"""
# Three folds across the lap and the hem's turned-up corners.
SKIRT = """
    b_____b__b
    bb__bb__bb
    __________
    __________
    __________
    B________B
"""
# The forearm's shadow under the sleeve, then the fingers.
HAND_L = """
    ____s_
    ______
    ______
    ______
    ___o__
    ___oo_
    o___o_
"""

OPS: list[tuple] = [
    ("block", (17, 10), HAIR_TOP),
    ("block", (16, 17), FACE),
    *block_pair((10, 18), BUN_L, CX),
    ("px", "h", [(35, 22)]),  # the one highlight pixel the screen-right bun has to itself
    ("px", "o", [(15, 29), (32, 29)]),  # the buns' lowest strands
    *block_pair((15, 35), SLEEVE_L, CX),
    ("block", (19, 44), SKIRT),
    *block_pair((13, 44), HAND_L, CX),
    ("px", "o", [(22, 59), (25, 59), (17, 60), (30, 60)]),  # shoe corners the ring can't reach
]


def figure() -> Figure:
    # Lit from the front and a little above, with no roll-off: every region stays one flat tone.
    return Figure((48, 64), PALETTE, RAMPS, REGIONS, Light(direction=(0, -0.7, 0.9), global_weight=0, local_weight=0), OPS)
