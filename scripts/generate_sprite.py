#!/usr/bin/env python3
"""Generate a simple animated placeholder sprite-sheet (CC0) into `assets/character.png`.

This creates a single-row strip of square frames (64x64) with a simple stick-figure
or blocky character in different arm/leg poses. It's free to use because it's
generated programmatically and contains no copyrighted art.
"""
from PIL import Image, ImageDraw
import os


def _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=12):
    # head
    draw.ellipse((cx - head_r, cy - 28, cx + head_r, cy - 12), fill=(220, 180, 140, 255))
    # torso
    draw.rectangle((cx - torso_w // 2, cy - 12, cx + torso_w // 2, cy + 18), fill=body_col)


def generate_archetype(path, archetype='martial', size=96, primary=(80, 120, 200)):
    """Generate a single-row multi-action sprite for an archetype.

    archetype: 'martial' or 'grappler'
    primary: RGB tuple for primary color
    """
    counts = {'idle': 4, 'walk': 4, 'punch': 3, 'kick': 3, 'jump': 3}
    total_frames = sum(counts.values())
    strip_w = total_frames * size
    img = Image.new('RGBA', (strip_w, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    i = 0
    for action, frames in counts.items():
        for f in range(frames):
            x0 = i * size
            cx = x0 + size // 2
            cy = size // 2
            head_r = size // 12

            body_col = tuple(list(primary) + [255])

            if archetype == 'martial':
                # martial artist: slimmer torso, headband
                _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=12)
                # headband
                draw.rectangle((cx - head_r - 2, cy - 26, cx + head_r + 2, cy - 22), fill=(220, 30, 30, 255))
                # arms/legs stylized
                if action == 'idle':
                    draw.line((cx, cy - 4, cx - 10, cy + 6), fill=(30, 30, 30, 255), width=6)
                    draw.line((cx, cy - 4, cx + 10, cy + 6), fill=(30, 30, 30, 255), width=6)
                elif action == 'walk':
                    offset = (-8, 0, 8, 0)[f % 4]
                    draw.line((cx, cy - 4, cx - 12 + offset, cy + 6), fill=(30, 30, 30, 255), width=6)
                    draw.line((cx, cy - 4, cx + 12 - offset, cy + 6), fill=(30, 30, 30, 255), width=6)
                elif action == 'punch':
                    if f == frames - 1:
                        draw.line((cx, cy - 4, cx + 34, cy - 4), fill=(30, 30, 30, 255), width=7)
                    else:
                        draw.line((cx, cy - 4, cx + 12, cy - 2), fill=(30, 30, 30, 255), width=6)
                elif action == 'kick':
                    if f == frames - 1:
                        draw.line((cx, cy + 18, cx + 34, cy + 6), fill=(30, 30, 30, 255), width=7)
                    else:
                        draw.line((cx, cy + 18, cx + 10, cy + 36), fill=(30, 30, 30, 255), width=6)
                else:  # jump
                    yoff = -12 if f == 1 else (-6 if f == 0 else -2)
                    draw.rectangle((cx - 6, cy - 12 + yoff, cx + 6, cy + 18 + yoff), fill=body_col)
            else:
                # grappler: bulkier torso and limbs
                _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=20)
                # massive arms/legs
                if action == 'idle':
                    draw.line((cx, cy - 4, cx - 18, cy + 10), fill=(30, 30, 30, 255), width=10)
                    draw.line((cx, cy - 4, cx + 18, cy + 10), fill=(30, 30, 30, 255), width=10)
                elif action == 'walk':
                    offset = (-6, 0, 6, 0)[f % 4]
                    draw.line((cx, cy - 4, cx - 20 + offset, cy + 12), fill=(30, 30, 30, 255), width=10)
                    draw.line((cx, cy - 4, cx + 20 - offset, cy + 12), fill=(30, 30, 30, 255), width=10)
                elif action == 'punch':
                    if f == frames - 1:
                        draw.line((cx, cy - 4, cx + 40, cy - 4), fill=(30, 30, 30, 255), width=12)
                    else:
                        draw.line((cx, cy - 4, cx + 16, cy - 2), fill=(30, 30, 30, 255), width=10)
                elif action == 'kick':
                    if f == frames - 1:
                        draw.line((cx, cy + 18, cx + 40, cy + 6), fill=(30, 30, 30, 255), width=12)
                    else:
                        draw.line((cx, cy + 18, cx + 14, cy + 36), fill=(30, 30, 30, 255), width=10)
                else:  # jump
                    yoff = -10 if f == 1 else (-6 if f == 0 else -2)
                    draw.rectangle((cx - 10, cy - 12 + yoff, cx + 10, cy + 18 + yoff), fill=body_col)

            i += 1

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f'Generated archetype "{archetype}" sprite: {path}')


def generate_pair(p1_path, p2_path, size=96):
    # defaults: martial artist for P1 (blue gi), grappler for P2 (red trunks)
    generate_archetype(p1_path, archetype='martial', size=size, primary=(60, 80, 200))
    generate_archetype(p2_path, archetype='grappler', size=size, primary=(180, 60, 60))


if __name__ == '__main__':
    out1 = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'player1.png')
    out2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'player2.png')
    generate_pair(out1, out2)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'character.png')
    generate_placeholder(out)
