#!/usr/bin/env python3
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so sibling packages (scripts/) can be imported
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# If a sprite isn't present, generate a simple placeholder so the game runs out-of-box.
sprite_path = project_root / 'assets' / 'character.png'
if not sprite_path.exists():
    try:
        # import the generator from scripts package
        from scripts.generate_sprite import generate_placeholder

        print('No sprite found; generating placeholder at', sprite_path)
        generate_placeholder(str(sprite_path))
    except Exception as e:
        print('Could not generate placeholder sprite:', e)

import pygame
from game import Game


def main():
    pygame.init()
    game = Game()
    try:
        game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
