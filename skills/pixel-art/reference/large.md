# Construct route: sprites over 32 px

## Contents
- How to read this guide
- Why this route
- The camera: in front of the character and above, looking down
- Workflow: style card, study, concepts, stance, construct, light, detail, look, fresh eyes, critique
- Critique checklist
- API (`kit/construct.py`)
- Animation
- Lessons that cost iterations

## How to read this guide

It describes how the game's sprites are built and what went wrong in test runs. Read it as observations and suggestions, not rules. The real sprites are the authority: where a reference, the request or your own eye disagrees with a line here, go with that. Numbers are typical values, not limits.

## Why this route

You draw without seeing, so two things decide quality: **how the figure is built** and **how often you look**.

Three failures this skill exists to prevent:

- **Balloons glued together.** Each part is outlined and shaded on its own. Real pixel art is one form under one light, with lines only where the artist chose them.
- **Noise and plastic.** Too many tones and single-pixel highlights. Real 50 px sprites use about 12–16 colors and big flat shadow shapes.
- **Blown-up icons.** Flat, empty masses with blank faces. This happens when the sprite is planned small and scaled up. Real sprites get their character from 1–3 px marks drawn at full size: features, beard texture, stains, folds.

**Where your strength is.** You draw 16×16 sprites well, because everything fits in one view. A 48×64 sprite is too big to hold at once, but its details live in areas about 16×16 (a face, a hand, a prop). So code builds the figure (shapes, one light, clean ink), and you draw every face, hand and detail as a ≤ 16×16 text window **at full size**. Planning at half size and scaling up was tested, and it produced flat, empty sprites.

Division of labour: **code owns consistency** (rasterizing, one light, clean ink). **You own intent**: shape design, where lines go, and every face, hand, clump and fold pixel.

## The camera: in front of the character and above, looking down

**This is the idea that matters most.** The game's sprites are not front elevations. They read as 3D volumes seen from in front and above:
- **Volumes:** the torso, limbs and skirt are cylinders or cones, and the head is an egg.
- **A horizontal ring around a form is usually drawn as the near half of an ellipse.** That covers skirt, coat and apron hems, belts and waistbands, cuffs, collars and necklines, hat bands and brims, boot tops, and bucket rims. It tends to **dip toward the viewer in the middle and rise at the sides.**
  - Sag is about 15 % of the ring's width: 1 px for 4–7 px rings, 2 px for 8–14, and 3 px for 15+.
  - `arc_pts()` and `band()` draw these. The game has flat hems too, but a figure whose every hem is a ruler line reads as a front view.
- **Tops show, bottoms hide.** The crown of the head or hat, the top plane of the shoulders, the inside of a bucket (an ellipse) and the tops of the shoes usually show; soles usually don't.
- **Skirt and coat sides** flare and curve, and their bottom corners round up.
- **Shading follows the volume.** Each cylinder has one shadow side. Shadows of bands and hems follow their arcs.
- **Check `flat_h`**, the share of interior horizontal boundaries that are straight runs of 6 px or more. The reference median is 0.28 and nine in ten real sprites are under 0.38; front-view test sprites scored up to 0.57.

Setup is in SKILL.md. Run tools from the skill folder (they add it to `sys.path`), or copy `kit/` and `tools/` into your project.

## Workflow

1. **Style card.** If `styles/<style>.md` exists, read it.
   - Otherwise, with clean sprites: run `tools/style_stats.py` over them for the numbers.
   - With screenshots only: `tools/native.py` and `tools/zoom.py` measure sizes. Their colors and shading are unreliable, because screenshots carry engine grading.
   - Write a card with the same sections as `styles/eastward.md`.
   - With no references at all: write a short card from the request (view, figure height on the canvas, color budget ≤ 16, outline, light). `styles/eastward.md` is a worked example of a top-down 3/4 RPG style; borrow its structure rules when the user wants that look.
