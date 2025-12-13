import pygame
from fighter import Fighter

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
        })
        self.ai = Fighter(600, GROUND_Y, is_ai=True)
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

        # simple combat: check attack rectangles
        for attacker, defender in ((self.player, self.ai), (self.ai, self.player)):
            if attacker.is_attacking and attacker.attack_rect().colliderect(defender.rect):
                if not defender.took_hit:
                    defender.take_damage(10)
                    defender.took_hit = True
            if not attacker.is_attacking:
                defender.took_hit = False

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
