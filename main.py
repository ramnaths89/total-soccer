# main.py
import pygame
import sys
from settings import SCREEN_W, SCREEN_H, FPS, BLACK


class ScreenManager:
    """
    Manages active screen. Each screen has:
      update(events, keys) -> None | str | dict
      draw(surface) -> None
      on_enter(**kwargs) -> None (optional)
    Transition dict: {'screen': 'name', ...kwargs passed to on_enter}
    """

    def __init__(self, surface):
        self.surface = surface
        self.screens = {}
        self.current = None
        # Shared config: duration and difficulty flow through here
        self.config = {'duration': 5, 'difficulty': 'Medium'}

    def register(self, name, screen):
        self.screens[name] = screen

    def switch(self, name, **kwargs):
        screen = self.screens[name]
        if hasattr(screen, 'on_enter'):
            screen.on_enter(**kwargs)
        self.current = screen

    def run(self):
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            self.surface.fill(BLACK)

            if self.current:
                result = self.current.update(events, keys)
                self.current.draw(self.surface)
                if result:
                    self._handle_transition(result)

            pygame.display.flip()
            clock.tick(FPS)

    def _handle_transition(self, result):
        if isinstance(result, str):
            self.switch(result)
        elif isinstance(result, dict):
            name = result.pop('screen')
            self.switch(name, **result)


def main():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Total Soccer')

    manager = ScreenManager(surface)

    from ui.menu import MenuScreen
    from ui.team_select import TeamSelectScreen
    from ui.settings_screen import SettingsScreen
    from modes.quick_match import QuickMatchMode
    from modes.tournament import TournamentMode
    from modes.league import LeagueMode

    manager.register('menu',        MenuScreen(manager))
    manager.register('team_select', TeamSelectScreen(manager))
    manager.register('settings',    SettingsScreen(manager))
    manager.register('quick_match', QuickMatchMode(manager))
    manager.register('tournament',  TournamentMode(manager))
    manager.register('league',      LeagueMode(manager))

    manager.switch('menu')
    manager.run()


if __name__ == '__main__':
    main()
