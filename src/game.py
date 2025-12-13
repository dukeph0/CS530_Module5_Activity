import pygame
from fighter import Fighter
from pathlib import Path

WIDTH, HEIGHT = 1024, 640
GROUND_Y = HEIGHT - 120


class Game:
    def __init__(self):
        # init audio first
        try:
            pygame.mixer.pre_init(22050, -16, 2, 512)
            pygame.mixer.init()
        except Exception:
            pass
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mini Fighter")
        self.clock = pygame.time.Clock()
        self.player = Fighter(150, GROUND_Y, is_ai=False, controls={
            "left": pygame.K_a,
            "right": pygame.K_d,
            "punch": pygame.K_j,
            "kick": pygame.K_k,
            "jump": pygame.K_w,
        })
        self.ai = Fighter(WIDTH - 174, GROUND_Y, is_ai=True)
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
        self.timer = 60.0
        self.score_p1 = 0
        self.score_ai = 0
        self.running = True

        # audio assets: generate/load bgm and sfx
        base = Path(__file__).resolve().parents[1]
        assets = base / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        self.bgm_path = assets / 'bgm.wav'
        self.sfx_punch_path = assets / 'sfx_punch.wav'
        self.sfx_kick_path = assets / 'sfx_kick.wav'
        self._ensure_audio_assets()
        try:
            self.sfx_punch = pygame.mixer.Sound(str(self.sfx_punch_path))
            self.sfx_kick = pygame.mixer.Sound(str(self.sfx_kick_path))
        except Exception:
            self.sfx_punch = None
            self.sfx_kick = None
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
            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                    self.reset_round()

    def update(self, dt):
        if self.game_over:
            return

        # update challenge timer
        self.timer = max(0.0, self.timer - dt)

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)
        self.ai.ai_update(self.player, dt)
        self.ai.update(dt)

        # play SFX on attack start
        for f in (self.player, self.ai):
            if getattr(f, 'just_started_attack', False):
                if getattr(f, 'attack_type', 'punch') == 'kick':
                    if getattr(self, 'sfx_kick', None):
                        self.sfx_kick.play()
                else:
                    if getattr(self, 'sfx_punch', None):
                        self.sfx_punch.play()
                f.just_started_attack = False

        # simple combat: check attack rectangles with active windows
        for attacker, defender in ((self.player, self.ai), (self.ai, self.player)):
            if attacker.is_attacking:
                # determine active portion of attack (middle 50%)
                t = attacker.attack_timer
                total = attacker.attack_duration if attacker.attack_duration > 0 else 0.001
                active = (t < total * 0.75) and (t > total * 0.25)
                if active:
                    ar = attacker.attack_rect()
                    if ar.colliderect(defender.rect) and getattr(defender, 'hit_cooldown', 0) <= 0:
                        # apply damage and knockback
                        dmg = 15 if getattr(attacker, 'attack_type', 'punch') == 'kick' else 10
                        defender.take_damage(dmg)
                        # simple knockback
                        kb = 200 if getattr(attacker, 'attack_type', 'kick') == 'kick' else 100
                        if attacker.rect.centerx < defender.rect.centerx:
                            defender.x += kb * 0.05
                        else:
                            defender.x -= kb * 0.05
                        defender.vy = -180
                        defender.hit_cooldown = 0.6
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
        # generate kick: lower freq + slight noise
        if not self.sfx_kick_path.exists():
            dur = 0.18
            freq = 220
            n = int(sr * dur)
            samples = [((math.sin(2*math.pi*freq*t/sr) * (1 - t/n)) + (random.uniform(-0.1,0.1))) * 0.5 for t in range(n)]
            write_wav(self.sfx_kick_path, samples)
        # generate bgm: simple arpeggio loop ~5s
        if not self.bgm_path.exists():
            length = 5.0
            n = int(sr * length)
            notes = [220, 277, 330, 440]
            samples = []
            for t in range(n):
                idx = (t // int(sr*0.5)) % len(notes)
                f = notes[idx]
                env = 0.3 + 0.2*math.sin(2*math.pi*t/(sr*4))
                s = math.sin(2*math.pi*f*t/sr) * env
                samples.append(s)
            write_wav(self.bgm_path, samples)

    def draw(self):
        self.screen.fill((45, 45, 70))
        # ground
        pygame.draw.rect(self.screen, (30, 200, 30), (0, GROUND_Y + 50, WIDTH, HEIGHT - (GROUND_Y + 50)))
        # simple 2D shapes (challenge visual flavor)
        pygame.draw.circle(self.screen, (90, 90, 140), (WIDTH // 2, GROUND_Y + 70), 30)
        pygame.draw.rect(self.screen, (120, 80, 160), (WIDTH - 120, GROUND_Y + 60, 60, 30))

        self.player.draw(self.screen)
        self.ai.draw(self.screen)

        # HUD
        p_text = self.font.render(f"P1 HP: {self.player.health}", True, (255, 255, 255))
        a_text = self.font.render(f"AI HP: {self.ai.health}", True, (255, 255, 255))
        self.screen.blit(p_text, (20, 20))
        self.screen.blit(a_text, (WIDTH - 160, 20))

        # Score + Timer
        score_text = self.font.render(f"Score P1: {self.score_p1}  AI: {self.score_ai}", True, (255, 255, 0))
        time_text = self.font.render(f"Time: {int(self.timer)}", True, (255, 255, 255))
        self.screen.blit(score_text, (WIDTH//2 - 150, 20))
        self.screen.blit(time_text, (WIDTH//2 + 80, 20))

        # On-screen instructions
        instr1 = self.small_font.render("Controls: A/D move, W jump, J punch, K kick", True, (220, 220, 220))
        instr2 = self.small_font.render("Win by KO or high score when time ends. Press Enter/R to restart.", True, (220, 220, 220))
        self.screen.blit(instr1, (20, 50))
        self.screen.blit(instr2, (20, 72))

        # Game over banner
        if self.game_over:
            # decide winner text
            if self.player.health > self.ai.health:
                result = "Player 1 Wins!"
            elif self.ai.health > self.player.health:
                result = "AI Wins!"
            else:
                result = "Draw!"
            over = self.font.render(result + " Press Enter/R to restart.", True, (255, 200, 200))
            rect = over.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            self.screen.blit(over, rect)

        pygame.display.flip()

    def reset_round(self):
        # reset health, positions, timer, scores remain to show cumulative performance
        self.player.health = 100
        self.ai.health = 100
        self.player.x = 150
        self.player.y = GROUND_Y - self.player.HEIGHT
        self.ai.x = WIDTH - 174
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
