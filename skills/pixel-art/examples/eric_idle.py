"""Worked example: Eric from Eastward, a kid, front idle on a 32x48 canvas, rebuilt pixel for pixel.
Kid proportions: 38 px tall, and the head with its hair is 18 of them; the body is a short block on two-pixel
legs. He stands square about x = 16, and each shape is written for the screen-left side and mirrored.
Three casts place the game's own contact shadows: the fringe on the forehead, the head on the neck and collar,
the shirt on the shorts. Regions are flat masses, and the hand pass draws the rest."""
from kit.construct import Figure, Light, Region, block_pair, centred, pair

CX = 16
# Row budget (canvas y): hair and head 8-25, neck and shirt 26-36, shorts 37-39, legs 40-42, shoes 43-45.
# The arms end at y = 38, level with the shorts.

# The shared Eastward colors keep their letters from styles/eastward_palette.json: ink, shadow brown, ochre, skin
# and its shadow, brown-orange. "A" is the second shared skin color, used here for the arms. His own are the eyes,
# the shirt's two greens, its stripe and the shorts.
PALETTE = {
    "o": "#281913",
    "b": "#5b3711", "y": "#ca7819",
    "S": "#f9d18c", "A": "#fad388", "s": "#d16b46",
    "E": "#597b73",
    "G": "#8bad4f", "g": "#686028", "X": "#efe7d3",
    "D": "#709090",
    "n": "#ae702d",
}

# material -> (hi, base, shade, deep). shade is what a cast turns the base into; deep is the color of a "shade"
# line drawn on that material.
RAMPS = {
    "hair": ("y", "y", "b", "o"), "skin": ("S", "S", "s", "b"), "arm": ("A", "A", "s", "b"),
    "shirt": ("G", "G", "g", "b"), "stripe": ("X", "X", "X", "b"), "shorts": ("D", "D", "b", "b"),
    "shoe": ("n", "n", "n", "o"),
}

# Shapes cover the pixels inside the outline; the kit inks the ring around their union.
HAIR = centred(((13, 9), (13, 10), (11, 10), (10, 11), (10, 15)), CX)
FRINGE = ((11, 12), (21, 12), (21, 14), (11, 14))
HEAD = centred(((11, 15), (11, 18), (8, 18), (8, 20), (10, 20), (10, 22), (11, 23), (12, 24), (13, 25)), CX)
NECK = ((14, 26), (18, 26), (18, 28), (14, 28))
SHIRT = centred(((11, 26), (10, 27), (9, 28), (9, 30), (10, 31), (10, 35), (11, 36)), CX)
STRIPE = ((11, 32), (21, 32), (21, 33), (11, 33))
ARM = ((8, 31), (9, 31), (9, 35), (10, 36), (10, 37), (9, 37), (8, 36))
SHORTS = ((11, 37), (21, 37), (20, 38), (20, 39), (17, 39), (17, 38), (15, 38), (15, 39), (12, 39), (12, 38))
LEG = ((13, 40), (14, 40), (14, 42), (13, 42))
SHOE = ((13, 43), (14, 43), (13, 44), (12, 44))

REGIONS = [
    Region("hair", "hair", HAIR, groups=("hair",)),
    *pair("leg", "skin", LEG, CX),
    # The shorts' "shade" line is the shadow they drop on the legs.
    Region("shorts", "shorts", SHORTS, line="shade"),
    # No line where the shirt meets the shorts: its cast darkens their top row instead.
    Region("shirt", "shirt", SHIRT, line=None, cast=(0, 1), groups=("shirt",)),
    Region("stripe", "stripe", STRIPE, line=None, groups=("shirt",)),
    Region("neck", "skin", NECK, line="ink"),
    # The head, ears included. Its "shade" line is the chin's edge on the neck; its cast shades the neck and the
    # collar beside it.
    Region("head", "skin", HEAD, line=None, line_vs=(("neck", "shade"),), cast=(0, 3)),
    # The fringe overhangs the forehead: same hair, listed after the head so that its cast is the shadow band
    # across the brow.
    Region("fringe", "hair", FRINGE, line=None, cast=(0, 3), groups=("hair",)),
    # Arms hang in front of the body: their ink line separates them from the shirt and the shorts.
    *pair("arm", "arm", ARM, CX, line="ink"),
    *pair("shoe", "shoe", SHOE, CX, line=None),
]

# Hand pass: what the build can't know. "_" keeps the built pixel; every letter is a mark drawn by hand, in a
# window of at most 16x16.
# Brown clump lines, the fringe's jagged ink edge, and the forehead showing through its gap.
HAIR = """
    ____b__b___
    _b_b__bb_b_
    b__o_osb__b
    b__o_osso_b
    ooosoossoob
"""
# Screen-left half of the face, centre column included: a brow, the ear with its inner shadow, a one-pixel eye,
# the nose's side line and shadow, the mouth and the jaw's corner.
FACE_L = """
    _____oo__
    _________
    sso_E_sbb
    sb____b__
    ss____bs_
    _________
    _________
    _______bb
    _________
    _____s___
"""
# The collar's shaded outer edge, the neck opening's corner and lower line, and the sleeve seam.
SHIRT_L = """
    _gg_____
    g___b___
    __b__bbb
    G_b_____
"""

OPS: list[tuple] = [
    ("block", (11, 10), HAIR),
    *block_pair((8, 16), FACE_L, CX),
    *block_pair((9, 27), SHIRT_L, CX),
    ("line", "b", [(15, 38), (17, 38)]),  # the shadow between the shorts' legs
    ("px", "o", [(13, 40), (19, 40)]),  # the shorts' outer corners on the legs
    ("px", "b", [(15, 40), (17, 40)]),  # the legs' inner outline, brown instead of ink under the shorts
    ("px", "o", [(15, 44), (17, 44), (11, 45), (21, 45)]),  # shoe corners the ring can't reach
]


def figure() -> Figure:
    # Lit from the front and a little above, with no roll-off: every region stays one flat tone.
    return Figure((32, 48), PALETTE, RAMPS, REGIONS, Light(direction=(0, -0.7, 0.9), global_weight=0, local_weight=0), OPS)
