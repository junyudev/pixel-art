# Style card: Eastward (风起之国)

Numbers come from 220 clean 1× character sprites (`tools/style_stats.py` over the sprite atlas) and
measurement of in-game screenshots. Screenshots carry engine grading, bloom and filtering, so take colors
and shading from clean sprites, never from screenshots.

## Targets

These are guardrails, not goals. A sprite outside them is wrong; being inside them doesn't make it good.

| Item | Value (median, p10–p90) |
|---|---|
| Native resolution | 640×360; in-game camera zoom 3.0×/3.3×/3.6× |
| Adult sprite | h 52 (42–59), w 27 (21–41) px |
| Kid sprite | ≈ 35–38 h × 17–27 w (Sam 26×36, Four-Eyes 17×38) |
| Canvas | adult 48×64, kid 32×48 |
| Colors per sprite | 12 (10–16) including ink. Budget: ≤ 16 |
| Tones per material | ≈ 2 (base + shadow). A highlight on 1–3 materials (skin, hair, metal or glossy) |
| Dark pixels (value < 0.25) | 25 % (17–32 %) |
| Silhouette edge inked | 87 % (69–98 %) |
| Interior dark pixels | 10 % (5–16 %): features, overlaps, deep folds |
| Isolated pixels (speckle) | 5 % (4–8 %). Below 4 % usually means faces and clothes lack drawn detail |
| Mean same-color cluster | 6.0 px (4.9–7.7). Above 7.7 means flat, empty "blown-up icon" masses; below 4.9 means noise |
| Head share of height | adults ≈ 33–42 % (slim realistic characters such as Lily, Emma and John: 33–37 %; stout or bearded up to 45 %); kids ≈ 45–50 % |
| Legs | short, ≈ 15–22 % of height |

## Perspective and proportions

The camera looks down slightly, so sprites are top-heavy and taper toward the ground. The width profile below is silhouette width at a fraction of the height, divided by the max width, as a median over 186 adults:

| height | 20 % | 40 % | 55 % | 70 % | 85 % | 95 % |
|---|---|---|---|---|---|---|
| width / max | 0.68 | 0.72 | 0.88 | 1.00 | 0.76 | **0.43** |

- The widest band is shoulders to hanging hands, at about 70 % of the height.
- The feet are small and close together.
- Kids' heads are not the widest part (`head_w` median 0.77).

Every horizontal ring around a form (hem, belt, cuff, collar, hat band, boot top, rim) is an arc that dips toward the viewer, and the tops of forms show. Only 28 % (median) of interior horizontal boundaries are straight runs of 6 px or more (`flat_h`). Front-view drawings score 0.34–0.57.

Limbs are slim and taper: arms 2–3 px inside the outline on average adults (John, Lily, Emma), legs 2–4 px each and long enough to show knees. Hands are 3–4 px and hang at hip or upper-thigh height.

## Shared palette

About 20 colors recur across the cast and cover a median 59 % of each sprite's pixels (30–78 %). They are listed with their roles in `eastward_palette.json`:

- ink `#281913`, in 75 % of sprites;
- shadow brown `#5b3711`;
- skin `#f9d18c` and skin shadow `#d36d45`;
- deep red-brown `#8f482c`;
- cream `#f9e9a5` / `#eedea5`;
- muted cloth: `#625847`, `#686090`, `#7c8775`, `#b98b53`.

Build every palette from these first, then add the character's own 3–6 colors.

Faces, hands and legs: see `eastward_anatomy.md`.

## How the sprites are built

- **Drawn at full size.** Faces, beards, hands, stains and folds are 1–3 px marks placed one by one. That density of drawn information is the style, so never plan at half size and scale up: the information never comes back.
- **Flat cel shading.** Each material has a base color and one big shadow shape: on the right side, under the head, under the arms and between the legs. There are no gradients, and parts don't each get their own rim of light.
- **Ink:** 1 px warm near-black (≈ `#281913`). It forms the outline, the line where an arm crosses the torso, and fat jowls. Inside the face it appears only as 1-pixel eyes; features are shadow brown and skin shadow (see `eastward_anatomy.md`).
- **Faces carry the character.** In Helen, read with `refs.py text`:
  - eyes are single ink pixels, surrounded by skin shadow;
  - the mouth is dark brown, not ink;
  - the nose is shaped with shadow color;
  - cheeks and blush are flat shapes.
  Beards and mustaches are big masses broken by a few shadow marks.
- **Hands:** big light mittens of 4–6 px, sometimes with one ink line between the fingers. Boots and feet are blocky.
- **Clothing:** big flat areas with a few drawn shapes on top (straps, pockets, stains, a fold or two).
- **Palette:** muted and warm. Shadows shift toward brown or purple, and the shared ink and brown tones recur across characters.

## Reference pack layout (if available)

`04-atlas/characters-static-1x.png` + `.json`: 220 single frames at 1× (TexturePacker-style atlas). Pull one out with `tools/refs.py extract`. `05-previews/characters-contact-sheet.png` shows every frame with its name, so you can browse and pick references. `02-animation-sheets/` holds real animation frames.
