# ui/result.py
import pygame
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY


class ResultScreen:
    """
    Displays match result. on_enter(result=dict, next_screen='menu', **extra_kwargs).
    On any key press, transitions to next_screen with extra_kwargs.
    """

    def __init__(self, manager):
        self.manager = manager
        self.result = {}
        self.next_screen = 'menu'
        self.extra_kwargs = {}
        self.font_big   = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_med   = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 20)

    def on_enter(self, result=None, next_screen='menu', **kwargs):
        self.result = result or {}
        self.next_screen = next_screen
        self.extra_kwargs = kwargs

    def update(self, events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.next_screen:
                    if self.extra_kwargs:
                        return {'screen': self.next_screen, **self.extra_kwargs}
                    return self.next_screen
        return None

    def draw(self, surface):
        surface.fill((5, 15, 5))
        r = self.result
        cx = SCREEN_W // 2

        ft = self.font_small.render('FULL TIME', True, GRAY)
        surface.blit(ft, ft.get_rect(center=(cx, 120)))

        score_str = f"{r.get('home_short','?')}  {r.get('score',[0,0])[0]} - {r.get('score',[0,0])[1]}  {r.get('away_short','?')}"
        surface.blit(self.font_big.render(score_str, True, WHITE),
                     self.font_big.render(score_str, True, WHITE).get_rect(center=(cx, 200)))

        names = f"{r.get('home_name','')}  vs  {r.get('away_name','')}"
        surface.blit(self.font_small.render(names, True, GRAY),
                     self.font_small.render(names, True, GRAY).get_rect(center=(cx, 258)))

        # Coin flip notice (tournament draws)
        if r.get('coin_flip'):
            cf = self.font_small.render(
                f"Draw — {r['coin_winner']} advances (away rule)", True, (255, 200, 0))
            surface.blit(cf, cf.get_rect(center=(cx, 300)))

        mom = self.font_small.render(
            f"Man of the Match: {r.get('man_of_match','N/A')}", True, (220, 200, 0))
        surface.blit(mom, mom.get_rect(center=(cx, 330)))

        cont = self.font_small.render('Press any key to continue', True, GRAY)
        surface.blit(cont, cont.get_rect(center=(cx, SCREEN_H - 60)))
