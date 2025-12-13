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
    # base dimensions; will be overridden after sprite load with scale applied
    WIDTH, HEIGHT = 60, 100

    def __init__(self, x, ground_y, is_ai=False, controls=None):
        self.scale = 1.6  # make fighters larger on screen
        self.x = x
        self.ground_y = ground_y
        self.sprite_path = None
        self.vx = 0
        # temp rect; will be resized after sprite load using scale
        self.rect = pygame.Rect(int(self.x), int(ground_y - self.HEIGHT), self.WIDTH, self.HEIGHT)
        self.health = 100
        self.is_ai = is_ai
        self.controls = controls or {}
        self.facing_left = False if not is_ai else True
        self.is_attacking = False
        self.just_started_attack = False
        self.attack_timer = 0.0
        self.attack_duration = 0.18
        self.took_hit = False

        # sprite support
        self.sprite_frames = []
        self.animator = None
        self._load_sprite()
        # anchor to ground after sprite size applied
        self.y = self.ground_y - self.rect.height
        self.rect.y = int(self.y)

    def _load_sprite(self):
        # look for the fighter-specific sprite path if provided, otherwise fallback
        base = Path(__file__).resolve().parents[1]
        if hasattr(self, 'sprite_path') and self.sprite_path:
            candidate = Path(self.sprite_path)
        else:
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
                # map frames to actions (counts must match generator)
                counts = {'idle': 4, 'walk': 4, 'punch': 3, 'kick': 3, 'jump': 3}
                idx = 0
                self.anim_map = {}
                for action, cnt in counts.items():
                    self.anim_map[action] = frames[idx:idx+cnt]
                    idx += cnt
                # default animator uses idle
                self.animator = SpriteAnimator(self.anim_map.get('idle', []), fps=8)
                # resize rect based on sprite frame and scale
                scaled_w = int(fw * self.scale)
                scaled_h = int(h * self.scale)
                self.WIDTH, self.HEIGHT = scaled_w, scaled_h
                self.rect.width = scaled_w
                self.rect.height = scaled_h
                print('Loaded', n, 'sprite frames for fighter from', candidate)
            except Exception as e:
                print('Failed to load sprite:', e)

    def handle_input(self, keys):
        self.vx = 0
        left_key = self.controls.get("left")
        right_key = self.controls.get("right")
        punch_key = self.controls.get("punch")
        kick_key = self.controls.get("kick")
        jump_key = self.controls.get("jump")

        if left_key and keys[left_key]:
            self.vx = -220
            self.facing_left = True
        if right_key and keys[right_key]:
            self.vx = 220
            self.facing_left = False
        if not self.is_attacking and punch_key and keys[punch_key]:
            self.attack_type = 'punch'
            self.just_started_attack = True
            self.start_attack()
        if not self.is_attacking and kick_key and keys[kick_key]:
            self.attack_type = 'kick'
            self.just_started_attack = True
            self.start_attack(force=True)
        if jump_key and keys[jump_key] and self.on_ground():
            # jump impulse
            if not hasattr(self, 'vy'):
                self.vy = 0.0
            self.vy = -360
            # set jump animation
            if hasattr(self, 'anim_map') and 'jump' in self.anim_map:
                self.animator.frames = self.anim_map['jump']
                self.animator.index = 0.0

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
            if not self.is_attacking:
                self.just_started_attack = True
                self.start_attack()

    def start_attack(self, force=False):
        if not self.is_attacking and self.on_ground():
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            # set attack type earlier when called with type param (kept compatibility)
            if not hasattr(self, 'attack_type') or self.attack_type is None:
                self.attack_type = 'punch' if not force else 'kick'
            # set corresponding animation
            if hasattr(self, 'anim_map') and self.attack_type in self.anim_map:
                self.animator.frames = self.anim_map[self.attack_type]
                self.animator.index = 0.0

    def attack_rect(self):
        if not self.is_attacking:
            return pygame.Rect(0, 0, 0, 0)
        # active only in the middle of attack duration
        # position differs for punch vs kick
        atype = getattr(self, 'attack_type', 'punch')
        w = int(self.rect.width * (0.55 if atype == 'punch' else 0.65))
        h = int(self.rect.height * 0.2)
        y_off = int(self.rect.height * (0.35 if atype == 'punch' else 0.55))
        if self.facing_left:
            return pygame.Rect(self.rect.left - w, self.rect.top + y_off, w, h)
        else:
            return pygame.Rect(self.rect.right, self.rect.top + y_off, w, h)

    def on_ground(self):
        # check if fighter is on stored ground level (allow small tolerance)
        height = getattr(self, 'HEIGHT', self.rect.height)
        return (self.y + height) >= (getattr(self, 'ground_y', self.y + height) - 1)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def update(self, dt):
        # horizontal
        self.x += self.vx * dt
        self.rect.x = int(self.x)

        # vertical physics
        if not hasattr(self, 'vy'):
            self.vy = 0.0
        self.vy += 900 * dt  # gravity
        self.y += self.vy * dt
        # ground clamp: use stored ground_y
        GROUND_Y = getattr(self, 'ground_y', (600 - 120))
        height = getattr(self, 'HEIGHT', self.rect.height)
        # rect bottom should not go below ground
        if self.y + height >= GROUND_Y:
            self.y = GROUND_Y - height
            self.vy = 0
        self.rect.y = int(self.y)
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_type = None

        # update animator based on state
        if hasattr(self, 'anim_map'):
            # determine current state
            if self.is_attacking:
                state = getattr(self, 'attack_type', 'punch')
            elif getattr(self, 'vy', 0) < -1:
                state = 'jump'
            elif abs(self.vx) > 10:
                state = 'walk'
            else:
                state = 'idle'

            frames = self.anim_map.get(state, self.anim_map.get('idle', []))
            if self.animator.frames is not frames:
                self.animator.frames = frames
                self.animator.index = 0.0
            # adjust fps per state
            if state == 'walk':
                self.animator.fps = 12
            elif state == 'idle':
                self.animator.fps = 6
            elif state in ('punch', 'kick'):
                self.animator.fps = 18
            elif state == 'jump':
                self.animator.fps = 10
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
