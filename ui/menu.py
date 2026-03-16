# ui/menu.py
import pygame
import sys
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


class MenuScreen:
    """
    Returns dict transitions so kwargs flow cleanly to downstream screens.
    """

    def __init__(self, manager):
        self.manager = manager
        self.selected = 0
        self.font_title = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_item  = pygame.font.SysFont('Arial', 28)
        self.font_sub   = pygame.font.SysFont('Arial', 18)

    # Menu items: (label, action_fn)
    # Each action_fn returns a transition dict or string
    def _items(self):
        cfg = self.manager.config
        return [
            ('New Quick Match', lambda: {'screen': 'team_select', 'mode': 'quick_match',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('New Tournament',  lambda: {'screen': 'team_select', 'mode': 'tournament',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('New Season',      lambda: {'screen': 'team_select', 'mode': 'league',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('Load Season',     lambda: {'screen': 'league', 'load': True}),
            ('Settings',        lambda: 'settings'),
            ('Quit',            lambda: self._quit()),
        ]

    def _quit(self):
        pygame.quit()
        sys.exit()

    def on_enter(self, **kwargs):
        self.selected = 0

    def update(self, events, keys):
        items = self._items()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return items[self.selected][1]()
        return None

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_title.render('TOTAL SOCCER', True, GREEN)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 120)))
        sub = self.font_sub.render('Classic 1997 Remake  |  Python + Pygame', True, GRAY)
        surface.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 165)))

        items = self._items()
        start_y = 240
        for i, (label, _) in enumerate(items):
            y = start_y + i * 48
            if i == self.selected:
                pygame.draw.rect(surface, (0, 80, 0),
                                 (SCREEN_W // 2 - 140, y - 8, 280, 38), border_radius=4)
            color = WHITE if i == self.selected else GRAY
            text = self.font_item.render(label, True, color)
            surface.blit(text, text.get_rect(center=(SCREEN_W // 2, y + 8)))
