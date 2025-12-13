import pygame
import os
from pathlib import Path


class SpriteAnimator:
    def __init__(self, frames, fps=8):
        self.frames = frames
        self.fps = fps
        self.index = 0.0

    def update(self, dt, loop=True):
        if not self.frames:
            return
        self.index += self.fps * dt
        if loop:
            self.index %= len(self.frames)
        else:
            if self.index >= len(self.frames):
                self.index = len(self.frames) - 1

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[int(self.index)]


class Fighter:
    WIDTH, HEIGHT = 60, 100

    def __init__(self, x, ground_y, is_ai=False, controls=None):
        self.x = x
        self.y = ground_y - self.HEIGHT
        self.vx = 0
        self.rect = pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)
        self.health = 100
        self.is_ai = is_ai
        self.controls = controls or {}
        self.facing_left = False if not is_ai else True
        self.is_attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.18
        self.took_hit = False

        # sprite support
        self.sprite_frames = []
        self.animator = None
        self._load_sprite()

    def _load_sprite(self):
        # look for a simple single-row sprite sheet at assets/character.png
        base = Path(__file__).resolve().parents[1]
        candidate = base / 'assets' / 'character.png'
        if candidate.exists():
            try:
                img = pygame.image.load(str(candidate)).convert_alpha()
                h = img.get_height()
                if h <= 0:
                    return
                # assume square frames, frame width = height
                fw = h
                n = img.get_width() // fw
                frames = []
                for i in range(n):
                    frame = img.subsurface((i * fw, 0, fw, h)).copy()
                    frames.append(frame)
                self.sprite_frames = frames
                self.animator = SpriteAnimator(self.sprite_frames, fps=8)
                print('Loaded', n, 'sprite frames for fighter from', candidate)
            except Exception as e:
                print('Failed to load sprite:', e)

    def handle_input(self, keys):
        self.vx = 0
        left_key = self.controls.get("left")
        right_key = self.controls.get("right")
        punch_key = self.controls.get("punch")
        kick_key = self.controls.get("kick")

        if left_key and keys[left_key]:
            self.vx = -220
            self.facing_left = True
        if right_key and keys[right_key]:
            self.vx = 220
            self.facing_left = False
        if punch_key and keys[punch_key]:
            self.start_attack()
        if kick_key and keys[kick_key]:
            self.start_attack(force=True)

    def ai_update(self, other, dt):
        if not self.is_ai:
            return
        # approach player, attack when close
        if other.rect.centerx < self.rect.centerx - 50:
            self.vx = -120
            self.facing_left = True
        elif other.rect.centerx > self.rect.centerx + 50:
            self.vx = 120
            self.facing_left = False
        else:
            self.vx = 0
            self.start_attack()

    def start_attack(self, force=False):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration

    def attack_rect(self):
        if not self.is_attacking:
            return pygame.Rect(0, 0, 0, 0)
        if self.facing_left:
            return pygame.Rect(self.rect.left - 30, self.rect.top + 30, 30, 20)
        else:
            return pygame.Rect(self.rect.right, self.rect.top + 30, 30, 20)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def update(self, dt):
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False

        if self.animator:
            # choose animation speed; faster when moving
            if abs(self.vx) > 0:
                self.animator.fps = 10
            else:
                self.animator.fps = 6
            self.animator.update(dt)

    def draw(self, surface):
        if self.animator and self.animator.get_frame() is not None:
            frame = self.animator.get_frame()
            # flip if facing left
            if self.facing_left:
                frame = pygame.transform.flip(frame, True, False)
            # scale frame to fit rect if needed
            fw, fh = frame.get_size()
            if (fw, fh) != (self.rect.width, self.rect.height):
                frame = pygame.transform.scale(frame, (self.rect.width, self.rect.height))
            surface.blit(frame, self.rect)
        else:
            color = (200, 80, 80) if not self.is_ai else (80, 80, 200)
            pygame.draw.rect(surface, color, self.rect)
            if self.is_attacking:
                pygame.draw.rect(surface, (255, 255, 0), self.attack_rect())
