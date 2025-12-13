#!/usr/bin/env python3
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so sibling packages (scripts/) can be imported
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# If player sprites aren't present, generate two original archetype sprites
p1 = project_root / 'assets' / 'player1.png'
p2 = project_root / 'assets' / 'player2.png'
if not p1.exists() or not p2.exists():
    try:
        from scripts.generate_sprite import generate_pair

        print('Generating archetype sprites at', p1, 'and', p2)
        generate_pair(str(p1), str(p2))
    except Exception as e:
        print('Could not generate archetype sprites:', e)

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
