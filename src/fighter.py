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

    def __init__(self, x, ground_y, is_ai=False, controls=None, variant="human"):
        self.scale = 2.2  # make fighters larger on screen with more detail
        self.x = x
        self.ground_y = ground_y
        self.sprite_path = None
        self.variant = variant
        self.vx = 0
        # temp rect; will be resized after sprite load using scale
        self.rect = pygame.Rect(int(self.x), int(ground_y - self.HEIGHT), self.WIDTH, self.HEIGHT)
        self.health = 300 if variant == "frog" else 200
        self.is_ai = is_ai
        self.controls = controls or {}
        self.facing_left = False if not is_ai else True
        self.is_attacking = False
        self.just_started_attack = False
        self.attack_timer = 0.0
        self.attack_duration = 0.12  # Faster for combos
        self.took_hit = False
        self.fireball_cooldown = 0.0
        self.shoot_fireball = False
        self.combo_count = 0
        self.combo_timer = 0.0
        self.last_attack_type = None

        # sprite support
        self.sprite_frames = []
        self.animator = None
        self._load_sprite()
        # anchor to ground after sprite size applied
        self.y = self.ground_y - self.rect.height
        self.rect.y = int(self.y)
        # frog hop timer
        self.hop_cooldown = 0.0

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
                counts = {'idle': 4, 'walk': 4, 'punch': 4, 'kick': 4, 'jump': 3, 'jumpkick': 3}
                idx = 0
                self.anim_map = {}
                for action, cnt in counts.items():
                    self.anim_map[action] = frames[idx:idx+cnt]
                    idx += cnt
                # default animator uses idle
                self.animator = SpriteAnimator(self.anim_map.get('idle', []), fps=12)  # Faster FPS for flashier moves
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
        fireball_key = self.controls.get("fireball")

        if left_key and keys[left_key]:
            self.vx = -220
            self.facing_left = True
        if right_key and keys[right_key]:
            self.vx = 220
            self.facing_left = False
        if not self.is_attacking and punch_key and keys[punch_key]:
            self.attack_type = 'punch'
            self.just_started_attack = True
            # Track combo
            if self.combo_timer > 0 and self.last_attack_type == 'punch':
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.combo_timer = 0.4
            self.last_attack_type = 'punch'
            self.start_attack()
        if not self.is_attacking and kick_key and keys[kick_key]:
            self.attack_type = 'kick'
            self.just_started_attack = True
            # Track combo
            if self.combo_timer > 0 and self.last_attack_type == 'kick':
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.combo_timer = 0.4
            self.last_attack_type = 'kick'
            self.start_attack(force=True)
        if jump_key and keys[jump_key] and self.on_ground():
            # jump impulse - Player 1 (human) jumps MUCH higher
            if not hasattr(self, 'vy'):
                self.vy = 0.0
            self.vy = -520 if self.variant == "human" else -420
            # set jump animation
            if hasattr(self, 'anim_map') and 'jump' in self.anim_map:
                self.animator.frames = self.anim_map['jump']
                self.animator.index = 0.0
        # fireball shooting (L key, player only)
        if not self.is_ai and keys[pygame.K_l] and self.fireball_cooldown <= 0 and self.on_ground():
            self.shoot_fireball = True
            self.fireball_cooldown = 0.8

    def ai_update(self, other, dt):
        if not self.is_ai:
            return
        # approach player, attack when close
        if other.rect.centerx < self.rect.centerx - 50:
            self.vx = -180 if self.variant == "frog" else -120
            self.facing_left = True
        elif other.rect.centerx > self.rect.centerx + 50:
            self.vx = 180 if self.variant == "frog" else 120
            self.facing_left = False
        else:
            self.vx = 0
            if not self.is_attacking:
                self.just_started_attack = True
                self.start_attack()

        # frog variant hops while moving
        if self.variant == "frog" and self.on_ground() and abs(self.vx) > 10 and self.hop_cooldown <= 0:
            if not hasattr(self, 'vy'):
                self.vy = 0.0
            self.vy = -440
            self.hop_cooldown = 0.55

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
                self.animator.fps = 14  # Faster attack animations for combos

    def attack_rect(self):
        if not self.is_attacking:
            return pygame.Rect(0, 0, 0, 0)
        # active only in the middle of attack duration
        # position differs for punch vs kick
        atype = getattr(self, 'attack_type', 'punch')
        # Much larger hitboxes to match extended punch/kick animations
        # Punch extends far forward (Ryu's extended arm), kick extends even further
        w = int(self.rect.width * (1.2 if atype == 'punch' else 1.5))
        h = int(self.rect.height * 0.35)  # Taller hitbox
        y_off = int(self.rect.height * (0.25 if atype == 'punch' else 0.45))
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

    def update(self, dt, screen_width=1024, platform_left=100, platform_right=924):
        # Check if fighter center is on the platform
        fighter_center_x = self.x + self.rect.width // 2
        on_platform = (fighter_center_x >= platform_left and fighter_center_x <= platform_right)
        
        # Apply speed penalty when off-platform (50% slower)
        speed_multiplier = 1.0 if on_platform else 0.5
        
        # horizontal
        self.x += self.vx * dt * speed_multiplier
        
        # Clamp position to keep fighter completely within screen boundaries (window edges)
        self.x = max(0, min(screen_width - self.rect.width, self.x))
        
        self.rect.x = int(self.x)
        
        # Apply friction/deceleration to knockback momentum
        if abs(self.vx) > 0:
            friction = 800 * dt
            if self.vx > 0:
                self.vx = max(0, self.vx - friction)
            else:
                self.vx = min(0, self.vx + friction)

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
        # frog hop cooldown decay
        if self.hop_cooldown > 0:
            self.hop_cooldown -= dt
            if self.hop_cooldown < 0:
                self.hop_cooldown = 0
        # fireball cooldown decay
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= dt
            if self.fireball_cooldown < 0:
                self.fireball_cooldown = 0
        
        # combo timer decay - reset combo if no attacks for 0.4s
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
                self.last_attack_type = None

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
