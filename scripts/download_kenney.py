#!/usr/bin/env python3
"""Download and extract a Kenney asset ZIP into `assets/`.

Usage:
    python3 scripts/download_kenney.py --url <direct-zip-url>

Because Kenney provides many download endpoints, please provide a direct .zip URL.
If you prefer, visit https://kenney.nl/assets/platformer-art-deluxe, copy the direct download link
and pass it with `--url`.

The script will extract the zip into `assets/platformer-art-deluxe/` and will try to copy
the first matching character/player PNG into `assets/character.png` for the game to load.
"""
import argparse
import os
import sys
import tempfile
import shutil
import zipfile
from urllib.request import urlopen


def download(url, dest_path):
    with urlopen(url) as resp:
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(resp, out)


def find_character_image(extract_dir):
    # look for likely character/player image files
    for root, dirs, files in os.walk(extract_dir):
        for name in files:
            lname = name.lower()
            if lname.endswith('.png') and ('character' in lname or 'player' in lname or 'hero' in lname):
                return os.path.join(root, name)

    # fallback: any png in a folder named 'characters' or 'character'
    for root, dirs, files in os.walk(extract_dir):
        if 'characters' in root.lower() or 'character' in root.lower():
            for name in files:
                if name.lower().endswith('.png'):
                    return os.path.join(root, name)

    # last resort: any png
    for root, dirs, files in os.walk(extract_dir):
        for name in files:
            if name.lower().endswith('.png'):
                return os.path.join(root, name)

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Direct URL to Kenney zip file (required)', required=True)
    args = parser.parse_args()

    url = args.url
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    print('Downloading:', url)
    with tempfile.TemporaryDirectory() as td:
        zip_path = os.path.join(td, 'kenney.zip')
        try:
            download(url, zip_path)
        except Exception as e:
            print('Download failed:', e)
            sys.exit(1)

        extract_dir = os.path.join(assets_dir, 'platformer-art-deluxe')
        if os.path.exists(extract_dir):
            print('Removing existing', extract_dir)
            shutil.rmtree(extract_dir)

        with zipfile.ZipFile(zip_path, 'r') as z:
            print('Extracting to', extract_dir)
            z.extractall(extract_dir)

        char_img = find_character_image(extract_dir)
        if char_img:
            dest = os.path.join(assets_dir, 'character.png')
            shutil.copy(char_img, dest)
            print('Copied character image to', dest)
        else:
            print('No character image automatically found. Inspect', extract_dir)

        # write basic assets README
        readme = os.path.join(assets_dir, 'README.txt')
        with open(readme, 'w') as f:
            f.write('Platformer Art Deluxe (Kenney) downloaded by script.\n')
            f.write('Original URL: ' + url + '\n')
            f.write('Kenney assets are provided under CC0/public domain unless otherwise noted.\n')

    print('Done.')


if __name__ == '__main__':
    main()
