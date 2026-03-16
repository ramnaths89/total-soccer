# modes/quick_match.py
import pygame
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK


class QuickMatchMode:
    """Quick match flow: match phase → result phase → back to menu."""

    def __init__(self, manager):
        self.manager = manager
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'match'
        self.multiplayer = False

    def on_enter(self, home=None, away=None, duration=5, multiplayer=False,
                 difficulty='Medium', **kwargs):
        if home is None or away is None:
            return
        self.multiplayer = multiplayer
        home_ctrl = 'HUMAN_P1'
        away_ctrl = 'HUMAN_P2' if multiplayer else 'CPU'
        self.match = Match(home, away, duration, home_ctrl, away_ctrl, difficulty)
        self.phase = 'match'

    def update(self, events, keys):
        if self.phase == 'result':
            result = self.result_screen.update(events, keys)
            if result is not None:
                return result
            return None

        if self.match is None:
            return 'menu'

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'menu'

        # P1 always gets keys; P2 gets keys only in multiplayer, else None
        keys_p2 = keys if self.multiplayer else None
        self.match.update(keys_p1=keys, keys_p2=keys_p2)

        if self.match.state == 'FULL_TIME':
            self.phase = 'result'
            self.result_screen.on_enter(result=self.match.get_result(), next_screen='menu')

        return None

    def draw(self, surface):
        if self.phase == 'result':
            self.result_screen.draw(surface)
            return
        surface.fill(BLACK)
        if self.match:
            draw_pitch(surface)
            self.match.home_team.draw(surface)
            self.match.away_team.draw(surface)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
