# Mini 2D Fighter (Pygame)

This is a small single-player vs AI prototype written with Pygame.

Run (recommended inside a virtualenv):

```fish
python3 -m pip install -r requirements.txt
python3 src/main.py
```

Controls (Player 1):
- Move: `A` / `D`
- Punch: `J`
- Kick: `K`

Files of interest:
- `src/main.py` - entrypoint
- `src/game.py` - game loop and AI hookup
- `src/fighter.py` - Fighter class (movement, attack, health)

This is a minimal prototype. The game will attempt to load `assets/character.png` as a single-row sprite strip.

To download Kenney's Platformer Art Deluxe into `assets/` (script will attempt to pick a character image):

```fish
python3 scripts/download_kenney.py --url '<DIRECT_ZIP_URL_FROM_KENNEY>'
```

Or generate a simple CC0 placeholder animated sprite (no network required):

```fish
python3 -m pip install -r requirements.txt
python3 -c "from scripts.generate_sprite import generate_placeholder; generate_placeholder('assets/character.png')"
```

If no sprite is present the game will auto-generate a placeholder at first run. You can replace `assets/character.png` with any single-row sprite strip where frame width equals the image height.
