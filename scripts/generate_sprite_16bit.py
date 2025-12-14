#!/usr/bin/env python3
"""Generate 16-bit pixel art sprites for fighters (Street Fighter 2 style)."""
from PIL import Image, ImageDraw
import os
from pathlib import Path


def draw_pixel_rect(draw, x, y, w, h, color):
    """Draw a filled rectangle with pixel precision."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def draw_rounded_body(draw, x, y, w, h, color, shadow_color):
    """Draw a body part with rounded edges for more natural SF2 look."""
    # Main body
    draw_pixel_rect(draw, x + 1, y, w - 2, h, color)
    draw_pixel_rect(draw, x, y + 1, w, h - 2, color)
    # Corner pixels for rounding
    draw_pixel_rect(draw, x + 1, y, w - 2, 1, color)
    draw_pixel_rect(draw, x + 1, y + h - 1, w - 2, 1, color)


def draw_muscle_limb(draw, x1, y1, x2, y2, thickness, color, shadow_color, highlight_color):
    """Draw a muscular limb with shading like SF2."""
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    
    # Perpendicular for width
    px = -dy / length * thickness / 2
    py = dx / length * thickness / 2
    
    # Draw main limb shape with rounded ends
    points = [
        (x1 - px, y1 - py),
        (x1 + px, y1 + py),
        (x2 + px, y2 + py),
        (x2 - px, y2 - py)
    ]
    draw.polygon(points, fill=color)
    
    # Add highlight on one side
    highlight_points = [
        (x1 - px/2, y1 - py/2),
        (x1 + px/3, y1 + py/3),
        (x2 + px/3, y2 + py/3),
        (x2 - px/2, y2 - py/2)
    ]
    draw.polygon(highlight_points, fill=highlight_color)
    
    # Round end caps
    draw.ellipse([x1 - thickness/2, y1 - thickness/2, x1 + thickness/2, y1 + thickness/2], fill=color)
    draw.ellipse([x2 - thickness/2, y2 - thickness/2, x2 + thickness/2, y2 + thickness/2], fill=color)


def draw_martial_artist(draw, cx, cy, action, frame):
    """Draw martial artist with 16-bit pixel art style - SF2 Ryu."""
    # Colors - Exact SF2 Ryu palette
    skin = (224, 176, 136)
    skin_dark = (176, 136, 96)
    skin_light = (248, 216, 184)
    skin_shadow = (152, 112, 80)
    gi_white = (248, 248, 248)
    gi_light = (232, 232, 232)
    gi_shadow = (208, 208, 208)
    gi_dark = (184, 184, 184)
    gi_darker = (160, 160, 160)
    belt = (32, 32, 32)
    belt_highlight = (64, 64, 64)
    headband = (224, 24, 24)
    headband_dark = (176, 16, 16)
    headband_shadow = (128, 8, 8)
    hair = (64, 40, 24)
    hair_dark = (40, 24, 16)
    hair_light = (88, 64, 40)
    
    if action == 'idle':
        # Ryu's breathing animation - SF2 timing with natural sway
        sway = [0, 1, 0, -1][frame % 4]
        bob = [0, -1, -2, -1][frame % 4]
        # Head tilts slightly toward opponent (forward lean)
        head_tilt = [1, 2, 2, 1][frame % 4]
        
        # Head - Ryu's distinctive strong jawline, tilted forward at enemy
        draw.ellipse([cx - 8 + head_tilt, cy - 24 + bob, cx + 8 + head_tilt, cy - 11 + bob], fill=skin)
        draw.ellipse([cx - 7 + head_tilt, cy - 23 + bob, cx + 7 + head_tilt, cy - 12 + bob], fill=skin_light)
        # Jaw definition
        draw_pixel_rect(draw, cx - 6 + head_tilt, cy - 13 + bob, 12, 2, skin_dark)
        
        # Hair - Ryu's spiky style
        draw.ellipse([cx - 7 + head_tilt, cy - 24 + bob, cx + 7 + head_tilt, cy - 19 + bob], fill=hair)
        draw_pixel_rect(draw, cx - 6 + head_tilt, cy - 23 + bob, 3, 2, hair_dark)
        draw_pixel_rect(draw, cx + 3 + head_tilt, cy - 23 + bob, 3, 2, hair_dark)
        # Spiky top
        draw_pixel_rect(draw, cx - 3 + head_tilt, cy - 25 + bob, 6, 2, hair)
        draw_pixel_rect(draw, cx - 2 + head_tilt, cy - 26 + bob, 4, 1, hair_light)
        
        # Headband - Ryu's signature red headband
        draw_pixel_rect(draw, cx - 8 + head_tilt, cy - 20 + bob, 16, 3, headband)
        draw_pixel_rect(draw, cx - 8 + head_tilt, cy - 19 + bob, 16, 1, headband_dark)
        draw_pixel_rect(draw, cx - 7 + head_tilt, cy - 18 + bob, 14, 1, headband_shadow)
        # Headband knot
        draw_pixel_rect(draw, cx - 9 + head_tilt, cy - 19 + bob, 2, 2, headband_dark)
        
        # Face - Ryu's determined expression, eyes locked on opponent
        # Eyes looking forward at enemy
        draw_pixel_rect(draw, cx - 5 + head_tilt, cy - 17 + bob, 2, 2, (40, 40, 40))  # left eye
        draw_pixel_rect(draw, cx + 3 + head_tilt, cy - 17 + bob, 2, 2, (40, 40, 40))  # right eye
        # Eye highlights showing focus direction (looking toward opponent)
        draw_pixel_rect(draw, cx - 3 + head_tilt, cy - 16 + bob, 1, 1, (80, 80, 80))  # left pupil forward
        draw_pixel_rect(draw, cx + 5 + head_tilt, cy - 16 + bob, 1, 1, (80, 80, 80))  # right pupil forward
        draw_pixel_rect(draw, cx - 1 + head_tilt, cy - 15 + bob, 2, 2, skin_dark)  # nose
        draw_pixel_rect(draw, cx - 2 + head_tilt, cy - 13 + bob, 4, 1, skin_shadow)  # mouth
        draw_pixel_rect(draw, cx - 7 + head_tilt, cy - 22 + bob, 3, 8, skin_dark)  # face shadow
        
        # Torso - Ryu's muscular gi with breathing rotation and detailed folds
        torso_rotate = [0, 1, 0, -1][frame % 4]  # subtle rotation with breathing
        draw_rounded_body(draw, cx - 11 + torso_rotate, cy - 11 + bob, 22, 21, gi_white, gi_shadow)
        # Gi opening/lapels - shift with rotation
        draw_pixel_rect(draw, cx - 9 + torso_rotate, cy - 10 + bob, 2, 19, gi_shadow)
        draw_pixel_rect(draw, cx + 7 + torso_rotate, cy - 10 + bob, 2, 19, gi_shadow)
        draw_pixel_rect(draw, cx - 3 + torso_rotate, cy - 10 + bob, 6, 19, gi_light)
        draw_pixel_rect(draw, cx - 2 + torso_rotate, cy - 9 + bob, 4, 18, gi_dark)
        # Gi folds and wrinkles (SF2 detail) - dynamic with breathing
        draw_pixel_rect(draw, cx - 7 + torso_rotate, cy - 8 + bob, 1, 3, gi_darker)
        draw_pixel_rect(draw, cx + 6 + torso_rotate, cy - 8 + bob, 1, 3, gi_darker)
        draw_pixel_rect(draw, cx - 8 + torso_rotate, cy - 4 + bob, 2, 1, gi_darker)
        draw_pixel_rect(draw, cx + 6 + torso_rotate, cy - 4 + bob, 2, 1, gi_darker)
        draw_pixel_rect(draw, cx - 5 + torso_rotate, cy + 2 + bob, 10, 1, gi_shadow)
        # Muscular chest definition with breathing
        draw.ellipse([cx - 6 + torso_rotate, cy - 8 + bob, cx - 2 + torso_rotate, cy - 3 + bob], fill=gi_shadow)
        draw.ellipse([cx + 2 + torso_rotate, cy - 8 + bob, cx + 6 + torso_rotate, cy - 3 + bob], fill=gi_shadow)
        # Underarm shadows - shoulders shift
        draw_pixel_rect(draw, cx - 10 + torso_rotate, cy - 6 + bob, 2, 4, gi_darker)
        draw_pixel_rect(draw, cx + 8 + torso_rotate, cy - 6 + bob, 2, 4, gi_darker)
        
        # Belt - Ryu's black belt with highlights
        draw_pixel_rect(draw, cx - 11, cy + 8 + bob, 22, 4, belt)
        draw_pixel_rect(draw, cx - 11, cy + 8 + bob, 22, 1, belt_highlight)
        draw_pixel_rect(draw, cx - 10, cy + 11 + bob, 20, 1, (16, 16, 16))
        # Belt knot
        draw_pixel_rect(draw, cx - 2, cy + 8 + bob, 4, 5, belt)
        draw_pixel_rect(draw, cx - 2, cy + 8 + bob, 4, 1, belt_highlight)
        
        # Arms - RYU'S CLASSIC SF2 STANCE: lead fist forward, back fist chambered
        # Lead arm (right) - EXTENDED FORWARD at chest level, ready to strike
        # Upper arm with gi sleeve
        draw_muscle_limb(draw, cx + 10, cy - 7 + bob, cx + 17, cy - 10 + sway, 8, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx + 12, cy - 8 + bob, 1, 2, gi_darker)  # sleeve fold
        # Forearm - muscular and extended forward
        draw_muscle_limb(draw, cx + 17, cy - 10 + sway, cx + 26, cy - 13 + sway, 7, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx + 19, cy - 11 + sway, 4, 1, gi_shadow)  # forearm detail
        # Gi sleeve end
        draw_pixel_rect(draw, cx + 24, cy - 14 + sway, 3, 2, gi_shadow)
        # Lead fist - Ryu's iconic forward fist
        draw.ellipse([cx + 24, cy - 16 + sway, cx + 30, cy - 10 + sway], fill=skin)
        draw.ellipse([cx + 25, cy - 15 + sway, cx + 29, cy - 11 + sway], fill=skin_light)
        draw_pixel_rect(draw, cx + 26, cy - 14 + sway, 2, 3, skin_dark)  # knuckles
        draw_pixel_rect(draw, cx + 25, cy - 13 + sway, 1, 1, skin_shadow)
        
        # Back arm (left) - CHAMBERED at side, protecting body
        # Upper arm close to body
        draw_muscle_limb(draw, cx - 10, cy - 5 + bob, cx - 14, cy + 1, 7, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx - 12, cy - 4 + bob, 1, 3, gi_darker)  # sleeve shadow
        # Forearm bent back defensively
        draw_muscle_limb(draw, cx - 14, cy + 1, cx - 17, cy - 5, 7, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx - 15, cy - 2, 2, 3, gi_shadow)
        # Gi sleeve end
        draw_pixel_rect(draw, cx - 18, cy - 6, 2, 3, gi_shadow)
        # Back fist - chambered at ribs
        draw.ellipse([cx - 20, cy - 7, cx - 15, cy - 2], fill=skin)
        draw.ellipse([cx - 19, cy - 6, cx - 16, cy - 3], fill=skin_light)
        draw_pixel_rect(draw, cx - 18, cy - 5, 2, 2, skin_dark)
        
        # Legs - RYU'S WIDE STABLE STANCE: powerful thighs, bent knees
        # Back leg (left) - strong thigh, bent knee
        draw_muscle_limb(draw, cx - 8, cy + 12, cx - 12, cy + 21, 11, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx - 10, cy + 14, 2, 4, gi_darker)  # thigh fold
        draw_pixel_rect(draw, cx - 11, cy + 19, 3, 1, gi_darker)  # knee fold
        # Shin
        draw_muscle_limb(draw, cx - 12, cy + 21, cx - 11, cy + 29, 9, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx - 12, cy + 24, 2, 3, gi_shadow)  # shin detail
        
        # Front leg (right) - forward stance, powerful
        draw_muscle_limb(draw, cx + 6, cy + 12, cx + 9, cy + 21, 11, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx + 7, cy + 14, 2, 4, gi_darker)  # thigh fold
        draw_pixel_rect(draw, cx + 8, cy + 19, 3, 1, gi_darker)  # knee fold
        # Shin
        draw_muscle_limb(draw, cx + 9, cy + 21, cx + 8, cy + 29, 9, gi_white, gi_shadow, gi_light)
        draw_pixel_rect(draw, cx + 8, cy + 24, 2, 3, gi_shadow)  # shin detail
        
        # Feet - Ryu's bare feet with proper anatomy
        # Back foot - turned out at angle (side/angled view)
        # Heel and sole
        draw_pixel_rect(draw, cx - 16, cy + 28, 8, 4, skin_dark)
        draw_pixel_rect(draw, cx - 15, cy + 28, 7, 3, skin)
        # Foot top/instep
        draw_pixel_rect(draw, cx - 14, cy + 29, 5, 2, skin_light)
        # Ankle connection
        draw_pixel_rect(draw, cx - 12, cy + 28, 2, 2, skin_dark)
        # Individual toes
        draw_pixel_rect(draw, cx - 15, cy + 30, 2, 2, skin_dark)  # big toe
        draw_pixel_rect(draw, cx - 14, cy + 30, 2, 1, skin)
        draw_pixel_rect(draw, cx - 13, cy + 31, 1, 1, skin_shadow)  # toe separator
        draw_pixel_rect(draw, cx - 12, cy + 30, 1, 1, skin_dark)  # second toe
        draw_pixel_rect(draw, cx - 11, cy + 30, 1, 1, skin_dark)  # third toe
        draw_pixel_rect(draw, cx - 10, cy + 31, 1, 1, skin_shadow)  # small toes
        
        # Front foot - forward stance (top/slight side view)
        # Heel
        draw_pixel_rect(draw, cx + 5, cy + 29, 2, 3, skin_shadow)
        # Foot body
        draw_pixel_rect(draw, cx + 6, cy + 28, 7, 4, skin_dark)
        draw_pixel_rect(draw, cx + 7, cy + 28, 6, 3, skin)
        # Arch and top
        draw_pixel_rect(draw, cx + 8, cy + 29, 4, 2, skin_light)
        # Ankle connection
        draw_pixel_rect(draw, cx + 8, cy + 28, 2, 2, skin_dark)
        # Individual toes
        draw_pixel_rect(draw, cx + 9, cy + 30, 2, 2, skin_dark)  # big toe
        draw_pixel_rect(draw, cx + 10, cy + 30, 2, 1, skin)
        draw_pixel_rect(draw, cx + 11, cy + 31, 1, 1, skin_shadow)  # toe separator
        draw_pixel_rect(draw, cx + 11, cy + 30, 1, 1, skin_dark)  # second toe
        draw_pixel_rect(draw, cx + 12, cy + 30, 1, 1, skin_dark)  # third toe
        draw_pixel_rect(draw, cx + 12, cy + 31, 1, 1, skin_shadow)  # small toes
        
    elif action == 'walk':
        # Ryu's forward walk - SF2 style deliberate stride
        walk_cycle = [0, 6, 0, -6][frame % 4]
        leg_lift = [0, 4, 0, 4][frame % 4]
        bob = [0, -2, -1, -2][frame % 4]
        # Head stays locked on opponent while walking
        head_look = [2, 3, 2, 3][frame % 4]  # always looking forward
        # Torso rotation with walking motion
        torso_sway = [0, 2, 0, -2][frame % 4]
        
        # Head - Ryu's determined forward walk, eyes on enemy
        draw.ellipse([cx - 8 + head_look, cy - 24 + bob, cx + 8 + head_look, cy - 11 + bob], fill=skin)
        draw.ellipse([cx - 7 + head_look, cy - 23 + bob, cx + 7 + head_look, cy - 12 + bob], fill=skin_light)
        draw.ellipse([cx - 7 + head_look, cy - 24 + bob, cx + 7 + head_look, cy - 19 + bob], fill=hair)
        draw_pixel_rect(draw, cx - 8 + head_look, cy - 20 + bob, 16, 3, headband)
        # Eyes tracking forward at opponent
        draw_pixel_rect(draw, cx - 5 + head_look, cy - 17 + bob, 2, 1, (40, 40, 40))
        draw_pixel_rect(draw, cx + 3 + head_look, cy - 17 + bob, 2, 1, (40, 40, 40))
        # Pupils looking forward
        draw_pixel_rect(draw, cx - 3 + head_look, cy - 16 + bob, 1, 1, (80, 80, 80))
        draw_pixel_rect(draw, cx + 5 + head_look, cy - 16 + bob, 1, 1, (80, 80, 80))
        
        # Torso - natural rotation during walk with shoulder movement
        draw_rounded_body(draw, cx - 9 + torso_sway, cy - 11 + bob, 18, 20, gi_white, gi_shadow)
        draw_pixel_rect(draw, cx - 7 + torso_sway, cy - 10 + bob, 2, 18, gi_shadow)
        draw_pixel_rect(draw, cx - 2 + torso_sway, cy - 10 + bob, 4, 18, gi_dark)
        draw_pixel_rect(draw, cx - 9 + torso_sway, cy + 7 + bob, 18, 3, belt)
        # Shoulder definition shifting with rotation
        draw_pixel_rect(draw, cx - 8 + torso_sway, cy - 9 + bob, 2, 3, gi_darker)
        draw_pixel_rect(draw, cx + 6 + torso_sway, cy - 9 + bob, 2, 3, gi_darker)
        
        # Arms - natural counterbalance swing with bent elbows
        # Left arm
        arm_bend_l = walk_cycle // 2
        draw_muscle_limb(draw, cx - 9, cy - 7 + bob, cx - 14 + walk_cycle, cy + arm_bend_l, 7, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx - 14 + walk_cycle, cy + arm_bend_l, cx - 16 + walk_cycle, cy + 6, 6, gi_white, gi_shadow, gi_white)
        draw.ellipse([cx - 19 + walk_cycle, cy + 5, cx - 13 + walk_cycle, cy + 11], fill=skin)
        # Right arm
        arm_bend_r = -walk_cycle // 2
        draw_muscle_limb(draw, cx + 9, cy - 7 + bob, cx + 14 - walk_cycle, cy + arm_bend_r, 7, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx + 14 - walk_cycle, cy + arm_bend_r, cx + 16 - walk_cycle, cy + 6, 6, gi_white, gi_shadow, gi_white)
        draw.ellipse([cx + 13 - walk_cycle, cy + 5, cx + 19 - walk_cycle, cy + 11], fill=skin)
        
        # Legs - natural walking with knee articulation
        # Left leg - thigh and shin separate for natural bend
        draw_muscle_limb(draw, cx - 5, cy + 10, cx - 6 + walk_cycle, cy + 18 - leg_lift, 10, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx - 6 + walk_cycle, cy + 18 - leg_lift, cx - 7 + walk_cycle, cy + 27, 8, gi_white, gi_shadow, gi_white)
        # Right leg
        draw_muscle_limb(draw, cx + 5, cy + 10, cx + 6 - walk_cycle, cy + 18 - (3 - leg_lift), 10, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx + 6 - walk_cycle, cy + 18 - (3 - leg_lift), cx + 7 - walk_cycle, cy + 27, 8, gi_white, gi_shadow, gi_white)
        
        # Feet - natural walking placement with proper anatomy
        # Left foot
        draw_pixel_rect(draw, cx - 11 + walk_cycle, cy + 26, 6, 4, skin_dark)
        draw_pixel_rect(draw, cx - 10 + walk_cycle, cy + 26, 5, 3, skin)
        draw_pixel_rect(draw, cx - 9 + walk_cycle, cy + 27, 3, 2, skin_light)
        draw_pixel_rect(draw, cx - 10 + walk_cycle, cy + 28, 2, 2, skin_dark)  # toes
        draw_pixel_rect(draw, cx - 8 + walk_cycle, cy + 28, 1, 1, skin_shadow)
        # Right foot
        draw_pixel_rect(draw, cx + 5 - walk_cycle, cy + 26, 6, 4, skin_dark)
        draw_pixel_rect(draw, cx + 6 - walk_cycle, cy + 26, 5, 3, skin)
        draw_pixel_rect(draw, cx + 7 - walk_cycle, cy + 27, 3, 2, skin_light)
        draw_pixel_rect(draw, cx + 8 - walk_cycle, cy + 28, 2, 2, skin_dark)  # toes
        draw_pixel_rect(draw, cx + 9 - walk_cycle, cy + 28, 1, 1, skin_shadow)
        
    elif action == 'punch':
        # SF2 Ryu's standing punch - consistent forward punch from lead hand
        # Frame 0: startup, Frame 1: mid-extension, Frame 2: full extension, Frame 3: recovery
        lean = [0, 1, 2, 1][frame % 4]
        # Head follows punch slightly but eyes stay locked
        head_shift = [1, 2, 3, 2][frame % 4]
        # Torso rotates more dramatically
        torso_rotate = [0, 2, 3, 1][frame % 4]
        
        # Head - leaning into punch, eyes locked on target
        draw.ellipse([cx - 7 + head_shift, cy - 23, cx + 7 + head_shift, cy - 12], fill=skin)
        draw.ellipse([cx - 6 + head_shift, cy - 22, cx + 6 + head_shift, cy - 13], fill=skin_light)
        draw.ellipse([cx - 6 + head_shift, cy - 23, cx + 6 + head_shift, cy - 18], fill=hair)
        draw_pixel_rect(draw, cx - 7 + head_shift, cy - 19, 14, 3, headband)
        # Eyes intense and focused forward
        draw_pixel_rect(draw, cx - 4 + head_shift, cy - 16, 2, 1, (50, 50, 50))
        draw_pixel_rect(draw, cx + 2 + head_shift, cy - 16, 2, 1, (50, 50, 50))
        # Pupils locked on opponent
        draw_pixel_rect(draw, cx - 2 + head_shift, cy - 15, 1, 1, (100, 100, 100))
        draw_pixel_rect(draw, cx + 4 + head_shift, cy - 15, 1, 1, (100, 100, 100))
        
        # Torso - rotating strongly with punch, shoulders turning
        draw_rounded_body(draw, cx - 9 + torso_rotate, cy - 11, 18, 20, gi_white, gi_shadow)
        draw_pixel_rect(draw, cx - 7 + torso_rotate, cy - 10, 2, 18, gi_shadow)
        draw_pixel_rect(draw, cx - 2 + torso_rotate, cy - 10, 4, 18, gi_dark)
        draw_pixel_rect(draw, cx - 9 + torso_rotate, cy + 7, 18, 3, belt)
        # Shoulder rotation emphasis
        draw_pixel_rect(draw, cx - 8 + torso_rotate, cy - 9, 3, 2, gi_darker)
        draw_pixel_rect(draw, cx + 5 + torso_rotate, cy - 9, 3, 2, gi_darker)
        
        # Back arm (left) - pulled back for power
        draw_muscle_limb(draw, cx - 9 + lean, cy - 6, cx - 18, cy + 2, 7, gi_white, gi_shadow, gi_white)
        draw.ellipse([cx - 21, cy + 2, cx - 15, cy + 8], fill=skin)
        draw.ellipse([cx - 20, cy + 3, cx - 16, cy + 7], fill=skin_light)
        
        # Lead arm (right) - punching, progressive extension
        if frame == 0:  # Startup - slight pull back
            draw_muscle_limb(draw, cx + 9 + lean, cy - 8, cx + 18, cy - 10, 8, gi_white, gi_shadow, gi_white)
            draw.ellipse([cx + 15, cy - 14, cx + 21, cy - 8], fill=skin)
            draw.ellipse([cx + 16, cy - 13, cx + 20, cy - 9], fill=skin_light)
            draw_pixel_rect(draw, cx + 17, cy - 12, 2, 2, skin_dark)
        elif frame == 1:  # Mid extension
            draw_muscle_limb(draw, cx + 9 + lean, cy - 8, cx + 26, cy - 7, 9, gi_white, gi_shadow, gi_white)
            draw.ellipse([cx + 23, cy - 11, cx + 30, cy - 4], fill=skin)
            draw.ellipse([cx + 24, cy - 10, cx + 29, cy - 5], fill=skin_light)
            draw_pixel_rect(draw, cx + 25, cy - 9, 3, 3, skin_dark)
        elif frame == 2:  # Full extension - impact!
            draw_muscle_limb(draw, cx + 9 + lean, cy - 8, cx + 36, cy - 5, 9, gi_white, gi_shadow, gi_white)
            draw.ellipse([cx + 33, cy - 9, cx + 41, cy - 1], fill=skin)
            draw.ellipse([cx + 34, cy - 8, cx + 40, cy - 2], fill=skin_light)
            draw_pixel_rect(draw, cx + 35, cy - 7, 3, 3, skin_dark)
            # Speed lines for impact
            draw_pixel_rect(draw, cx + 42, cy - 6, 4, 1, (255, 255, 200))
            draw_pixel_rect(draw, cx + 42, cy - 4, 3, 1, (255, 255, 200))
        else:  # Recovery - pulling back
            draw_muscle_limb(draw, cx + 9 + lean, cy - 8, cx + 22, cy - 8, 8, gi_white, gi_shadow, gi_white)
            draw.ellipse([cx + 19, cy - 12, cx + 26, cy - 5], fill=skin)
            draw.ellipse([cx + 20, cy - 11, cx + 25, cy - 6], fill=skin_light)
            draw_pixel_rect(draw, cx + 21, cy - 10, 3, 3, skin_dark)
        
        # Legs - power stance
        draw_muscle_limb(draw, cx - 6, cy + 10, cx - 9, cy + 24, 9, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx + 4, cy + 10, cx + 6, cy + 24, 9, gi_white, gi_shadow, gi_white)
        # Back foot
        draw_pixel_rect(draw, cx - 13, cy + 25, 7, 4, skin_dark)
        draw_pixel_rect(draw, cx - 12, cy + 25, 6, 3, skin)
        draw_pixel_rect(draw, cx - 11, cy + 26, 4, 2, skin_light)
        draw_pixel_rect(draw, cx - 12, cy + 27, 2, 2, skin_dark)  # toes
        # Front foot
        draw_pixel_rect(draw, cx + 4, cy + 25, 7, 4, skin_dark)
        draw_pixel_rect(draw, cx + 5, cy + 25, 6, 3, skin)
        draw_pixel_rect(draw, cx + 6, cy + 26, 4, 2, skin_light)
        draw_pixel_rect(draw, cx + 7, cy + 27, 2, 2, skin_dark)  # toes
        
    elif action == 'kick':
        # SF2 Ryu's standing kick - progressive extension
        # Frame 0: startup, Frame 1: chamber knee up, Frame 2: full extension, Frame 3: recovery
        # Head stays focused on opponent
        head_focus = [2, 2, 3, 2][frame % 4]
        # Torso counter-rotates for balance during kick
        torso_balance = [0, -1, -2, -1][frame % 4]
        
        # Head - laser focused on opponent while kicking
        draw.ellipse([cx - 7 + head_focus, cy - 23, cx + 7 + head_focus, cy - 12], fill=skin)
        draw.ellipse([cx - 6 + head_focus, cy - 22, cx + 6 + head_focus, cy - 13], fill=skin_light)
        draw.ellipse([cx - 6 + head_focus, cy - 23, cx + 6 + head_focus, cy - 18], fill=hair)
        draw_pixel_rect(draw, cx - 7 + head_focus, cy - 19, 14, 3, headband)
        # Eyes locked forward
        draw_pixel_rect(draw, cx - 4 + head_focus, cy - 16, 2, 1, (50, 50, 50))
        draw_pixel_rect(draw, cx + 2 + head_focus, cy - 16, 2, 1, (50, 50, 50))
        # Pupils showing focus
        draw_pixel_rect(draw, cx - 2 + head_focus, cy - 15, 1, 1, (100, 100, 100))
        draw_pixel_rect(draw, cx + 4 + head_focus, cy - 15, 1, 1, (100, 100, 100))
        
        # Torso - counter-rotating for balance during kick, shoulders adjusting
        draw_rounded_body(draw, cx - 9 + torso_balance, cy - 11, 18, 20, gi_white, gi_shadow)
        draw_pixel_rect(draw, cx - 7 + torso_balance, cy - 10, 2, 18, gi_shadow)
        draw_pixel_rect(draw, cx - 2 + torso_balance, cy - 10, 4, 18, gi_dark)
        draw_pixel_rect(draw, cx - 9 + torso_balance, cy + 7, 18, 3, belt)
        # Shoulders shifting for balance
        draw_pixel_rect(draw, cx - 8 + torso_balance, cy - 9, 2, 3, gi_darker)
        draw_pixel_rect(draw, cx + 6 + torso_balance, cy - 9, 2, 3, gi_darker)
        
        # Arms - balance during kick
        draw_muscle_limb(draw, cx - 9, cy - 6, cx - 16, cy + 2, 7, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx + 9, cy - 6, cx + 16, cy + 2, 7, gi_white, gi_shadow, gi_white)
        draw.ellipse([cx - 19, cy + 2, cx - 13, cy + 8], fill=skin)
        draw.ellipse([cx - 20, cy + 3, cx - 14, cy + 7], fill=skin_light)
        draw.ellipse([cx + 13, cy + 2, cx + 19, cy + 8], fill=skin)
        draw.ellipse([cx + 14, cy + 3, cx + 18, cy + 7], fill=skin_light)
        
        # Standing leg (left) - stable base
        draw_muscle_limb(draw, cx - 5, cy + 10, cx - 7, cy + 24, 9, gi_white, gi_shadow, gi_white)
        draw_pixel_rect(draw, cx - 11, cy + 25, 7, 4, skin_dark)
        draw_pixel_rect(draw, cx - 10, cy + 25, 6, 3, skin)
        draw_pixel_rect(draw, cx - 9, cy + 26, 4, 2, skin_light)
        
        # Kicking leg (right) - progressive animation
        if frame == 0:  # Startup - leg begins to lift
            draw_muscle_limb(draw, cx + 5, cy + 10, cx + 10, cy + 18, 9, gi_white, gi_shadow, gi_white)
            draw_pixel_rect(draw, cx + 8, cy + 17, 6, 4, skin_dark)
            draw_pixel_rect(draw, cx + 9, cy + 18, 5, 3, skin)
            draw_pixel_rect(draw, cx + 10, cy + 19, 3, 2, skin_light)
        elif frame == 1:  # Chamber - knee pulled up high
            draw_muscle_limb(draw, cx + 5, cy + 10, cx + 12, cy + 4, 9, gi_white, gi_shadow, gi_white)
            draw_muscle_limb(draw, cx + 12, cy + 4, cx + 20, cy + 8, 8, gi_white, gi_shadow, gi_white)
            draw_pixel_rect(draw, cx + 18, cy + 7, 6, 4, skin_dark)
            draw_pixel_rect(draw, cx + 19, cy + 8, 5, 3, skin)
            draw_pixel_rect(draw, cx + 20, cy + 9, 3, 2, skin_light)
        elif frame == 2:  # Full extension - IMPACT!
            draw_muscle_limb(draw, cx + 5, cy + 10, cx + 32, cy + 4, 10, gi_white, gi_shadow, gi_white)
            # Kicking foot with striking detail
            draw_pixel_rect(draw, cx + 30, cy + 1, 8, 5, skin_dark)
            draw_pixel_rect(draw, cx + 31, cy + 2, 7, 4, skin)
            draw_pixel_rect(draw, cx + 32, cy + 3, 5, 2, skin_light)
            draw_pixel_rect(draw, cx + 34, cy + 4, 3, 2, skin_dark)  # striking surface
            # Impact lines
            draw_pixel_rect(draw, cx + 39, cy + 3, 5, 1, (255, 255, 200))
            draw_pixel_rect(draw, cx + 39, cy + 5, 4, 1, (255, 255, 200))
        else:  # Recovery - leg retracting
            draw_muscle_limb(draw, cx + 5, cy + 10, cx + 14, cy + 6, 9, gi_white, gi_shadow, gi_white)
            draw_muscle_limb(draw, cx + 14, cy + 6, cx + 18, cy + 12, 8, gi_white, gi_shadow, gi_white)
            draw_pixel_rect(draw, cx + 16, cy + 11, 6, 4, skin_dark)
            draw_pixel_rect(draw, cx + 17, cy + 12, 5, 3, skin)
            draw_pixel_rect(draw, cx + 18, cy + 13, 3, 2, skin_light)
            
    elif action == 'jump':
        # Ryu's jump arc - SF2 style
        y_offset = [-13, -19, -8][frame % 3]
        tuck = [0, 2, 1][frame % 3]  # Body tucks slightly at apex
        
        # Head - looking forward during jump
        draw.ellipse([cx - 8, cy - 24 + y_offset, cx + 8, cy - 11 + y_offset], fill=skin)
        draw.ellipse([cx - 7, cy - 23 + y_offset, cx + 7, cy - 12 + y_offset], fill=skin_light)
        draw.ellipse([cx - 7, cy - 24 + y_offset, cx + 7, cy - 19 + y_offset], fill=hair)
        draw_pixel_rect(draw, cx - 8, cy - 20 + y_offset, 16, 3, headband)
        draw_pixel_rect(draw, cx - 5, cy - 17 + y_offset, 2, 1, (40, 40, 40))
        draw_pixel_rect(draw, cx + 3, cy - 17 + y_offset, 2, 1, (40, 40, 40))
        
        # Torso - slightly tucked at jump apex
        draw_rounded_body(draw, cx - 10, cy - 11 + y_offset + tuck, 20, 20, gi_white, gi_shadow)
        draw_pixel_rect(draw, cx - 8, cy - 10 + y_offset + tuck, 2, 18, gi_shadow)
        draw_pixel_rect(draw, cx - 2, cy - 10 + y_offset + tuck, 4, 18, gi_dark)
        draw_pixel_rect(draw, cx - 10, cy + 7 + y_offset + tuck, 20, 3, belt)
        
        # Arms - balanced jump position
        draw_muscle_limb(draw, cx - 10, cy - 7 + y_offset + tuck, cx - 16, cy - 13 + y_offset, 7, gi_white, gi_shadow, gi_light)
        draw_muscle_limb(draw, cx + 10, cy - 7 + y_offset + tuck, cx + 16, cy - 13 + y_offset, 7, gi_white, gi_shadow, gi_light)
        draw.ellipse([cx - 19, cy - 15 + y_offset, cx - 14, cy - 10 + y_offset], fill=skin)
        draw.ellipse([cx + 14, cy - 15 + y_offset, cx + 19, cy - 10 + y_offset], fill=skin)
        
        # Legs bent
        draw_muscle_limb(draw, cx - 7, cy + 10 + y_offset, cx - 11, cy + 20 + y_offset, 9, gi_white, gi_shadow, gi_white)
        draw_muscle_limb(draw, cx + 7, cy + 10 + y_offset, cx + 11, cy + 20 + y_offset, 9, gi_white, gi_shadow, gi_white)
        # Left foot - tucked during jump
        draw_pixel_rect(draw, cx - 14, cy + 20 + y_offset, 6, 4, skin_dark)
        draw_pixel_rect(draw, cx - 13, cy + 21 + y_offset, 5, 3, skin)
        draw_pixel_rect(draw, cx - 12, cy + 22 + y_offset, 3, 2, skin_light)
        # Right foot - tucked during jump
        draw_pixel_rect(draw, cx + 8, cy + 20 + y_offset, 6, 4, skin_dark)
        draw_pixel_rect(draw, cx + 9, cy + 21 + y_offset, 5, 3, skin)
        draw_pixel_rect(draw, cx + 10, cy + 22 + y_offset, 3, 2, skin_light)
    
    elif action == 'jumpkick':
        # Jump kick - realistic aerial kick with leg extension
        y_offset = [-12, -18, -10][frame % 3]
        kick_ext = [0.3, 1.0, 0.5][frame % 3]  # Kick extension progression
        
        # Head - focused on target
        draw.ellipse([cx - 8, cy - 24 + y_offset, cx + 8, cy - 11 + y_offset], fill=skin)
        draw.ellipse([cx - 7, cy - 23 + y_offset, cx + 7, cy - 12 + y_offset], fill=skin_light)
        draw.ellipse([cx - 7, cy - 24 + y_offset, cx + 7, cy - 19 + y_offset], fill=hair)
        draw_pixel_rect(draw, cx - 8, cy - 20 + y_offset, 16, 3, headband)
        draw_pixel_rect(draw, cx - 5, cy - 17 + y_offset, 2, 1, (40, 40, 40))
        draw_pixel_rect(draw, cx + 3, cy - 17 + y_offset, 2, 1, (40, 40, 40))
        
        # Torso - rotating for kick
        draw_rounded_body(draw, cx - 10, cy - 11 + y_offset, 20, 20, gi_white, gi_shadow)
        draw_pixel_rect(draw, cx - 8, cy - 10 + y_offset, 2, 18, gi_shadow)
        draw_pixel_rect(draw, cx - 2, cy - 10 + y_offset, 4, 18, gi_dark)
        draw_pixel_rect(draw, cx - 10, cy + 7 + y_offset, 20, 3, belt)
        
        # Arms - balance during aerial kick
        draw_muscle_limb(draw, cx - 10, cy - 7 + y_offset, cx - 18, cy - 10 + y_offset, 7, gi_white, gi_shadow, gi_light)
        draw_muscle_limb(draw, cx + 10, cy - 7 + y_offset, cx + 14, cy + 2 + y_offset, 7, gi_white, gi_shadow, gi_light)
        draw.ellipse([cx - 21, cy - 12 + y_offset, cx - 16, cy - 7 + y_offset], fill=skin)
        draw.ellipse([cx + 12, cy + 1 + y_offset, cx + 17, cy + 6 + y_offset], fill=skin)
        
        # Non-kicking leg - tucked
        draw_muscle_limb(draw, cx - 7, cy + 10 + y_offset, cx - 10, cy + 18 + y_offset, 9, gi_white, gi_shadow, gi_white)
        draw_pixel_rect(draw, cx - 13, cy + 18 + y_offset, 6, 4, skin_dark)
        draw_pixel_rect(draw, cx - 12, cy + 19 + y_offset, 5, 3, skin)
        
        # Kicking leg - extended forward for strike
        if kick_ext == 1.0:  # Full extension
            draw_muscle_limb(draw, cx + 7, cy + 10 + y_offset, cx + 28, cy + 2 + y_offset, 10, gi_white, gi_shadow, gi_white)
            # Kicking foot - striking position
            draw_pixel_rect(draw, cx + 26, cy - 1 + y_offset, 9, 6, skin_dark)
            draw_pixel_rect(draw, cx + 27, cy + 0 + y_offset, 8, 5, skin)
            draw_pixel_rect(draw, cx + 28, cy + 1 + y_offset, 6, 3, skin_light)
            draw_pixel_rect(draw, cx + 30, cy + 2 + y_offset, 4, 2, skin_dark)  # striking surface
            # Impact lines
            draw_pixel_rect(draw, cx + 36, cy + 2 + y_offset, 5, 1, (255, 255, 200))
            draw_pixel_rect(draw, cx + 36, cy + 4 + y_offset, 4, 1, (255, 255, 200))
        elif kick_ext == 0.5:  # Retraction
            draw_muscle_limb(draw, cx + 7, cy + 10 + y_offset, cx + 18, cy + 8 + y_offset, 9, gi_white, gi_shadow, gi_white)
            draw_pixel_rect(draw, cx + 16, cy + 7 + y_offset, 7, 5, skin_dark)
            draw_pixel_rect(draw, cx + 17, cy + 8 + y_offset, 6, 4, skin)
        else:  # Chamber
            draw_muscle_limb(draw, cx + 7, cy + 10 + y_offset, cx + 12, cy + 6 + y_offset, 9, gi_white, gi_shadow, gi_white)
            draw_muscle_limb(draw, cx + 12, cy + 6 + y_offset, cx + 20, cy + 10 + y_offset, 8, gi_white, gi_shadow, gi_white)
            draw_pixel_rect(draw, cx + 18, cy + 9 + y_offset, 6, 4, skin_dark)
            draw_pixel_rect(draw, cx + 19, cy + 10 + y_offset, 5, 3, skin)


def draw_frog_warrior(draw, cx, cy, action, frame):
    """Draw frog warrior with 16-bit pixel art style - detailed."""
    # Colors
    frog_green = (25, 95, 35)
    frog_dark = (15, 65, 25)
    frog_light = (80, 150, 90)
    belly = (160, 210, 120)
    belly_light = (190, 230, 150)
    eye_white = (245, 245, 220)
    eye_pupil = (10, 10, 10)
    eye_red = (120, 30, 30)
    mouth_dark = (20, 20, 20)
    mouth_red = (140, 40, 40)
    
    cy = cy + 10  # Lower position for squat
    
    if action == 'idle':
        # Body (wide squat) - rounded
        draw.ellipse([cx - 19, cy - 7, cx + 19, cy + 17], fill=frog_green)
        draw.ellipse([cx - 17, cy - 5, cx + 17, cy + 15], fill=frog_dark)  # back marking
        draw.ellipse([cx - 16, cy + 2, cx + 16, cy + 18], fill=belly)
        draw.ellipse([cx - 14, cy + 4, cx + 14, cy + 17], fill=belly_light)
        
        # Eyes on top (bulging rounded)
        draw.ellipse([cx - 16, cy - 19, cx - 5, cy - 8], fill=eye_white)
        draw.ellipse([cx + 5, cy - 19, cx + 16, cy - 8], fill=eye_white)
        draw.ellipse([cx - 15, cy - 18, cx - 7, cy - 10], fill=frog_green)
        draw.ellipse([cx + 7, cy - 18, cx + 15, cy - 10], fill=frog_green)
        draw_pixel_rect(draw, cx - 12, cy - 15, 3, 4, eye_pupil)  # slit pupils
        draw_pixel_rect(draw, cx + 9, cy - 15, 3, 4, eye_pupil)
        # Angry brows
        draw_pixel_rect(draw, cx - 15, cy - 16, 5, 2, eye_red)
        draw_pixel_rect(draw, cx + 10, cy - 16, 5, 2, eye_red)
        
        # Mouth (huge gaping)
        draw_rounded_body(draw, cx - 12, cy - 3, 24, 6, mouth_dark, (0, 0, 0))
        draw_pixel_rect(draw, cx - 10, cy - 1, 20, 3, mouth_red)
        
        # Front arms (small, curved)
        draw_muscle_limb(draw, cx - 18, cy + 4, cx - 22, cy + 12, 5, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 18, cy + 4, cx + 22, cy + 12, 5, frog_light, frog_dark, frog_light)
        draw.ellipse([cx - 25, cy + 12, cx - 19, cy + 17], fill=frog_green)  # webbed hands
        draw.ellipse([cx + 19, cy + 12, cx + 25, cy + 17], fill=frog_green)
        
        # Back legs (massive, wide squat, curved)
        draw_muscle_limb(draw, cx - 18, cy + 8, cx - 26, cy + 20, 11, frog_green, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 18, cy + 8, cx + 26, cy + 20, 11, frog_green, frog_dark, frog_light)
        # Webbed feet
        draw.ellipse([cx - 34, cy + 20, cx - 22, cy + 28], fill=frog_light)
        draw.ellipse([cx + 22, cy + 20, cx + 34, cy + 28], fill=frog_light)
        # Webbed toes
        draw_pixel_rect(draw, cx - 33, cy + 24, 3, 3, frog_green)
        draw_pixel_rect(draw, cx + 30, cy + 24, 3, 3, frog_green)
        
    elif action == 'walk':
        hop_y = [-4, -10, -6, 0][frame % 4]
        # Body - rounded
        draw.ellipse([cx - 13, cy - 5 + hop_y, cx + 13, cy + 13 + hop_y], fill=frog_green)
        draw.ellipse([cx - 11, cy + 1 + hop_y, cx + 11, cy + 13 + hop_y], fill=belly)
        
        # Eyes - bulging
        draw.ellipse([cx - 11, cy - 13 + hop_y, cx - 3, cy - 5 + hop_y], fill=eye_white)
        draw.ellipse([cx + 3, cy - 13 + hop_y, cx + 11, cy - 5 + hop_y], fill=eye_white)
        draw_pixel_rect(draw, cx - 8, cy - 10 + hop_y, 2, 3, eye_pupil)
        draw_pixel_rect(draw, cx + 6, cy - 10 + hop_y, 2, 3, eye_pupil)
        
        # Mouth
        draw_rounded_body(draw, cx - 8, cy - 2 + hop_y, 16, 4, mouth_dark, (0, 0, 0))
        
        # Arms - curved
        draw_muscle_limb(draw, cx - 11, cy + 2 + hop_y, cx - 14, cy + 9 + hop_y, 4, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 11, cy + 2 + hop_y, cx + 14, cy + 9 + hop_y, 4, frog_light, frog_dark, frog_light)
        
        # Legs - hopping motion with curves
        leg_ext = [0, 4, 2, 0][frame % 4]
        draw_muscle_limb(draw, cx - 8, cy + 8 + hop_y, cx - 18 - leg_ext, cy + 14 + hop_y, 7, frog_green, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 8, cy + 8 + hop_y, cx + 18 + leg_ext, cy + 14 + hop_y, 7, frog_green, frog_dark, frog_light)
        draw.ellipse([cx - 22 - leg_ext, cy + 12 + hop_y, cx - 14 - leg_ext, cy + 18 + hop_y], fill=frog_light)
        draw.ellipse([cx + 14 + leg_ext, cy + 12 + hop_y, cx + 22 + leg_ext, cy + 18 + hop_y], fill=frog_light)
        
    elif action == 'punch':
        # Body - rounded
        draw.ellipse([cx - 13, cy - 5, cx + 13, cy + 13], fill=frog_green)
        draw.ellipse([cx - 11, cy + 1, cx + 11, cy + 13], fill=belly)
        
        # Eyes - bulging
        draw.ellipse([cx - 11, cy - 13, cx - 3, cy - 5], fill=eye_white)
        draw.ellipse([cx + 3, cy - 13, cx + 11, cy - 5], fill=eye_white)
        draw_pixel_rect(draw, cx - 8, cy - 10, 2, 3, eye_pupil)
        draw_pixel_rect(draw, cx + 6, cy - 10, 2, 3, eye_pupil)
        
        # Mouth open with tongue
        draw_rounded_body(draw, cx - 8, cy - 2, 16, 5, mouth_dark, (0, 0, 0))
        if frame == 1 or frame == 3:  # Tongue lash on extension frames
            tongue_col = (220, 60, 60)
            draw_rounded_body(draw, cx + 8, cy - 1, 20, 3, tongue_col, (180, 40, 40))
            draw.ellipse([cx + 26, cy - 3, cx + 32, cy + 3], fill=tongue_col)
        
        # Arms - curved
        draw_muscle_limb(draw, cx - 11, cy + 2, cx - 14, cy + 9, 4, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 11, cy + 2, cx + 14, cy + 9, 4, frog_light, frog_dark, frog_light)
        
        # Legs - curved
        draw_muscle_limb(draw, cx - 8, cy + 8, cx - 18, cy + 14, 7, frog_green, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 8, cy + 8, cx + 18, cy + 14, 7, frog_green, frog_dark, frog_light)
        draw.ellipse([cx - 22, cy + 12, cx - 14, cy + 18], fill=frog_light)
        draw.ellipse([cx + 14, cy + 12, cx + 22, cy + 18], fill=frog_light)
        
    elif action == 'kick':
        # Body - rounded
        draw.ellipse([cx - 13, cy - 5, cx + 13, cy + 13], fill=frog_green)
        draw.ellipse([cx - 11, cy + 1, cx + 11, cy + 13], fill=belly)
        
        # Eyes - bulging
        draw.ellipse([cx - 11, cy - 13, cx - 3, cy - 5], fill=eye_white)
        draw.ellipse([cx + 3, cy - 13, cx + 11, cy - 5], fill=eye_white)
        draw_pixel_rect(draw, cx - 8, cy - 10, 2, 3, eye_pupil)
        draw_pixel_rect(draw, cx + 6, cy - 10, 2, 3, eye_pupil)
        
        # Mouth
        draw_rounded_body(draw, cx - 8, cy - 2, 16, 4, mouth_dark, (0, 0, 0))
        
        # Arms - curved
        draw_muscle_limb(draw, cx - 11, cy + 2, cx - 14, cy + 9, 4, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 11, cy + 2, cx + 14, cy + 9, 4, frog_light, frog_dark, frog_light)
        
        # Standing leg
        draw_muscle_limb(draw, cx - 8, cy + 8, cx - 18, cy + 14, 7, frog_green, frog_dark, frog_light)
        draw.ellipse([cx - 22, cy + 12, cx - 14, cy + 18], fill=frog_light)
        
        if frame == 1 or frame == 3:  # Extended kick on odd frames
            draw_muscle_limb(draw, cx + 8, cy + 8, cx + 28, cy + 6, 7, frog_green, frog_dark, frog_light)
            draw.ellipse([cx + 26, cy + 2, cx + 34, cy + 10], fill=frog_light)
        else:
            draw_muscle_limb(draw, cx + 8, cy + 8, cx + 18, cy + 14, 7, frog_green, frog_dark, frog_light)
            draw.ellipse([cx + 14, cy + 12, cx + 22, cy + 18], fill=frog_light)
            
    elif action == 'jump':
        y_offset = [-10, -16, -6][frame % 3]
        # Body - rounded
        draw.ellipse([cx - 13, cy - 5 + y_offset, cx + 13, cy + 13 + y_offset], fill=frog_green)
        draw.ellipse([cx - 11, cy + 1 + y_offset, cx + 11, cy + 13 + y_offset], fill=belly)
        
        # Eyes - bulging
        draw.ellipse([cx - 11, cy - 13 + y_offset, cx - 3, cy - 5 + y_offset], fill=eye_white)
        draw.ellipse([cx + 3, cy - 13 + y_offset, cx + 11, cy - 5 + y_offset], fill=eye_white)
        draw_pixel_rect(draw, cx - 8, cy - 10 + y_offset, 2, 3, eye_pupil)
        draw_pixel_rect(draw, cx + 6, cy - 10 + y_offset, 2, 3, eye_pupil)
        
        # Mouth
        draw_rounded_body(draw, cx - 8, cy - 2 + y_offset, 16, 4, mouth_dark, (0, 0, 0))
        
        # Arms spread - curved
        draw_muscle_limb(draw, cx - 11, cy + 2 + y_offset, cx - 16, cy + 7 + y_offset, 4, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 11, cy + 2 + y_offset, cx + 16, cy + 7 + y_offset, 4, frog_light, frog_dark, frog_light)
        
        # Legs extended - curved
        draw_muscle_limb(draw, cx - 8, cy + 8 + y_offset, cx - 20, cy + 16 + y_offset, 7, frog_green, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 8, cy + 8 + y_offset, cx + 20, cy + 16 + y_offset, 7, frog_green, frog_dark, frog_light)
        draw.ellipse([cx - 24, cy + 14 + y_offset, cx - 16, cy + 20 + y_offset], fill=frog_light)
        draw.ellipse([cx + 16, cy + 14 + y_offset, cx + 24, cy + 20 + y_offset], fill=frog_light)
    
    elif action == 'jumpkick':
        # Frog jump kick - extending both legs
        y_offset = [-10, -16, -8][frame % 3]
        
        # Body - rounded
        draw.ellipse([cx - 13, cy - 5 + y_offset, cx + 13, cy + 13 + y_offset], fill=frog_green)
        draw.ellipse([cx - 11, cy + 1 + y_offset, cx + 11, cy + 13 + y_offset], fill=belly)
        
        # Eyes - bulging
        draw.ellipse([cx - 11, cy - 13 + y_offset, cx - 3, cy - 5 + y_offset], fill=eye_white)
        draw.ellipse([cx + 3, cy - 13 + y_offset, cx + 11, cy - 5 + y_offset], fill=eye_white)
        draw_pixel_rect(draw, cx - 8, cy - 10 + y_offset, 2, 3, eye_pupil)
        draw_pixel_rect(draw, cx + 6, cy - 10 + y_offset, 2, 3, eye_pupil)
        
        # Mouth open
        draw_rounded_body(draw, cx - 8, cy - 2 + y_offset, 16, 4, mouth_dark, (0, 0, 0))
        
        # Arms back for balance
        draw_muscle_limb(draw, cx - 11, cy + 2 + y_offset, cx - 18, cy + 5 + y_offset, 4, frog_light, frog_dark, frog_light)
        draw_muscle_limb(draw, cx + 11, cy + 2 + y_offset, cx + 18, cy + 5 + y_offset, 4, frog_light, frog_dark, frog_light)
        
        # Both legs forward kicking
        if frame == 1:  # Full extension
            draw_muscle_limb(draw, cx - 8, cy + 8 + y_offset, cx - 24, cy + 4 + y_offset, 7, frog_green, frog_dark, frog_light)
            draw_muscle_limb(draw, cx + 8, cy + 8 + y_offset, cx + 26, cy + 6 + y_offset, 7, frog_green, frog_dark, frog_light)
            draw.ellipse([cx - 28, cy + 2 + y_offset, cx - 20, cy + 8 + y_offset], fill=frog_light)
            draw.ellipse([cx + 24, cy + 4 + y_offset, cx + 32, cy + 10 + y_offset], fill=frog_light)
        else:
            draw_muscle_limb(draw, cx - 8, cy + 8 + y_offset, cx - 18, cy + 14 + y_offset, 7, frog_green, frog_dark, frog_light)
            draw_muscle_limb(draw, cx + 8, cy + 8 + y_offset, cx + 18, cy + 14 + y_offset, 7, frog_green, frog_dark, frog_light)
            draw.ellipse([cx - 22, cy + 12 + y_offset, cx - 14, cy + 18 + y_offset], fill=frog_light)
            draw.ellipse([cx + 14, cy + 12 + y_offset, cx + 22, cy + 18 + y_offset], fill=frog_light)


def generate_16bit_sprite(path, fighter_type='martial'):
    """Generate 16-bit pixel art sprite strip."""
    size = 128  # Larger size for more detail
    # Expanded frame counts: alternating punches (4), alternating kicks (4), jump kick (3)
    counts = {'idle': 4, 'walk': 4, 'punch': 4, 'kick': 4, 'jump': 3, 'jumpkick': 3}
    total_frames = sum(counts.values())
    strip_w = total_frames * size
    
    img = Image.new('RGBA', (strip_w, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    i = 0
    for action, frame_count in counts.items():
        for f in range(frame_count):
            x0 = i * size
            cx = x0 + size // 2
            cy = size // 2
            
            if fighter_type == 'martial':
                draw_martial_artist(draw, cx, cy, action, f)
            elif fighter_type == 'frog':
                draw_frog_warrior(draw, cx, cy, action, f)
            
            i += 1
    
    img.save(str(path))
    print(f"Generated 16-bit {fighter_type} sprite: {path}")


def main():
    base = Path(__file__).resolve().parents[1]
    assets = base / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    
    p1_path = assets / 'player1.png'
    p2_path = assets / 'player2.png'
    
    generate_16bit_sprite(p1_path, 'martial')
    generate_16bit_sprite(p2_path, 'frog')


if __name__ == '__main__':
    main()