2. **Study real sprites as text** (with no references, use the Eastward anatomy and head files below as your examples of how faces and hands are built).
   - Read `styles/<game>_anatomy.md` if it exists: face, hand and leg grammar with real snippets.
   - Read `styles/<game>_heads.md` and **pick a head template**: the real head closest to your character's type (woman, old or bearded man, big man, kid). You will adapt its structure in step 7.
   - Then pick 3–6 sprites close to your character's build, age and role. From a sprite atlas, cut one out with `tools/refs.py extract ATLAS.png ATLAS.json NAME ref.png`. Then `tools/refs.py text ref.png [x y w h] --map styles/<game>_palette.json` prints it in the medium you draw in. The style's shared colors always print as the same letters.
   - Write down:
     - the row budget (head, torso and leg rows);
     - how eyes, nose, mouth, beard and hands are drawn, pixel by pixel;
     - where the shadow shapes sit;
     - how many colors are used.
3. **Concepts, then brief.**
   - **Concepts:** it helps to write 3 genuinely different concepts in one line each: body type (stout, lanky, hunched, top-heavy), age cues, silhouette hook, and how the prop is held. Your first idea is the one every other run also has, so the most specific concept is usually the better pick.
   - **Brief, 4 lines:** silhouette hook, one caricature feature, 3–5 materials plus one accent, one story detail. Add one line on **how the age reads**, using the marks from the anatomy grammar. An adult with a round face, a closed-eye grin and no marks reads as a child.
   - **Palette:** this is a good point to write it, around the card's budget (Eastward sprites use 10–16 colors including ink).
     - If `styles/<game>_palette.json` exists, start from its shared colors: ink, skin and skin shadow, shadow brown, cream. Then add the character's own colors, typically 3–6.
     - Most materials in the game have a base and a shadow only (`hi == base` in the ramp); a highlight appears on 1–3 materials.
     - It helps to plan values so that dark materials don't all land in one horizontal band (mud).
