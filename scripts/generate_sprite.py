#!/usr/bin/env python3
"""Generate a simple animated placeholder sprite-sheet (CC0) into `assets/character.png`.

This creates a single-row strip of square frames (64x64) with a simple stick-figure
or blocky character in different arm/leg poses. It's free to use because it's
generated programmatically and contains no copyrighted art.
"""
from PIL import Image, ImageDraw
import os


def generate_placeholder(path, frames=6, size=64):
    strip_w = frames * size
    img = Image.new('RGBA', (strip_w, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for i in range(frames):
        x0 = i * size
        # draw simple body
        body_x = x0 + size // 2
        body_y = size // 2
        head_r = size // 8
        # head
        draw.ellipse((body_x - head_r, body_y - 28, body_x + head_r, body_y - 12), fill=(220, 180, 140, 255))
        # torso
        draw.rectangle((body_x - 6, body_y - 12, body_x + 6, body_y + 20), fill=(80, 120, 200, 255))
        # simple legs/arms vary per frame
        leg_offset = (i % 3) - 1
        # left leg
        draw.line((body_x, body_y + 20, body_x - 10 + leg_offset*4, body_y + 40), fill=(40, 40, 40, 255), width=4)
        # right leg
        draw.line((body_x, body_y + 20, body_x + 10 - leg_offset*4, body_y + 40), fill=(40, 40, 40, 255), width=4)
        # left arm (swing)
        arm_up = (-8 + leg_offset*3)
        draw.line((body_x, body_y - 4, body_x - 16, body_y + arm_up), fill=(40, 40, 40, 255), width=4)
        # right arm
        draw.line((body_x, body_y - 4, body_x + 16, body_y - arm_up), fill=(40, 40, 40, 255), width=4)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print('Generated placeholder sprite:', path)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'character.png')
    generate_placeholder(out)
