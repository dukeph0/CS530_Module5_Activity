import pygame
from fighter import Fighter
from pathlib import Path

WIDTH, HEIGHT = 1024, 640
GROUND_Y = HEIGHT - 120
PLATFORM_LEFT = 100
PLATFORM_RIGHT = 924  # width - 100


class Projectile:
    """Fireball projectile for Player 1"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.speed = 450
        self.radius = 12
        self.active = True
        self.damage = 20
        
    def update(self, dt):
        self.x += self.speed * self.direction * dt
        # deactivate if off-screen
        if self.x < -50 or self.x > WIDTH + 50:
            self.active = False
    
    def draw(self, screen):
        # draw fireball as orange/red gradient circle
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(screen, (255, 150, 0), (cx, cy), self.radius)
        pygame.draw.circle(screen, (255, 220, 0), (cx, cy), self.radius - 4)
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), self.radius - 8)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class HitSpark:
    """Visual effect for hit impacts"""
    def __init__(self, x, y, combo=1):
        self.x = x
        self.y = y
        self.life = 0.15  # Duration
        self.combo = combo
        self.size = 8 + (combo * 2)  # Bigger sparks for combos
        
    def update(self, dt):
        self.life -= dt
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / 0.15))
            size = int(self.size * (1 + (1 - self.life / 0.15)))
            # Draw expanding star burst
            cx, cy = int(self.x), int(self.y)
            colors = [(255, 255, 100), (255, 200, 50), (255, 100, 0)]
            for i, color in enumerate(colors):
                s = size - i * 3
                # Draw star points
                pygame.draw.circle(screen, color, (cx, cy), s)
                for angle in range(0, 360, 45):
                    import math
                    rad = math.radians(angle)
                    ex = cx + int(math.cos(rad) * s * 1.5)
                    ey = cy + int(math.sin(rad) * s * 1.5)
                    pygame.draw.line(screen, color, (cx, cy), (ex, ey), 3)


class Game:
    def __init__(self):
        # init audio first
        try:
            pygame.mixer.pre_init(22050, -16, 2, 512)
            pygame.mixer.init()
        except Exception:
            pass
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mini Fighter - Street Fighter 2 Style")
        self.clock = pygame.time.Clock()
        
        # Load background
        base = Path(__file__).resolve().parents[1]
        bg_path = base / 'assets' / 'bg_swamp.png'
        self.background = None
        if bg_path.exists():
            try:
                self.background = pygame.image.load(str(bg_path)).convert()
            except Exception:
                pass
        
        self.player = Fighter(150, GROUND_Y, is_ai=False, controls={
            "left": pygame.K_a,
            "right": pygame.K_d,
            "punch": pygame.K_j,
            "kick": pygame.K_k,
            "jump": pygame.K_w,
            "fireball": pygame.K_l,
        })
        self.ai = Fighter(WIDTH - 174, GROUND_Y, is_ai=True, variant="frog")
        # set player-specific sprite path
        base = Path(__file__).resolve().parents[1]
        p1 = base / 'assets' / 'player1.png'
        p2 = base / 'assets' / 'player2.png'
        if p1.exists():
            self.player.sprite_path = str(p1)
            # reload sprites now that path is set
            try:
                self.player._load_sprite()
            except Exception:
                pass
        if p2.exists():
            self.ai.sprite_path = str(p2)
            try:
                self.ai._load_sprite()
            except Exception:
                pass
        # HUD/fonts and round state
        self.small_font = pygame.font.Font(None, 24)
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.paused = False
        self.timer = 60.0
        self.score_p1 = 0
        self.score_ai = 0
        self.running = True
        self.projectiles = []
        self.hit_sparks = []  # Visual hit effects
        self.screen_shake = 0.0  # Screen shake intensity
        self.combo_display_timer = 0.0
        self.last_combo_count = 0

        # audio assets: generate/load bgm and sfx
        base = Path(__file__).resolve().parents[1]
        assets = base / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        self.bgm_path = assets / 'bgm_swamp.wav'
        self.sfx_punch_path = assets / 'sfx_punch.wav'
        self.sfx_kick_path = assets / 'sfx_kick.wav'
        self.sfx_frog_path = assets / 'sfx_frog.wav'
        self.sfx_fireball_path = assets / 'sfx_fireball.wav'
        self._ensure_audio_assets()
        try:
            self.sfx_punch = pygame.mixer.Sound(str(self.sfx_punch_path))
            self.sfx_kick = pygame.mixer.Sound(str(self.sfx_kick_path))
            self.sfx_frog = pygame.mixer.Sound(str(self.sfx_frog_path))
            self.sfx_fireball = pygame.mixer.Sound(str(self.sfx_fireball_path))
        except Exception:
            self.sfx_punch = None
            self.sfx_kick = None
            self.sfx_frog = None
            self.sfx_fireball = None
        try:
            pygame.mixer.music.load(str(self.bgm_path))
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.game_over:
                    self.paused = not self.paused
                    try:
                        if self.paused:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    except Exception:
                        pass
                if self.game_over:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                        self.reset_round()

    def update(self, dt):
        if self.game_over or self.paused:
            return

        # update challenge timer
        self.timer = max(0.0, self.timer - dt)
        
        # Update visual effects
        for spark in self.hit_sparks[:]:
            spark.update(dt)
            if spark.life <= 0:
                self.hit_sparks.remove(spark)
        
        # Decay screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 30)
        
        # Decay combo display
        if self.combo_display_timer > 0:
            self.combo_display_timer -= dt

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # check for fireball shooting (player only)
        if getattr(self.player, 'shoot_fireball', False):
            self.player.shoot_fireball = False
            direction = -1 if self.player.facing_left else 1
            proj_x = self.player.rect.centerx + (40 * direction)
            proj_y = self.player.rect.centery - 20
            self.projectiles.append(Projectile(proj_x, proj_y, direction))
            if self.sfx_fireball:
                self.sfx_fireball.play()
        
        self.player.update(dt, WIDTH, PLATFORM_LEFT, PLATFORM_RIGHT)
        self.ai.ai_update(self.player, dt)
        self.ai.update(dt, WIDTH, PLATFORM_LEFT, PLATFORM_RIGHT)
        
        # update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
            # check collision with AI
            elif proj.get_rect().colliderect(self.ai.rect) and getattr(self.ai, 'hit_cooldown', 0) <= 0:
                self.ai.take_damage(proj.damage)
                self.ai.vy = -320  # Much stronger upward knock
                kb_dir = 1 if proj.direction > 0 else -1
                self.ai.x += kb_dir * 280 * dt * 15  # Much stronger pushback
                self.ai.vx = kb_dir * 500  # Much stronger momentum
                self.ai.hit_cooldown = 0.5
                self.score_p1 += proj.damage
                proj.active = False
                self.projectiles.remove(proj)

        # play SFX on attack start
        for f in (self.player, self.ai):
            if getattr(f, 'just_started_attack', False):
                atype = getattr(f, 'attack_type', 'punch')
                if getattr(f, 'variant', 'human') == 'frog' and getattr(self, 'sfx_frog', None):
                    self.sfx_frog.play()
                else:
                    if atype == 'kick':
                        if getattr(self, 'sfx_kick', None):
                            self.sfx_kick.play()
                    else:
                        if getattr(self, 'sfx_punch', None):
                            self.sfx_punch.play()
                f.just_started_attack = False

        # simple combat: check attack rectangles with active windows
        for attacker, defender in ((self.player, self.ai), (self.ai, self.player)):
            if attacker.is_attacking:
                # determine active portion of attack - wider window (60%) to catch extended animations
                # Hits register during extension phase (frames 1-2 of 4-frame animation)
                t = attacker.attack_timer
                total = attacker.attack_duration if attacker.attack_duration > 0 else 0.001
                active = (t < total * 0.80) and (t > total * 0.20)
                if active:
                    ar = attacker.attack_rect()
                    if ar.colliderect(defender.rect) and getattr(defender, 'hit_cooldown', 0) <= 0:
                        # apply damage and enhanced knockback
                        dmg = 15 if getattr(attacker, 'attack_type', 'punch') == 'kick' else 10
                        defender.take_damage(dmg)
                        
                        # Add hit spark effect
                        spark_x = (ar.centerx + defender.rect.centerx) // 2
                        spark_y = (ar.centery + defender.rect.centery) // 2
                        combo = getattr(attacker, 'combo_count', 1)
                        self.hit_sparks.append(HitSpark(spark_x, spark_y, combo))
                        
                        # Screen shake based on combo
                        self.screen_shake = min(8.0, 3.0 + combo * 1.5)
                        
                        # Update combo display
                        if combo > 1:
                            self.combo_display_timer = 1.5
                            self.last_combo_count = combo
                        # Enhanced knockback - AI gets pushed back much more by Player 1
                        if attacker is self.player:  # Player 1 attacking AI
                            kb_x = 500 if getattr(attacker, 'attack_type', 'kick') == 'kick' else 350
                            momentum = 450 if getattr(attacker, 'attack_type', 'kick') == 'kick' else 350
                            vy_knock = -280
                        else:  # AI attacking Player 1 - normal knockback
                            kb_x = 350 if getattr(attacker, 'attack_type', 'kick') == 'kick' else 250
                            momentum = 300
                            vy_knock = -220
                        
                        if attacker.rect.centerx < defender.rect.centerx:
                            defender.x += kb_x * dt * 15  # Visible pushback
                            defender.vx = momentum  # Add momentum
                        else:
                            defender.x -= kb_x * dt * 15
                            defender.vx = -momentum
                        defender.vy = vy_knock  # Pop-up
                        defender.hit_cooldown = 0.5
                        # scoring
                        if attacker is self.player:
                            self.score_p1 += dmg
                        else:
                            self.score_ai += dmg
            # decrement hit cooldowns
            if getattr(defender, 'hit_cooldown', 0) > 0:
                defender.hit_cooldown -= dt
                if defender.hit_cooldown < 0:
                    defender.hit_cooldown = 0

        # win/loss conditions
        if self.player.health <= 0 or self.ai.health <= 0 or self.timer <= 0:
            self.game_over = True

    def _ensure_audio_assets(self):
        # simple WAV synthesis for bgm and sfx without external deps
        try:
            import wave, struct, math, random
        except Exception:
            return
        sr = 22050
        def write_wav(path, samples):
            try:
                with wave.open(str(path), 'wb') as w:
                    w.setnchannels(2)
                    w.setsampwidth(2)
                    w.setframerate(sr)
                    for s in samples:
                        v = max(-1.0, min(1.0, s))
                        val = int(v * 32767)
                        w.writeframes(struct.pack('<hh', val, val))
            except Exception:
                pass
        # generate punch: short sine blip
        if not self.sfx_punch_path.exists():
            dur = 0.12
            freq = 440
            n = int(sr * dur)
            samples = [(math.sin(2*math.pi*freq*t/sr) * (1 - t/n)) * 0.5 for t in range(n)]
            write_wav(self.sfx_punch_path, samples)
            print(f"Generated punch SFX: {self.sfx_punch_path}")
        # generate kick: lower freq + slight noise
        if not self.sfx_kick_path.exists():
            dur = 0.18
            freq = 220
            n = int(sr * dur)
            samples = [((math.sin(2*math.pi*freq*t/sr) * (1 - t/n)) + (random.uniform(-0.1,0.1))) * 0.5 for t in range(n)]
            write_wav(self.sfx_kick_path, samples)
            print(f"Generated kick SFX: {self.sfx_kick_path}")
        # generate frog croak
        if not self.sfx_frog_path.exists():
            dur = 0.25
            n = int(sr * dur)
            samples = []
            base = 160
            for t in range(n):
                env = (1 - t/n)
                s = (math.sin(2*math.pi*base*t/sr) + 0.4*math.sin(2*math.pi*80*t/sr)) * 0.5 * env
                s += random.uniform(-0.05, 0.05) * env
                samples.append(s)
            write_wav(self.sfx_frog_path, samples)
            print(f"Generated frog croak SFX: {self.sfx_frog_path}")
        # generate fireball: ascending whoosh
        if not self.sfx_fireball_path.exists():
            dur = 0.3
            n = int(sr * dur)
            samples = []
            for t in range(n):
                env = (1 - t/n) * 0.7
                freq = 200 + (t/n) * 400  # sweep from 200 to 600 Hz
                s = math.sin(2*math.pi*freq*t/sr) * env
                s += random.uniform(-0.1, 0.1) * env * 0.5
                samples.append(s)
            write_wav(self.sfx_fireball_path, samples)
            print(f"Generated fireball SFX: {self.sfx_fireball_path}")
        # generate swamp bgm: SF2-inspired energetic fighting theme
        if not self.bgm_path.exists():
            length = 8.0  # 8 second loop
            n = int(sr * length)
            samples = []
            # Main melody frequencies (SF2-inspired pentatonic scale)
            melody_notes = [262, 330, 392, 440, 392, 330, 262, 440]  # C-E-G-A pattern
            
            for t in range(n):
                # Main bass line: low driving pulses
                bass_freq = 85  # Low E
                bass = 0.3 * math.sin(2*math.pi*bass_freq*t/sr)
                
                # Rhythmic stabs (energetic martial music pattern)
                time_beat = (t / sr) % 1.0
                stab_freq = 220  # A3
                stab_env = 0.2 if (time_beat % 0.5) < 0.1 else 0
                stab = stab_env * math.sin(2*math.pi*stab_freq*t/sr)
                
                # Melodic lead - arpeggiated chord pattern
                note_idx = (t // (sr // 4)) % len(melody_notes)
                freq = melody_notes[note_idx]
                melody = 0.15 * math.sin(2*math.pi*freq*t/sr)
                
                # Swamp atmosphere: filtered noise
                noise = random.uniform(-1, 1) * 0.08
                
                # Combine: bass + rhythmic stabs + melody + noise
                s = bass + stab + melody + noise
                
                # Envelope: smooth start, consistent body
                env = min(1.0, t / (sr * 0.5))  # fade in over 0.5s
                s *= env * 0.6
                samples.append(s)
            
            write_wav(self.bgm_path, samples)
            print(f"Generated SF2-style fighting music: {self.bgm_path}")

    def draw(self):
        # Apply screen shake
        import random
        shake_x = int(random.uniform(-self.screen_shake, self.screen_shake))
        shake_y = int(random.uniform(-self.screen_shake, self.screen_shake))
        
        # Draw background instead of solid fill
        if self.background:
            self.screen.blit(self.background, (shake_x, shake_y))
        else:
            self.screen.fill((45, 45, 70))
            # ground fallback
            pygame.draw.rect(self.screen, (30, 200, 30), (shake_x, GROUND_Y + 50 + shake_y, WIDTH, HEIGHT - (GROUND_Y + 50)))
            # simple 2D shapes (challenge visual flavor)
            pygame.draw.circle(self.screen, (90, 90, 140), (WIDTH // 2 + shake_x, GROUND_Y + 70 + shake_y), 30)
            pygame.draw.rect(self.screen, (120, 80, 160), (WIDTH - 120 + shake_x, GROUND_Y + 60 + shake_y, 60, 30))

        # Create temporary surface for shake effect
        if abs(self.screen_shake) > 0.1:
            temp_surface = pygame.Surface((WIDTH, HEIGHT))
            temp_surface.fill((0, 0, 0))
            if self.background:
                temp_surface.blit(self.background, (0, 0))
            
            # Draw fighters on temp surface
            fighter_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.player.draw(fighter_surface)
            self.ai.draw(fighter_surface)
            temp_surface.blit(fighter_surface, (0, 0))
            
            # Draw temp surface with shake offset
            self.screen.blit(temp_surface, (shake_x, shake_y))
        else:
            self.player.draw(self.screen)
            self.ai.draw(self.screen)
        
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)

        # SF2-style HUD with health bars
        # P1 health bar (left side)
        bar_w = 150
        bar_h = 20
        p1_x, p1_y = 20, 20
        pygame.draw.rect(self.screen, (0, 0, 0), (p1_x, p1_y, bar_w + 4, bar_h + 4))  # black outline
        pygame.draw.rect(self.screen, (50, 50, 50), (p1_x + 2, p1_y + 2, bar_w, bar_h))  # bg
        health_w = int((self.player.health / 100.0) * bar_w)
        pygame.draw.rect(self.screen, (0, 255, 0), (p1_x + 2, p1_y + 2, health_w, bar_h))  # health
        
        # P1 name
        p1_name = self.small_font.render("MARTIAL ARTIST", True, (255, 255, 200))
        self.screen.blit(p1_name, (p1_x, p1_y - 20))
        
        # AI health bar (right side)
        ai_x = WIDTH - bar_w - 20
        pygame.draw.rect(self.screen, (0, 0, 0), (ai_x - 2, p1_y, bar_w + 4, bar_h + 4))  # black outline
        pygame.draw.rect(self.screen, (50, 50, 50), (ai_x, p1_y + 2, bar_w, bar_h))  # bg
        ai_health_w = int((self.ai.health / 100.0) * bar_w)
        pygame.draw.rect(self.screen, (255, 0, 0), (ai_x, p1_y + 2, ai_health_w, bar_h))  # health
        
        # AI name
        ai_name = self.small_font.render("FROG WARRIOR", True, (255, 100, 100))
        ai_name_rect = ai_name.get_rect(topright=(WIDTH - p1_x, p1_y - 20))
        self.screen.blit(ai_name, ai_name_rect)
        
        # Round timer - center top
        timer_text = self.font.render(f"ROUND 1 - {max(0, int(self.timer))}s", True, (255, 255, 0))
        timer_rect = timer_text.get_rect(midtop=(WIDTH // 2, 20))
        self.screen.blit(timer_text, timer_rect)

        # Score display - lower HUD
        score_text = self.small_font.render(f"P1 Score: {self.score_p1}  |  AI Score: {self.score_ai}", True, (200, 200, 255))
        score_rect = score_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.screen.blit(score_text, score_rect)

        # On-screen instructions (subtle)
        instr1 = self.small_font.render("A/D: Move  W: Jump  J: Punch  K: Kick  L: Fireball", True, (150, 150, 150))
        self.screen.blit(instr1, (20, HEIGHT - 30))
        
        # Draw hit sparks
        for spark in self.hit_sparks:
            spark.draw(self.screen)
        
        # Draw combo counter
        if self.combo_display_timer > 0 and self.last_combo_count > 1:
            combo_text = f"{self.last_combo_count} HIT COMBO!"
            combo_size = 48 + min(24, self.last_combo_count * 4)
            combo_font = pygame.font.Font(None, combo_size)
            alpha = int(255 * min(1.0, self.combo_display_timer / 0.5))
            
            # Pulsing effect
            pulse = 1.0 + (0.2 * abs((self.combo_display_timer % 0.3) - 0.15) / 0.15)
            
            combo_surf = combo_font.render(combo_text, True, (255, 255, 0))
            combo_surf.set_alpha(alpha)
            # Scale for pulse
            w, h = combo_surf.get_size()
            scaled = pygame.transform.scale(combo_surf, (int(w * pulse), int(h * pulse)))
            combo_rect = scaled.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(scaled, combo_rect)

        # Game over banner
        if self.game_over:
            # decide winner text
            if self.player.health > self.ai.health:
                result = "MARTIAL ARTIST WINS!"
                result_col = (0, 255, 0)
            elif self.ai.health > self.player.health:
                result = "FROG WARRIOR WINS!"
                result_col = (255, 0, 0)
            else:
                result = "PERFECT DRAW!"
                result_col = (255, 255, 0)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            over = pygame.font.Font(None, 72).render(result, True, result_col)
            rect = over.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            self.screen.blit(over, rect)
            
            restart_text = self.small_font.render("Press ENTER or R to restart", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw pause overlay
        if self.paused and not self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = pygame.font.Font(None, 96).render("PAUSED", True, (255, 255, 100))
            pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            self.screen.blit(pause_text, pause_rect)
            
            resume_text = self.font.render("Press ESC to resume", True, (220, 220, 220))
            resume_rect = resume_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
            self.screen.blit(resume_text, resume_rect)

        pygame.display.flip()

    def reset_round(self):
        # reset health, positions, timer, scores remain to show cumulative performance
        self.player.health = 200
        self.ai.health = 200
        self.player.x = 150
        self.player.y = GROUND_Y - self.player.HEIGHT
        self.ai.x = WIDTH - 174
        self.projectiles = []
        self.ai.y = GROUND_Y - self.ai.HEIGHT
        self.player.vx = 0
        self.player.vy = 0
        self.ai.vx = 0
        self.ai.vy = 0
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)
        self.ai.rect.x = int(self.ai.x)
        self.ai.rect.y = int(self.ai.y)
        self.timer = 60.0
        self.game_over = False
        self.paused = False
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass
        self.paused = False
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass
