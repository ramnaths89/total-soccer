# ui/settings_screen.py
import pygame
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


class SettingsScreen:
    DURATIONS    = [1, 3, 5, 10]
    DIFFICULTIES = ['Easy', 'Medium', 'Hard']

    def __init__(self, manager):
        self.manager = manager
        self.selected_row = 0
        self.font_h = pygame.font.SysFont('Arial', 30, bold=True)
        self.font_m = pygame.font.SysFont('Arial', 22)
        self.font_s = pygame.font.SysFont('Arial', 17)

    @property
    def _duration_idx(self):
        d = self.manager.config.get('duration', 5)
        return self.DURATIONS.index(d) if d in self.DURATIONS else 2

    @property
    def _difficulty_idx(self):
        d = self.manager.config.get('difficulty', 'Medium')
        return self.DIFFICULTIES.index(d) if d in self.DIFFICULTIES else 1

    def on_enter(self, **kwargs):
        self.selected_row = 0

    def update(self, events, keys):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            k = event.key
            if k == pygame.K_ESCAPE or k == pygame.K_RETURN:
                return 'menu'
            if k == pygame.K_UP:
                self.selected_row = max(0, self.selected_row - 1)
            if k == pygame.K_DOWN:
                self.selected_row = min(1, self.selected_row + 1)
            if k == pygame.K_LEFT:
                if self.selected_row == 0:
                    idx = (self._duration_idx - 1) % len(self.DURATIONS)
                    self.manager.config['duration'] = self.DURATIONS[idx]
                else:
                    idx = (self._difficulty_idx - 1) % len(self.DIFFICULTIES)
                    self.manager.config['difficulty'] = self.DIFFICULTIES[idx]
            if k == pygame.K_RIGHT:
                if self.selected_row == 0:
                    idx = (self._duration_idx + 1) % len(self.DURATIONS)
                    self.manager.config['duration'] = self.DURATIONS[idx]
                else:
                    idx = (self._difficulty_idx + 1) % len(self.DIFFICULTIES)
                    self.manager.config['difficulty'] = self.DIFFICULTIES[idx]
        return None

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_h.render('SETTINGS', True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 60)))

        rows = [
            ('Match Duration',
             f"{self.manager.config.get('duration', 5)} min",
             ' / '.join(f"{d}m" for d in self.DURATIONS)),
            ('AI Difficulty',
             self.manager.config.get('difficulty', 'Medium'),
             ' / '.join(self.DIFFICULTIES)),
        ]
        for i, (label, value, options) in enumerate(rows):
            y = 160 + i * 80
            selected = (i == self.selected_row)
            if selected:
                pygame.draw.rect(surface, (0, 50, 0),
                                 (SCREEN_W // 2 - 220, y - 10, 440, 55), border_radius=6)
            color = WHITE if selected else GRAY
            surface.blit(self.font_m.render(label, True, color), (SCREEN_W // 2 - 200, y))
            val_surf = self.font_m.render(f'< {value} >', True, GREEN if selected else GRAY)
            surface.blit(val_surf, (SCREEN_W // 2 + 40, y))
            surface.blit(self.font_s.render(options, True, (100, 100, 100)),
                         (SCREEN_W // 2 - 200, y + 28))

        # Controls reference
        surface.blit(self.font_m.render('Controls', True, WHITE), (SCREEN_W // 2 - 200, 340))
        controls = [
            'Player 1:  WASD to move  |  Left Shift to kick',
            'Player 2:  Arrow Keys    |  Right Ctrl to kick',
            'Pause / Back:  Escape',
        ]
        for j, line in enumerate(controls):
            surface.blit(self.font_s.render(line, True, GRAY),
                         (SCREEN_W // 2 - 200, 370 + j * 26))

        hint = self.font_s.render(
            'Up/Down: Navigate   Left/Right: Change   Enter/Esc: Back', True, GRAY)
        surface.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 28)))
