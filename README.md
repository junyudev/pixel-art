# pixel-art

An agent skill that draws pixel-art sprites as real PNGs at any size, and **[Pixel Bench](https://pixel.jyu.app)**, the benchmark it was built against.

```sh
npx skills add junyudev/pixel-art
```

The skill needs Python with `pillow`, `numpy` and `scipy`. It works with Claude Code, Codex, Cursor and other agents that load skills.

## The skill

`skills/pixel-art` picks a route by canvas size:

| Canvas | Route |
|---|---|
| up to 32 px | **Grid**: the agent writes a palette and the pixel grid as text; a renderer checks it at 1×. |
| over 32 px | **Construct**: code builds the figure and its light; the agent draws faces, hands and details at full size. |
| 32 px and up, optional | **Concept**: Codex image generation (gpt-image) designs the sprite; a converter recovers true pixels. |

## The benchmark

Agents redraw 10 real Eastward (风来之国) characters from a 3–5 sentence brief, never seeing the original. Two blind judges compare each drawing with the original on 7 criteria; a Bradley–Terry fit over every judging ranks the entries. A second suite covers 16×16 and 32×32 sprites with no original.

- pixel-art 1.0 beat the previous best version's drawings 15–5. 1.1 shades flat like the game and sets the arms off the body, at the same likeness (13–7 against those drawings, 9–11 against 1.0).
- Its grid route beat plain Opus 9–1 at 16×16.

Everything is on [pixel.jyu.app](https://pixel.jyu.app): every drawing next to its original, the judges' notes, ratings with intervals, and cost per drawing. `site/` is the static build of that site.

## License

MIT for the code (see LICENSE). Eastward © Pixpil: the original sprites and the Eastward style data are used with permission.
