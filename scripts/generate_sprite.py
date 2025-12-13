#!/usr/bin/env python3
"""Generate original CC0 sprite sheets for archetypes (martial/grappler/frog).

Creates single-row strips with actions: idle, walk, punch, kick, jump.
Art is programmatic and non-infringing, aiming for an SF-inspired silhouette
without copying any existing sprites.
"""
from PIL import Image, ImageDraw
import os


def _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=12):
    # head
    draw.ellipse((cx - head_r, cy - 28, cx + head_r, cy - 12), fill=(220, 180, 140, 255))
    # torso
    draw.rectangle((cx - torso_w // 2, cy - 12, cx + torso_w // 2, cy + 18), fill=body_col)


def _limb(draw, x0, y0, x1, y1, width, color):
    draw.line((x0, y0, x1, y1), fill=color, width=width)
    r = max(2, width // 2)
    draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=color)


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

            limb_col = (30, 30, 30, 255)
            if archetype == 'martial':
                # martial artist: slimmer torso, headband
                _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=12)
                # headband
                draw.rectangle((cx - head_r - 2, cy - 26, cx + head_r + 2, cy - 22), fill=(220, 30, 30, 255))
                # gi outline
                draw.rectangle((cx - 14, cy - 12, cx + 14, cy + 18), outline=(240, 240, 240, 255), width=2)
                # gloves
                draw.ellipse((cx + 18, cy - 6, cx + 26, cy + 2), fill=(240, 240, 240, 255))
                draw.ellipse((cx - 26, cy - 6, cx - 18, cy + 2), fill=(240, 240, 240, 255))
                # arms/legs with segments
                if action == 'idle':
                    _limb(draw, cx, cy - 4, cx - 16, cy + 10, 7, limb_col)
                    _limb(draw, cx, cy - 4, cx + 16, cy + 10, 7, limb_col)
                    _limb(draw, cx - 6, cy + 16, cx - 10, cy + 36, 8, limb_col)
                    _limb(draw, cx + 6, cy + 16, cx + 10, cy + 36, 8, limb_col)
                elif action == 'walk':
                    offset = (-10, -4, 10, 4)[f % 4]
                    _limb(draw, cx, cy - 4, cx - 18 + offset, cy + 10, 7, limb_col)
                    _limb(draw, cx, cy - 4, cx + 18 - offset, cy + 10, 7, limb_col)
                    _limb(draw, cx - 6, cy + 16, cx - 12 + offset, cy + 40, 8, limb_col)
                    _limb(draw, cx + 6, cy + 16, cx + 12 - offset, cy + 40, 8, limb_col)
                elif action == 'punch':
                    if f == frames - 1:
                        _limb(draw, cx, cy - 4, cx + 38, cy - 4, 8, limb_col)
                    else:
                        _limb(draw, cx, cy - 4, cx + 18, cy - 2, 7, limb_col)
                    _limb(draw, cx, cy - 4, cx - 18, cy - 2, 7, limb_col)
                    _limb(draw, cx - 6, cy + 16, cx - 10, cy + 36, 8, limb_col)
                    _limb(draw, cx + 6, cy + 16, cx + 10, cy + 36, 8, limb_col)
                elif action == 'kick':
                    _limb(draw, cx, cy - 4, cx + 16, cy - 2, 7, limb_col)
                    _limb(draw, cx, cy - 4, cx - 16, cy - 2, 7, limb_col)
                    if f == frames - 1:
                        _limb(draw, cx + 2, cy + 18, cx + 44, cy + 4, 9, limb_col)
                    else:
                        _limb(draw, cx + 2, cy + 18, cx + 16, cy + 40, 8, limb_col)
                    _limb(draw, cx - 6, cy + 18, cx - 10, cy + 40, 8, limb_col)
                else:  # jump
                    yoff = -12 if f == 1 else (-6 if f == 0 else -2)
                    draw.rectangle((cx - 6, cy - 12 + yoff, cx + 6, cy + 18 + yoff), fill=body_col)
                    _limb(draw, cx, cy - 4 + yoff, cx - 16, cy + 8 + yoff, 7, limb_col)
                    _limb(draw, cx, cy - 4 + yoff, cx + 16, cy + 8 + yoff, 7, limb_col)
                    _limb(draw, cx - 6, cy + 16 + yoff, cx - 10, cy + 36 + yoff, 8, limb_col)
                    _limb(draw, cx + 6, cy + 16 + yoff, cx + 10, cy + 36 + yoff, 8, limb_col)
            elif archetype == 'frog':
                # angry frog: green body, red gloves, wide eyes/brow
                frog_skin = (60, 170, 60, 255)
                body_col = frog_skin
                _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=16)
                # eyes + brow
                draw.ellipse((cx - 10, cy - 30, cx - 2, cy - 22), fill=(240, 240, 240, 255))
                draw.ellipse((cx + 2, cy - 30, cx + 10, cy - 22), fill=(240, 240, 240, 255))
                draw.rectangle((cx - 10, cy - 28, cx + 10, cy - 24), fill=(40, 40, 40, 255))
                # mouth (frown)
                draw.rectangle((cx - 6, cy - 16, cx + 6, cy - 14), fill=(40, 40, 40, 255))
                # gloves/feet
                glove_col = (200, 40, 40, 255)
                foot_col = (50, 120, 50, 255)
                draw.ellipse((cx + 18, cy - 6, cx + 26, cy + 2), fill=glove_col)
                draw.ellipse((cx - 26, cy - 6, cx - 18, cy + 2), fill=glove_col)
                # arms/legs
                if action == 'idle':
                    _limb(draw, cx, cy - 4, cx - 16, cy + 10, 8, limb_col)
                    _limb(draw, cx, cy - 4, cx + 16, cy + 10, 8, limb_col)
                    _limb(draw, cx - 6, cy + 18, cx - 10, cy + 40, 9, foot_col)
                    _limb(draw, cx + 6, cy + 18, cx + 10, cy + 40, 9, foot_col)
                elif action == 'walk':
                    offset = (-10, -2, 10, 2)[f % 4]
                    _limb(draw, cx, cy - 4, cx - 18 + offset, cy + 10, 8, limb_col)
                    _limb(draw, cx, cy - 4, cx + 18 - offset, cy + 10, 8, limb_col)
                    _limb(draw, cx - 6, cy + 18, cx - 12 + offset, cy + 44, 9, foot_col)
                    _limb(draw, cx + 6, cy + 18, cx + 12 - offset, cy + 44, 9, foot_col)
                elif action == 'punch':
                    if f == frames - 1:
                        _limb(draw, cx, cy - 4, cx + 40, cy - 2, 9, limb_col)
                    else:
                        _limb(draw, cx, cy - 4, cx + 18, cy - 2, 8, limb_col)
                    _limb(draw, cx, cy - 4, cx - 18, cy - 2, 8, limb_col)
                    _limb(draw, cx - 6, cy + 18, cx - 10, cy + 40, 9, foot_col)
                    _limb(draw, cx + 6, cy + 18, cx + 10, cy + 40, 9, foot_col)
                elif action == 'kick':
                    _limb(draw, cx, cy - 4, cx + 16, cy - 2, 8, limb_col)
                    _limb(draw, cx, cy - 4, cx - 16, cy - 2, 8, limb_col)
                    if f == frames - 1:
                        _limb(draw, cx + 2, cy + 20, cx + 44, cy + 6, 11, foot_col)
                    else:
                        _limb(draw, cx + 2, cy + 20, cx + 16, cy + 42, 9, foot_col)
                    _limb(draw, cx - 6, cy + 20, cx - 12, cy + 42, 9, foot_col)
                else:  # jump
                    yoff = -12 if f == 1 else (-6 if f == 0 else -2)
                    draw.rectangle((cx - 8, cy - 12 + yoff, cx + 8, cy + 18 + yoff), fill=body_col)
                    _limb(draw, cx, cy - 4 + yoff, cx - 18, cy + 8 + yoff, 8, limb_col)
                    _limb(draw, cx, cy - 4 + yoff, cx + 18, cy + 8 + yoff, 8, limb_col)
                    _limb(draw, cx - 6, cy + 18 + yoff, cx - 10, cy + 40 + yoff, 9, foot_col)
                    _limb(draw, cx + 6, cy + 18 + yoff, cx + 10, cy + 40 + yoff, 9, foot_col)
            else:
                # grappler: bulkier torso and limbs
                _draw_base(draw, cx, cy, size, head_r, body_col, torso_w=20)
                # belt/trunks
                draw.rectangle((cx - 20, cy + 6, cx + 20, cy + 14), fill=(primary[0], primary[1]//2, primary[2]//2, 255))
                # massive arms/legs
                if action == 'idle':
                    _limb(draw, cx, cy - 4, cx - 20, cy + 12, 12, limb_col)
                    _limb(draw, cx, cy - 4, cx + 20, cy + 12, 12, limb_col)
                    _limb(draw, cx - 8, cy + 18, cx - 14, cy + 44, 12, limb_col)
                    _limb(draw, cx + 8, cy + 18, cx + 14, cy + 44, 12, limb_col)
                elif action == 'walk':
                    offset = (-6, 0, 6, 0)[f % 4]
                    _limb(draw, cx, cy - 4, cx - 22 + offset, cy + 12, 12, limb_col)
                    _limb(draw, cx, cy - 4, cx + 22 - offset, cy + 12, 12, limb_col)
                    _limb(draw, cx - 8, cy + 18, cx - 14 + offset, cy + 48, 12, limb_col)
                    _limb(draw, cx + 8, cy + 18, cx + 14 - offset, cy + 48, 12, limb_col)
                elif action == 'punch':
                    if f == frames - 1:
                        _limb(draw, cx, cy - 4, cx + 48, cy - 2, 14, limb_col)
                    else:
                        _limb(draw, cx, cy - 4, cx + 20, cy - 2, 12, limb_col)
                    _limb(draw, cx, cy - 4, cx - 18, cy - 2, 12, limb_col)
                    _limb(draw, cx - 8, cy + 18, cx - 14, cy + 44, 12, limb_col)
                    _limb(draw, cx + 8, cy + 18, cx + 14, cy + 44, 12, limb_col)
                elif action == 'kick':
                    _limb(draw, cx, cy - 4, cx + 18, cy - 2, 12, limb_col)
                    _limb(draw, cx, cy - 4, cx - 18, cy - 2, 12, limb_col)
                    if f == frames - 1:
                        _limb(draw, cx + 4, cy + 22, cx + 52, cy + 6, 14, limb_col)
                    else:
                        _limb(draw, cx + 4, cy + 22, cx + 20, cy + 44, 12, limb_col)
                    _limb(draw, cx - 8, cy + 22, cx - 14, cy + 48, 12, limb_col)
                else:  # jump
                    yoff = -10 if f == 1 else (-6 if f == 0 else -2)
                    draw.rectangle((cx - 10, cy - 12 + yoff, cx + 10, cy + 18 + yoff), fill=body_col)
                    _limb(draw, cx, cy - 4 + yoff, cx - 20, cy + 8 + yoff, 12, limb_col)
                    _limb(draw, cx, cy - 4 + yoff, cx + 20, cy + 8 + yoff, 12, limb_col)
                    _limb(draw, cx - 8, cy + 18 + yoff, cx - 14, cy + 44 + yoff, 12, limb_col)
                    _limb(draw, cx + 8, cy + 18 + yoff, cx + 14, cy + 44 + yoff, 12, limb_col)

            i += 1

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f'Generated archetype "{archetype}" sprite: {path}')


def generate_pair(p1_path, p2_path, size=96):
    # defaults: martial artist for P1 (blue gi), angry frog for P2
    generate_archetype(p1_path, archetype='martial', size=size, primary=(60, 80, 200))
    generate_archetype(p2_path, archetype='frog', size=size, primary=(60, 170, 60))


if __name__ == '__main__':
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    out1 = os.path.join(base, 'player1.png')
    out2 = os.path.join(base, 'player2.png')
    os.makedirs(base, exist_ok=True)
    generate_pair(out1, out2)
