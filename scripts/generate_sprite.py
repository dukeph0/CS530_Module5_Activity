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


def _webbed(draw, base_x, base_y, out_x, out_y, spread, color):
    # Simple triangular webbed tip
    draw.polygon(
        [
            (out_x, out_y),
            (out_x - spread, out_y + spread // 2),
            (out_x + spread, out_y + spread // 2),
        ],
        fill=color,
    )
    draw.line((base_x, base_y, out_x, out_y), fill=color, width=spread)


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
                # MENACING FROG: wide body, huge eyes on top, massive mouth
                frog_skin = (25, 95, 35, 255)
                dark_skin = (15, 65, 25, 255)
                belly = (160, 210, 120, 255)
                eye_white = (245, 245, 220, 255)
                pupil = (10, 10, 10, 255)
                mouth_dark = (20, 20, 20, 255)
                mouth_inside = (140, 40, 40, 255)

                # MASSIVE BODY - lower center for grounded squat
                body_w = 32
                body_h = 30
                cy_low = cy + 8  # lower the center position
                body_top = cy_low - 10
                # main body mass - wide oval
                draw.ellipse((cx - body_w, body_top, cx + body_w, body_top + body_h), fill=frog_skin)
                # darker back marking
                draw.ellipse((cx - body_w + 6, body_top + 4, cx + body_w - 6, body_top + 16), fill=dark_skin)
                # belly - lighter, lower half
                draw.ellipse((cx - 26, body_top + 14, cx + 26, body_top + body_h - 2), fill=belly)
                # body shading/roundness
                draw.ellipse((cx - body_w + 2, body_top + 2, cx + body_w - 2, body_top + body_h - 4), outline=dark_skin, width=1)
                
                # MASSIVE BULGING EYES on very top
                eye_size = 16
                eye_y = body_top - 18
                eye_spacing = 10
                # left eye bulge
                draw.ellipse((cx - eye_spacing - eye_size, eye_y, cx - eye_spacing, eye_y + eye_size), fill=eye_white)
                draw.ellipse((cx - eye_spacing - eye_size + 2, eye_y + 2, cx - eye_spacing + 2, eye_y + eye_size - 2), fill=frog_skin, outline=dark_skin)
                # right eye bulge  
                draw.ellipse((cx + eye_spacing, eye_y, cx + eye_spacing + eye_size, eye_y + eye_size), fill=eye_white)
                draw.ellipse((cx + eye_spacing - 2, eye_y + 2, cx + eye_spacing + eye_size - 2, eye_y + eye_size - 2), fill=frog_skin, outline=dark_skin)
                # ANGRY SLIT PUPILS
                draw.ellipse((cx - eye_spacing - 10, eye_y + 5, cx - eye_spacing - 4, eye_y + 11), fill=pupil)
                draw.ellipse((cx + eye_spacing + 4, eye_y + 5, cx + eye_spacing + 10, eye_y + 11), fill=pupil)
                # menacing brow ridges
                draw.polygon([(cx - eye_spacing - eye_size, eye_y + 3), (cx - eye_spacing - 2, eye_y - 1), (cx - eye_spacing, eye_y + 3)], fill=(80, 20, 20, 255))
                draw.polygon([(cx + eye_spacing, eye_y + 3), (cx + eye_spacing + 2, eye_y - 1), (cx + eye_spacing + eye_size, eye_y + 3)], fill=(80, 20, 20, 255))
                
                # HUGE GAPING MOUTH - almost whole width
                mouth_y = body_top + 6
                mouth_w = 24
                # mouth opening
                draw.ellipse((cx - mouth_w, mouth_y, cx + mouth_w, mouth_y + 14), fill=mouth_dark)
                # inside mouth/throat
                draw.ellipse((cx - mouth_w + 3, mouth_y + 2, cx + mouth_w - 3, mouth_y + 10), fill=mouth_inside)
                # mouth line detail
                draw.arc((cx - mouth_w, mouth_y, cx + mouth_w, mouth_y + 14), 3.14, 6.28, fill=dark_skin, width=2)
                # FROG LEGS - thick powerful haunches
                leg_col = frog_skin
                webbed_foot = (50, 115, 55, 255)
                
                if action == 'idle':
                    # tiny front arms tucked close
                    draw.ellipse((cx - 30, cy_low + 10, cx - 24, cy_low + 16), fill=leg_col)
                    draw.ellipse((cx + 24, cy_low + 10, cx + 30, cy_low + 16), fill=leg_col)
                    # MASSIVE back leg haunches - WIDE SQUAT
                    draw.ellipse((cx - 38, cy_low + 12, cx - 20, cy_low + 28), fill=leg_col)
                    draw.ellipse((cx + 20, cy_low + 12, cx + 38, cy_low + 28), fill=leg_col)
                    # lower legs bent OUT TO SIDES
                    _webbed(draw, cx - 26, cy_low + 24, cx - 34, cy_low + 46, 14, webbed_foot)
                    _webbed(draw, cx + 26, cy_low + 24, cx + 34, cy_low + 46, 14, webbed_foot)
                elif action == 'walk':
                    # hop cycle: coil, launch, extend, land
                    hop_y = (-6, -16, -8, 0)[f % 4]
                    leg_ext = (0, 12, 8, 0)[f % 4]
                    leg_spread = (0, 4, 2, 0)[f % 4]
                    # front arms
                    draw.ellipse((cx - 30, cy_low + 10 + hop_y, cx - 24, cy_low + 16 + hop_y), fill=leg_col)
                    draw.ellipse((cx + 24, cy_low + 10 + hop_y, cx + 30, cy_low + 16 + hop_y), fill=leg_col)
                    # haunches compress/extend WIDE
                    draw.ellipse((cx - 38 - leg_spread, cy_low + 12 + hop_y, cx - 20, cy_low + 28 + hop_y - leg_ext), fill=leg_col)
                    draw.ellipse((cx + 20, cy_low + 12 + hop_y, cx + 38 + leg_spread, cy_low + 28 + hop_y - leg_ext), fill=leg_col)
                    # lower legs push OUT
                    _webbed(draw, cx - 26, cy_low + 24 + hop_y, cx - 36 - leg_ext, cy_low + 48 + hop_y, 14, webbed_foot)
                    _webbed(draw, cx + 26, cy_low + 24 + hop_y, cx + 36 + leg_ext, cy_low + 48 + hop_y, 14, webbed_foot)
                elif action == 'punch':
                    # TONGUE LASH - shoots from mouth
                    if f == frames - 1:
                        tongue_len = 68
                        tongue_start_y = mouth_y + 5
                        # thick tongue base tapering
                        draw.polygon([
                            (cx + 2, tongue_start_y), 
                            (cx + tongue_len, tongue_start_y + 2),
                            (cx + tongue_len, tongue_start_y + 5),
                            (cx + 2, tongue_start_y + 7)
                        ], fill=(220, 60, 60, 255))
                        # sticky tip
                        draw.ellipse((cx + tongue_len - 4, tongue_start_y, cx + tongue_len + 4, tongue_start_y + 7), fill=(200, 50, 50, 255))
                    # front arms
                    draw.ellipse((cx - 30, cy_low + 10, cx - 24, cy_low + 16), fill=leg_col)
                    draw.ellipse((cx + 24, cy_low + 10, cx + 30, cy_low + 16), fill=leg_col)
                    # back legs planted WIDE for stability
                    draw.ellipse((cx - 38, cy_low + 12, cx - 20, cy_low + 28), fill=leg_col)
                    draw.ellipse((cx + 20, cy_low + 12, cx + 38, cy_low + 28), fill=leg_col)
                    _webbed(draw, cx - 26, cy_low + 24, cx - 34, cy_low + 46, 14, webbed_foot)
                    _webbed(draw, cx + 26, cy_low + 24, cx + 34, cy_low + 46, 14, webbed_foot)
                elif action == 'kick':
                    # POWERFUL LEG STRIKE
                    # front arms
                    draw.ellipse((cx - 30, cy_low + 10, cx - 24, cy_low + 16), fill=leg_col)
                    draw.ellipse((cx + 24, cy_low + 10, cx + 30, cy_low + 16), fill=leg_col)
                    if f == frames - 1:
                        # mouth open, short tongue flick
                        draw.polygon([
                            (cx + 2, mouth_y + 5), 
                            (cx + 34, mouth_y + 5),
                            (cx + 34, mouth_y + 7),
                            (cx + 2, mouth_y + 7)
                        ], fill=(220, 60, 60, 180))
                        # extended haunch
                        draw.ellipse((cx + 18, cy_low + 10, cx + 36, cy_low + 22), fill=leg_col)
                        # STRIKE leg fully extended
                        _webbed(draw, cx + 26, cy_low + 16, cx + 56, cy_low + 12, 15, webbed_foot)
                        # back support leg WIDE
                        draw.ellipse((cx - 38, cy_low + 12, cx - 20, cy_low + 28), fill=leg_col)
                        _webbed(draw, cx - 26, cy_low + 24, cx - 34, cy_low + 46, 14, webbed_foot)
                    else:
                        # coiling WIDE
                        draw.ellipse((cx - 38, cy_low + 12, cx - 20, cy_low + 28), fill=leg_col)
                        draw.ellipse((cx + 20, cy_low + 12, cx + 38, cy_low + 28), fill=leg_col)
                        _webbed(draw, cx - 26, cy_low + 24, cx - 34, cy_low + 46, 14, webbed_foot)
                        _webbed(draw, cx + 26, cy_low + 24, cx + 34, cy_low + 46, 14, webbed_foot)
                else:  # jump
                    # BIG LEAP - legs extended WIDE
                    yoff = (-16 if f == 1 else -10 if f == 0 else -4)
                    # front arms spread
                    draw.ellipse((cx - 32, cy_low + 8 + yoff, cx - 26, cy_low + 14 + yoff), fill=leg_col)
                    draw.ellipse((cx + 26, cy_low + 8 + yoff, cx + 32, cy_low + 14 + yoff), fill=leg_col)
                    # haunches extended in air WIDE
                    draw.ellipse((cx - 38, cy_low + 10 + yoff, cx - 20, cy_low + 24 + yoff), fill=leg_col)
                    draw.ellipse((cx + 20, cy_low + 10 + yoff, cx + 38, cy_low + 24 + yoff), fill=leg_col)
                    # legs stretched back and OUT
                    _webbed(draw, cx - 26, cy_low + 20 + yoff, cx - 36, cy_low + 48 + yoff, 15, webbed_foot)
                    _webbed(draw, cx + 26, cy_low + 20 + yoff, cx + 36, cy_low + 48 + yoff, 15, webbed_foot)
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
