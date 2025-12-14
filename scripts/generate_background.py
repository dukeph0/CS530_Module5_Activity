#!/usr/bin/env python3
"""Generate a Street Fighter 2 style swamp background."""
from PIL import Image, ImageDraw
import random
import os
from pathlib import Path

def generate_sf2_swamp_bg(width=1024, height=640):
    """Create a 16-bit pixel art style swamp background inspired by SF2."""
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Sky gradient - swamp sky (purple-blue hazy)
    sky_top = (60, 40, 100)
    sky_mid = (90, 70, 140)
    sky_bot = (120, 100, 160)
    
    for y in range(height // 2):
        r = int(sky_top[0] + (sky_mid[0] - sky_top[0]) * (y / (height // 2)))
        g = int(sky_top[1] + (sky_mid[1] - sky_top[1]) * (y / (height // 2)))
        b = int(sky_top[2] + (sky_mid[2] - sky_top[2]) * (y / (height // 2)))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Lower sky to ground transition
    for y in range(height // 2, height):
        ratio = (y - height // 2) / (height // 2)
        r = int(sky_mid[0] + (150 - sky_mid[0]) * ratio)
        g = int(sky_mid[1] + (100 - sky_mid[1]) * ratio)
        b = int(sky_mid[2] + (80 - sky_mid[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Distant trees - very dark silhouettes
    tree_positions = [
        (100, 280), (250, 300), (450, 260), (650, 290), (850, 270), (950, 310)
    ]
    for tx, ty in tree_positions:
        # Tree trunk
        draw.rectangle([(tx - 8, ty), (tx + 8, ty + 120)], fill=(20, 30, 20))
        # Tree canopy - rounded
        draw.ellipse([(tx - 60, ty - 80), (tx + 60, ty + 20)], fill=(30, 50, 30))
        draw.ellipse([(tx - 50, ty - 60), (tx + 50, ty + 40)], fill=(40, 70, 40))
    
    # Swamp water/ground - layered with depth
    ground_y = 420
    water_col1 = (60, 100, 50)
    water_col2 = (70, 120, 60)
    water_col3 = (80, 140, 70)
    
    # Far background water/mud
    draw.rectangle([(0, ground_y - 80), (width, ground_y)], fill=water_col1)
    
    # Mid-ground reeds and vegetation
    reed_colors = [(80, 120, 60), (90, 130, 70), (70, 110, 50)]
    for i in range(width // 30):
        x = i * 30 + random.randint(-15, 15)
        h = random.randint(40, 100)
        col = reed_colors[i % 3]
        # Reed bunches
        for dx in range(-8, 9, 4):
            draw.line([(x + dx, ground_y - h), (x + dx + 2, ground_y)], fill=col, width=3)
    
    # Fighting arena platform - raised slightly, solid
    arena_y = ground_y + 10
    arena_col = (100, 120, 90)
    platform_shadow = (60, 70, 50)
    
    draw.rectangle([(100, arena_y), (width - 100, arena_y + 60)], fill=arena_col)
    # Platform shading/depth
    draw.rectangle([(100, arena_y), (width - 100, arena_y + 8)], fill=(120, 140, 110))
    draw.rectangle([(100, arena_y + 52), (width - 100, arena_y + 60)], fill=platform_shadow)
    
    # Platform edge details
    for x in range(100, width - 100, 40):
        draw.rectangle([(x, arena_y - 2), (x + 2, arena_y + 60)], fill=(70, 85, 60))
    
    # Water ripples/reflections on ground
    ripple_col = (70, 110, 60)
    for i in range(0, width, 60):
        offset = (i // 60) % 2
        y_off = arena_y + 20 + offset * 4
        draw.line([(i, y_off), (i + 30, y_off)], fill=ripple_col, width=2)
    
    # Some atmospheric fog/haze
    fog_col = (100, 100, 120)
    # Light fog overlay
    for y in range(ground_y - 60, ground_y):
        alpha_val = int(255 * (0.1 + 0.2 * ((y - (ground_y - 60)) / 60)))
        # Blend fog
        for x in range(0, width, 4):
            img.putpixel((x, y), tuple(int(c * 0.2 + fog_col[i] * 0.8) 
                                       for i, c in enumerate(img.getpixel((x, y)))))
    
    # Some distant enemy structures/buildings (swamp huts)
    hut1_x, hut1_y = 150, 250
    # Hut silhouette
    draw.polygon([(hut1_x, hut1_y), (hut1_x - 40, hut1_y + 50), (hut1_x + 40, hut1_y + 50)], 
                 fill=(40, 50, 40))
    
    hut2_x, hut2_y = 850, 260
    draw.polygon([(hut2_x, hut2_y), (hut2_x - 35, hut2_y + 45), (hut2_x + 35, hut2_y + 45)], 
                 fill=(45, 55, 45))
    
    return img

def main():
    base = Path(__file__).resolve().parents[1]
    assets = base / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    
    bg_path = assets / 'bg_swamp.png'
    bg = generate_sf2_swamp_bg(1024, 640)
    bg.save(str(bg_path))
    print(f"Generated SF2-style swamp background: {bg_path}")

if __name__ == '__main__':
    main()