4. **Stance and proportions first.** Writing joint coordinates in a comment before any shape helps: the centre line, then head, shoulders, elbows, wrists, hips, knees, ankles.
   - **Pixel numbers in this step are for Eastward-scale figures** (adults about 52 px tall on a 48×64 canvas). Scale them to your figure height; keep the ratios.
   - **Seen from slightly above.** Top-down RPG cameras look down a little (Eastward's does), and the sprites keep that.
     - **Head:** the crown (hair or cap) takes the upper ~40 % of the head, and the face sits low in it, with the eyes about 55–60 % of the way down.
     - **Shoulders:** they show their top plane (a lit band), and the collar is seen from above.
     - **Widths:** the figure is widest across the shoulder-to-hands band, at about 70 % of its height, then narrows down to **small feet close together**: each 3–4 px, with the toes' tops showing.
     `head_w`, `shoulder_w` and `feet_w` in the fingerprint are this width profile, and the style card has the reference medians. They move with the character (a tall head or a hat lowers `shoulder_w`, a robe raises `feet_w`), so compare with references of the same build. A barrel that stays wide down to big boots reads flat.
   - **Realistic limbs, not cylinders.** `limb(start, end, w_start, w_end)` draws a tapering limb.
     - Average adults: arms 3–4 px tapering to 2–3, and legs 4–5 tapering to 3. Burly characters have thicker ones.
     - Hands are small (3–4 px) and hang at hip or upper-thigh height. Legs are long enough to show knees (adults: ≈ 20–28 % of height).
     - A limb usually has one shadow edge. A highlight stripe down the middle makes it read as a tube.
   - **Stance: most idle sprites in the game stand square.** Shoulders and hips are level, both arms hang alike and the feet are at the same height, so the silhouette is close to a mirror image about its centre line. `mirror` measures this as the share of silhouette pixels with no mirror partner: the reference median is 0.01. Writing a shape for one side and mirroring it with `pair`, `centred` and `block_pair` is an easy way to get there.
     - Asymmetry in the game comes from the character: a held prop, a pose such as crossed arms or a hand on the hip, or hair, a hat or a bag worn to one side. About a quarter of the references have `mirror` above 0.04, mostly for one of these reasons. Use it when the request or your concept calls for it.
     - A plain standing figure rarely has a tilted skeleton. At this size a shoulder 1–2 px lower, a leaning head or staggered feet tend to read as a crooked drawing rather than as attitude.
     - Small differences inside the silhouette are normal: a parting, a fold, a pocket.
     - Arms sit close to the body and overlap the torso edge.
   - **Width:** the reference medians are 27 px for adults and 24 for kids. Most adult torsos stay under about 32 px, or 40 with a flared elbow or a held prop.
   - **Kid height:** usually 35–40 px.
   - **What makes a figure read as an adult rather than a child:**
     - shoulders 2+ px wider than the head on each side;
     - a collar or neckline under the chin;
     - legs or knees visible between the hem and the shoes;
     - a head of about 33–42 % of the height (stout or bearded characters go up to 45 %).
     A big head on a small body with no legs reads as a child.
5. **Construct** a `Figure` from `Region` polygons, listed back to front (API below).
   - **Shape design:**
     - Straight edges against curves.
     - Deliberate corners at shoulders, jaw, elbows and boots.
     - Limbs taper; nothing is a uniform capsule.
     - The silhouette is usually close to symmetric. What breaks the symmetry is something the character has or does.
     - Legs usually show below a garment: two separate feet or boots, 3–5 px each, with a sole row, a gap or an ink line between them, normally at the same height under the hips. A hem sitting on boot slabs reads as a box.
     - **Clothes wrap a body; they are not pasted panels.**
       - Sleeves overlap the torso edge.
       - Straps, belts and hems curve with the form, dipping 1 px at the middle or the sides.
       - The garment's silhouette bends at the waist, hips and knees.
       - Long straight contours are mostly hems and soles. Elsewhere a fold, notch, clump or taper keeps a contour from looking ruler-drawn. See `straight` in the fingerprint (reference median 0.19).
   - **`groups`:** regions that form one continuous form share a group (torso skin with both upper arms, hips with legs, all hair parts). No line is drawn inside a group, which removes ball-joint seams.
   - **`line`:**
     - `"ink"` where one form overlaps another (arm over torso, chin over neck).
     - `"shade"` for details (belt, pouch, fringe, boots over trousers).
     - `None` for pieces of the same fabric.
6. **Light.** One `Light` for the whole figure.
   - Per region, set:
     - `tilt`, the way its plane faces: shoulders and hair top `(0,-0.3..-0.4)`, right-side pieces `(+0.2..0.35, …)`;
     - `volume`: 0 for flat panels, 1 for round forms;
     - `cast`: head `(1,2)`, arms `(1,1)`, fringe `(0,1)`.
   - Check the per-region stats. A front-facing region with more than 60 % shade has the wrong tilt.
   - The examples' light is flat. They reproduce real sprites, whose shadows are drawn shapes: the contact shadows come from `cast`, and the rest are in the hand pass.
7. **Draw the detail at full size. Most loops go here.**
   - **Face and hands as windows.** `render_figure.py fig.py out/ name --window x y w h` prints that area as text with a ruler.
     - Rewrite it as a `("block", (x, y), """rows""")` op: `_` keeps a pixel, `.` erases one.
     - Draw it like the faces and hands you studied in step 2.
     - **Head from the template.** Your template's structure is a good starting point; from there make it your own character:
       - **Silhouette bumps:** ears (1–2 px, with a skin-shadow inner edge) unless hair covers them, plus jowls, hair tufts and the hat brim. A smooth disc or box head reads as a mask.
       - **Faces in the game are carved more than decorated.** The marks that do it, not all of them on every face:
         - a shadow side, 2–3 columns away from the light;
         - a shadow band under the hair, hat or scarf;
         - an **eye-socket band** of skin shadow (or the cool violet) around the eyes, merging into the brows;
         - a nose shape with a dark underside;
         - shadow under the lower lip and under the chin or jaw.
       - Where cool violet is used, it sits **in the socket band** above and around the eyes. Under the eyes it reads as bruises.
       - Freckles and blush read best folded into the cheek's shadow shape.
     - **Bold features.** The references' features are bigger and darker than you expect.
       - The nose is a 2–4 px shape, with skin shadow and a shadow-brown underside.
       - Brows are 2–4 px.
       - The mouth is 2–4 px.
       - The cheek and jaw masses are skin-shadow shapes.
       Compare your head row against theirs on the critique sheet. Small features on an empty skin slab is the most repeated "generic face" complaint.
     - **Blush and freckles** are usually one flat shape per cheek. Scattered dots read as a rash or noise.
     - **Face grammar:**
       - Ink is rare inside the face: mostly 1-pixel eyes, sometimes the edge of a mustache or a strand of hair.
       - Mouth, brows, nose underside and age lines are the shadow brown (or your darkest skin step). Nose, sockets, cheeks and jaw are skin-shadow shapes.
       - The chin usually casts a shadow on the neck.
       - **Mouth:** a skin row between the nose's underside and the mouth keeps the two apart.
         - Women and kids often have a short mouth (2–3 px), in deep red-brown or lip color.
         - An open mouth is a filled dark shape with no ring.
         - A dark bar or ring right under the nose reads as a mustache or goatee. Judges flagged this in 4 runs.
       - **Hair under a scarf or cap** joins the face edge as one clump. Separately outlined puffs at the ears read as headphones.
     - **Hands** are inked mittens with a shadowed underside.
     - Blocks of about 16×16 or smaller, one feature area at a time, are the easiest to get right.
   - **Then smaller marks** with `px` and `line` ops: hair clumps, folds, stains, buckles, glints, and line breaks where a contour should open.
   - **Clothes are layered shapes, not slabs.**
     - A large garment typically has 2–4 tapered fold or shadow shapes (2–6 px) that start at a joint, strap or waist.
     - Cuffs, collar, hem and belt are often separate bands.
     - Gloss is one or two strokes.
     - Big garments are mostly in the shared muted cloth colors. A large saturated area tends to pop out of the scene.
   - **Variants.** For the face, the prop and the biggest garment, it pays to draw 2–3 alternatives (for example, separate block constants switched by a flag). Render each one, put them all on one critique sheet with the references, and keep the version that reads best at 1×. Note why you chose it. Runs that did this fixed their worst misreads.
   - **Colors and single pixels.** Staying within your palette keeps the sprite coherent, and an isolated pixel works when it is a deliberate one (an eye, a glint, a button).
     - Sheen, wetness, stitches and texture read best as one shape or one line. Judges called scattered specks "noise".
   - **Props:** it helps to name the two features that make each prop read and give each about 2 px or more.
     - A fish reads by its eye and a head with a mouth, then a tail.
     - Boots read by a top cuff and a sole; without them they look like trousers.
     - A bucket reads by a rim ellipse and a gripped handle.
     - Rope reads as a few thick coils rather than a woven pattern.
   - **Prop placement:** the most recognizable part is best kept visible (a fish's head and eye, a paper's printed face), with the hand gripping the prop. Looking at the prop alone at 1× and asking what else it could be catches misreads. A forked fish tail above a fist read as a wrench 3 times.
8. **Look often**, ideally every loop.
   - `tools/render_figure.py fig.py out/ name --budget 16` prints:
     - bbox and colors used;
     - the fingerprint;
     - **guardrail warnings in both directions** (too noisy *and* too flat or empty), and a note when `mirror` is above 0.04;
     - per-region light stats.
     It also writes the views: 1×, 3×, grid, silhouette, squint, grey and flip.
   - **Critique sheet (worth viewing every loop):** `tools/sheet.py out/sheet.png --ours out/name_1x.png --refs a.png b.png` (or `--atlas ATLAS.png ATLAS.json --names "Ref A" "Ref B"`).
     - Your 3–4 closest references work well.
     - It shows the full sprites at 4×, the **heads at 8× side by side**, and everything at game size.
     - Judge your sprite the way a blind judge will: next to the real ones.
   - `tools/compare.py` does the same for arbitrary crops of screenshots.
   - `tools/scene.py NATIVE x0 y0 x1 y1 out/scene.png --put out/name_1x.png X Y` pastes yours into a real screenshot.
9. **Fresh-eyes check** (after loop 2, and on the final).
   - If you can launch a subagent, give it **only** your 4× PNG (on a neutral background) and ask: "Who is this (gender, age, job)? What is each held item and garment? What looks odd?" Each misread is worth fixing or at least weighing.
   - If you can't, write your own description of the 1× image before looking at your notes. A fresh reader caught the mustache, cleaver and bruise misreads that rules alone did not.
   - "Stiff" or "symmetric" alone is a weak reason to change the stance: a fresh reader shown three real sprites said the same of them.
10. **Critique, then repeat.** Three or more loops is typical. Noting what you changed and why each time helps, and the judge is your eye against the real sprites.
   - **Take guardrail warnings seriously.** The guardrails are the full range of the real sprites, so a warning means no sprite in the game looks like this, and it is nearly always worth fixing. A `mirror` note is information, not a fault: check that the asymmetry is one you chose.
   - Numbers inside the guardrails don't make a sprite good.

## Critique checklist

- [ ] **Silhouette.** As a solid fill, is it recognizable at 1×? Where the two halves differ, is it something the character has or does, rather than a tilted skeleton?
- [ ] **Seams.** Is any part outlined on its own? A ring at shoulders, hips or wrists inside one form is a seam.
- [ ] **Light.** One light across the figure: a big shadow side, no pillow rims on every part, no speckles?
- [ ] **Detail density.** Do the face, hands and clothes have drawn marks like the references, or are they blank fills?
- [ ] **Economy.** Colors within budget, about 2 tones per material, and no `render_figure` warnings?
- [ ] **Proportions.** Height, width and head share inside the card's range? Do both legs and feet show? Do the arms stay close to the body?
- [ ] **Wrapping.** Do clothes overlap and curve around the body, or are they flat panels with ruler edges?
- [ ] **Misreads.** At 1×, could the mouth read as a mustache, hair as headphones, or the prop as a tool?
- [ ] **Heads row.** On the critique sheet, are your features as big, dark and specific as the references'? Does the head have ears or bumps? Is the face carved with a shadow side, a socket band, a nose underside and a chin shadow?
- [ ] **Props.** Does each prop show its two identifying features at 1×?
- [ ] **Camera from above.** Is every hem, belt, cuff, collar and band an arc dipping toward the viewer? Do the tops show (head crown, shoulders, shoe tops, rims)? Is `flat_h` near the references' 0.28?
- [ ] **Perspective and limbs.** Is the figure widest across the shoulders and hands, narrowing to small close feet? Are the limbs slim and tapered, with no tubes or highlight stripes?
- [ ] **Age and character.** Does the face read at the brief's age, and is it a specific person rather than the generic default?
- [ ] **Color world.** Are most pixels the style's shared colors, and are large areas as muted as the references?
- [ ] **Fit.** Next to the real sprites, does it look like the same game?

## API (`kit/construct.py`)

```python
limb(start, end, w_start, w_end)         # tapered limb polygon between two joints, e.g. limb(SHOULDER, ELBOW, 4, 3)
mirror(points, cx)                       # the same points mirrored about x = cx: the twin of a one-sided shape
centred(half, cx)                        # outline of a shape that straddles x = cx, from its screen-left half
pair(name, material, half, cx, **kw)     # two Regions, NAME_l and its mirror twin NAME_r
block_pair((x, y), rows, cx)             # a ("block", ...) op and its mirror twin
arc_pts(x0, x1, y, sag)                  # points of a ring's near half: dips `sag` px toward the viewer at the middle
band(x0, x1, y, thick, sag)              # curved band polygon (belt, cuff, collar, hat band)
Region(name, material, shape,            # shape: polygon ((x, y), ...) in canvas px, vertices inclusive
       line="ink" | "shade" | None,      # policy where this region overlaps regions listed before it
       volume=1.0,                       # edge roll-off strength (0 = flat panel)
       cast=None | (dx, dy),             # contact shadow onto regions listed before it
       ellipse=False,                    # shape = ((x0, y0), (x1, y1)) bounding box
       groups=(),                        # shared group => no line between them
       tilt=(0, 0),                      # plane normal slope: +x faces right, +y faces down
       line_vs=(("lower_region_name", "shade"),))  # per-neighbour policy override
Light(direction=(-0.5, -0.7, 0.9), global_weight=0.35, blur=4.0, local_weight=0.6, bevel=2.5, hi=0.86, shade=0.55)
Figure(size, palette, ramps, regions, light, ops, shadow)
#   palette: key -> "#rrggbb"; "o" is ink.  ramps: material -> (hi, base, shade, deep) keys (hi == base = no highlight)
#   ops: ("block", (x, y), rows) | ("px", key, [(x, y), ...]) | ("line", key, [p0, p1, ...])
#        | ("poly", key, [...]) | ("erase", [...])
#   shadow: kit.pixelkit.Shadow(cx, cy, rx, ry) ground ellipse, or None
```

Your module defines `figure() -> Figure`. Read the examples before writing your own, starting with the one closest to your character's build. Each rebuilds a real Eastward sprite pixel for pixel: flat regions written for one side and mirrored, line policies, casts, and the face, hands and folds drawn as blocks.
- `examples/lawrence_idle.py`: an average man in a shirt and trousers, 48×64.
- `examples/sayuri_idle.py`: a slim woman with big hair and a narrow dress, 48×64, centre line between two columns.
- `examples/eric_idle.py`: a kid, 32×48.

`kit/pixelkit.py` provides FX (`arc()` smears, `Shadow`). It suits effects and tiny props; bodies come out better from `construct`.

## Animation (guidance, not yet battle-tested)

Write regions as a function of a pose dict (joint coordinates) and rebuild every frame, so key poses are redrawn rather than parts slid around. Reuse the same face and hand blocks wherever they don't change.

- Walk: contact → passing (body −1) → mirrored contact → passing.
- Hair and cloth lag one frame.
- Actions: anticipation → one smear frame (≤ 70 ms) → impact (FX + 1–2 px squash) → recover.

## Lessons that cost iterations

- **Asymmetry for its own sake** made every figure crooked. An earlier rule asked for a weight leg, counter-tilted shoulders and hips, and arms doing different things, because a test figure with both arms pulled in had scored lower with blind judges. Drawn from requests with both arms at the sides, it came out as one shoulder 2 px lower, a leaning head and staggered feet (`mirror` 0.04–0.08). The real idle sprites are mirror images: `mirror` is 0 for 31 % of the 220 references and at most 0.04 for 75 %, and most of the rest hold a prop or strike a pose. The earlier example, an invented mechanic with a hand on her hip, had also spread that pose into every early run; the examples are now real sprites.
- **Guardrails cut from the middle of the references** (the p10–p90 band of each number) warned on 85 % of the real adult sprites and 94 % of the kids, and `shoulder_w` alone on 27 % of the adults. Drawers then "fixed" what the game's own art does. The guardrails are now the real sprites' full range, and the width profile is printed without one.
- **Flat buckets with tube limbs** were the verdict on early test runs. Thick constant-width limbs, big boots set wide apart, and a head as wide as the body read as flat. The real sprites are seen from slightly above, with slim tapering limbs that are close to realistic. The width profile (`shoulder_w`, `feet_w`, `head_w`) catches it: a stiff test fishmonger scored `feet_w` 0.82 against a reference median of 0.43.
- **Numbers stopped discriminating** once the economy was right: saturation and largest flat area were inside the reference range even for sprites judges called garish or slab-like. The remaining gaps (bold faces, layered clothes) are caught by looking: the critique sheet and variants.
- **Blind judges' most repeated complaints about adult NPCs:** "reads as a child", "figure stops at boot slabs under the apron", "hands are skin blocks", "bright generic palette". The concept step, the age line, the leg rule, the hand rule and the shared palette exist for these.
- **Ink inside faces** (mouth lines, nose outlines) made faces read as masks. Eastward draws features with shadow brown and skin shadow.
- **Half-size planning plus a pixel-art upscaler** (Scale2x) gave flat, rounded, blank sprites that people rated far worse. The details never come back, and the scaler rounds every edge.
- **Numbers inside the guardrails** did not make a sprite good. They only flag what's clearly wrong.
- **Screenshot colors** (graded, filtered) suggested 3–4 tones per material. Clean sprites use about 2.
- **Lighting from one inflated-silhouette height field** makes faces "look down" into the neck. That's why regions declare `tilt`.
- **Black outlines on every small detail** push dark pixels to about 30 % and read as clutter.
- **Several dark materials at waist height** turn into one muddy band. Make gloves or belts lighter.
- **Round goggle lenses bigger than 4×3** read as giant eyes. Test small props at 1×.
- **Head share above 45 %** on an adult reads as chibi / RPG Maker.
- **Busy textures:** checker rope, camo-like trouser shading and a speckled beard. Each texture reads better as one or two shapes.
- **Misreads that rules alone missed** and a fresh reader caught: a dark bar under the nose plus chin dots read as stubble on a woman; a fish with no eye read as a cleaver; boots with no cuff read as trousers; purple eye bags read as bruises.
