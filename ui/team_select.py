# ui/team_select.py
import pygame
from data.teams import TEAMS, ALL_LEAGUES, get_all_teams
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class TeamSelectScreen:
    """
    mode='quick_match': two-stage pick (home then away)
    mode='tournament' : single pick (player's team)
    mode='league'     : single pick (player's team + league carried over)
    """

    def __init__(self, manager):
        self.manager = manager
        self.font_h = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_m = pygame.font.SysFont('Arial', 20)
        self.font_s = pygame.font.SysFont('Arial', 15)

        self.mode = 'quick_match'
        self.duration = 5
        self.difficulty = 'Medium'
        self.leagues = ['All'] + ALL_LEAGUES
        self.league_idx = 0
        self.team_idx = 0
        self.team_scroll = 0
        self.stage = 'home'
        self.home_team = None

    def on_enter(self, mode='quick_match', duration=5, difficulty='Medium', **kwargs):
        self.mode = mode
        self.duration = duration
        self.difficulty = difficulty
        self.stage = 'home'
        self.home_team = None
        self.league_idx = 0
        self.team_idx = 0
        self.team_scroll = 0

    def _filtered_teams(self):
        league = self.leagues[self.league_idx]
        if league == 'All':
            return get_all_teams()
        return [{**t, 'league': league} for t in TEAMS[league]]

    @property
    def _stage_label(self):
        if self.mode == 'quick_match':
            return 'SELECT HOME TEAM' if self.stage == 'home' else 'SELECT AWAY TEAM'
        return 'SELECT YOUR TEAM'

    def update(self, events, keys):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            k = event.key
            if k == pygame.K_ESCAPE:
                return 'menu'

            teams = self._filtered_teams()
            if k == pygame.K_LEFT:
                self.league_idx = (self.league_idx - 1) % len(self.leagues)
                self.team_idx = 0; self.team_scroll = 0
            elif k == pygame.K_RIGHT:
                self.league_idx = (self.league_idx + 1) % len(self.leagues)
                self.team_idx = 0; self.team_scroll = 0
            elif k == pygame.K_UP:
                self.team_idx = max(0, self.team_idx - 1)
                if self.team_idx < self.team_scroll:
                    self.team_scroll = self.team_idx
            elif k == pygame.K_DOWN:
                self.team_idx = min(len(teams) - 1, self.team_idx + 1)
                if self.team_idx >= self.team_scroll + 12:
                    self.team_scroll += 1
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                selected = teams[self.team_idx]
                return self._on_select(selected)
        return None

    def _on_select(self, selected):
        if self.mode == 'quick_match':
            if self.stage == 'home':
                self.home_team = selected
                self.stage = 'away'
                self.team_idx = 0; self.team_scroll = 0
                return None
            else:
                return {'screen': 'quick_match',
                        'home': self.home_team,
                        'away': selected,
                        'duration': self.duration,
                        'difficulty': self.difficulty,
                        'multiplayer': False}

        elif self.mode == 'tournament':
            return {'screen': 'tournament',
                    'home': selected,
                    'duration': self.duration,
                    'difficulty': self.difficulty}

        elif self.mode == 'league':
            league = self.leagues[self.league_idx]
            if league == 'All':
                league = selected.get('league', ALL_LEAGUES[0])
            teams_in_league = [{**t, 'league': league} for t in TEAMS[league]]
            return {'screen': 'league',
                    'league_name': league,
                    'player_team': selected['name'],
                    'teams': teams_in_league,
                    'duration': self.duration,
                    'difficulty': self.difficulty}

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_h.render(self._stage_label, True, (255, 255, 255))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 20))

        # League tabs
        tx = 40
        for i, league in enumerate(self.leagues):
            col = GREEN if i == self.league_idx else GRAY
            tab = self.font_s.render(league, True, col)
            surface.blit(tab, (tx, 58))
            tx += tab.get_width() + 18

        # Team list
        teams = self._filtered_teams()
        for i, team in enumerate(teams[self.team_scroll:self.team_scroll + 12]):
            abs_idx = self.team_scroll + i
            y = 90 + i * 36
            selected = abs_idx == self.team_idx
            pygame.draw.rect(surface, (0, 60, 0) if selected else (10, 20, 10),
                             (40, y, 340, 34))
            # Kit swatch
            pygame.draw.rect(surface, _hex_to_rgb(team['kit_primary']),
                             (44, y + 4, 20, 26))
            pygame.draw.rect(surface, _hex_to_rgb(team['kit_secondary']),
                             (44, y + 17, 20, 13))
            col = (255, 255, 255) if selected else GRAY
            surface.blit(self.font_m.render(team['name'], True, col), (70, y + 8))
            stars = '* ' * team['rating'] + '  ' * (5 - team['rating'])
            surface.blit(self.font_s.render(stars.strip(), True, (220, 180, 0)), (300, y + 10))

        if self.mode == 'quick_match' and self.stage == 'away' and self.home_team:
            preview = self.font_s.render(f"Home: {self.home_team['name']}", True, (180, 255, 180))
            surface.blit(preview, (420, 90))

        hint = self.font_s.render(
            'Left/Right: League  Up/Down: Team  Enter: Select  Esc: Back', True, GRAY)
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 28))
