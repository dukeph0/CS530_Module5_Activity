import pygame
from fighter import Fighter
from pathlib import Path

WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 120


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mini Fighter")
        self.clock = pygame.time.Clock()
        self.player = Fighter(100, GROUND_Y, is_ai=False, controls={
            "left": pygame.K_a,
            "right": pygame.K_d,
            "punch": pygame.K_j,
            "kick": pygame.K_k,
            "jump": pygame.K_w,
        })
        self.ai = Fighter(600, GROUND_Y, is_ai=True)
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
        self.font = pygame.font.Font(None, 36)
        self.running = True

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

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)
        self.ai.ai_update(self.player, dt)
        self.ai.update(dt)

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
            # decrement hit cooldowns
            if getattr(defender, 'hit_cooldown', 0) > 0:
                defender.hit_cooldown -= dt
                if defender.hit_cooldown < 0:
                    defender.hit_cooldown = 0

    def draw(self):
        self.screen.fill((45, 45, 70))
        # ground
        pygame.draw.rect(self.screen, (30, 200, 30), (0, GROUND_Y + 50, WIDTH, HEIGHT - (GROUND_Y + 50)))
        self.player.draw(self.screen)
        self.ai.draw(self.screen)

        # HUD
        p_text = self.font.render(f"P1 HP: {self.player.health}", True, (255, 255, 255))
        a_text = self.font.render(f"AI HP: {self.ai.health}", True, (255, 255, 255))
        self.screen.blit(p_text, (20, 20))
        self.screen.blit(a_text, (WIDTH - 160, 20))

        pygame.display.flip()
