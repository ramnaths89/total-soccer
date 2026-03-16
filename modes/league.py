# modes/league.py
import json
import random
import itertools
import pygame
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK, WHITE, GRAY, GREEN, SCREEN_W, SCREEN_H, FPS


# ----------------------------------------------------------------
# Pure helpers
# ----------------------------------------------------------------

def calculate_standings(teams, fixtures):
    table = {t['name']: {'team': t['name'], 'p': 0, 'w': 0, 'd': 0, 'l': 0,
                          'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}
             for t in teams}
    for f in fixtures:
        if not f.get('played'):
            continue
        h, a = f['home'], f['away']
        hg, ag = f['score']
        for key, delta in [(h, (1, hg, ag)), (a, (1, ag, hg))]:
            table[key]['p'] += delta[0]
            table[key]['gf'] += delta[1]
            table[key]['ga'] += delta[2]
        if hg > ag:
            table[h]['w'] += 1; table[h]['pts'] += 3; table[a]['l'] += 1
        elif hg < ag:
            table[a]['w'] += 1; table[a]['pts'] += 3; table[h]['l'] += 1
        else:
            table[h]['d'] += 1; table[h]['pts'] += 1
            table[a]['d'] += 1; table[a]['pts'] += 1
    for r in table.values():
        r['gd'] = r['gf'] - r['ga']
    return sorted(table.values(), key=lambda r: (-r['pts'], -r['gd'], -r['gf'], r['team']))


def simulate_match_score(home_rating, away_rating):
    home_eff = home_rating + 0.5
    prob_home = 1 / (1 + 10 ** ((away_rating - home_eff) / 2.5))
    r = random.random()
    if r < prob_home * 0.65:
        hg = random.randint(1, max(1, home_rating)); ag = random.randint(0, max(0, hg - 1))
    elif r < prob_home * 0.65 + 0.25:
        g = random.randint(0, max(1, min(home_rating, away_rating))); hg = ag = g
    else:
        ag = random.randint(1, max(1, away_rating)); hg = random.randint(0, max(0, ag - 1))
    return hg, ag


def _generate_fixtures(teams):
    names = [t['name'] for t in teams]
    pairs = list(itertools.permutations(names, 2))
    random.shuffle(pairs)
    fixtures = []
    matchday = 1
    remaining = list(pairs)
    while remaining:
        used = set()
        day = []
        leftover = []
        for home, away in remaining:
            if home not in used and away not in used:
                day.append({'matchday': matchday, 'home': home, 'away': away,
                            'played': False, 'score': None})
                used.add(home); used.add(away)
            else:
                leftover.append((home, away))
        if day:
            fixtures.extend(day); matchday += 1
        remaining = leftover
        if remaining and not day:
            for home, away in remaining:
                fixtures.append({'matchday': matchday, 'home': home, 'away': away,
                                 'played': False, 'score': None})
                matchday += 1
            break
    return fixtures


class Season:
    def __init__(self, league_name, player_team, teams, duration=5, difficulty='Medium'):
        self.league_name = league_name
        self.player_team = player_team
        self.teams = teams
        self.duration = duration
        self.difficulty = difficulty
        self.fixtures = _generate_fixtures(teams)
        self.current_matchday = 1
        self.total_matchdays = max((f['matchday'] for f in self.fixtures), default=0)

    def get_player_fixture(self, matchday):
        for f in self.fixtures:
            if f['matchday'] == matchday and not f['played']:
                if f['home'] == self.player_team or f['away'] == self.player_team:
                    return f
        return None

    def simulate_matchday(self, matchday):
        """Simulate all non-player fixtures on matchday."""
        for f in self.fixtures:
            if f['matchday'] != matchday or f['played']:
                continue
            if f['home'] == self.player_team or f['away'] == self.player_team:
                continue
            hd = next((t for t in self.teams if t['name'] == f['home']), None)
            ad = next((t for t in self.teams if t['name'] == f['away']), None)
            if hd and ad:
                f['score'] = list(simulate_match_score(hd['rating'], ad['rating']))
                f['played'] = True

    def record_player_result(self, fixture, score):
        fixture['score'] = list(score)
        fixture['played'] = True

    def advance_matchday(self):
        self.current_matchday += 1


def save_season(season, path='save.json'):
    data = {
        'league': season.league_name,
        'season': 1,
        'player_team': season.player_team,
        'match_duration_minutes': season.duration,
        'difficulty': season.difficulty,
        'current_matchday': season.current_matchday,
        'total_matchdays': season.total_matchdays,
        'standings': calculate_standings(season.teams, season.fixtures),
        'fixtures': season.fixtures,
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_season(path, teams):
    """Load season state from JSON file. teams: list of team dicts for the league."""
    with open(path, 'r') as f:
        data = json.load(f)
    season = Season.__new__(Season)
    season.league_name = data['league']
    season.player_team = data['player_team']
    season.teams = teams
    season.duration = data.get('match_duration_minutes', 5)
    season.difficulty = data.get('difficulty', 'Medium')
    season.current_matchday = data['current_matchday']
    season.total_matchdays = data['total_matchdays']
    season.fixtures = data['fixtures']
    return season


# ----------------------------------------------------------------
# LeagueMode screen
# ----------------------------------------------------------------

class LeagueMode:
    def __init__(self, manager):
        self.manager = manager
        self.season = None
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'standings'
        self.player_fixture = None
        self.save_path = 'save.json'
        self.font_h = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_m = pygame.font.SysFont('Courier New', 16)
        self.font_s = pygame.font.SysFont('Arial', 14)

    def on_enter(self, league_name=None, player_team=None, teams=None,
                 duration=5, difficulty='Medium', load=False, **kwargs):
        if load:
            try:
                self.season = load_season(self.save_path, teams or [])
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return  # silently stay on menu if save file bad
        else:
            if league_name and player_team and teams:
                self.season = Season(league_name, player_team, teams, duration, difficulty)
        self.phase = 'standings'

    def update(self, events, keys):
        if self.phase == 'season_end':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    return 'menu'
            return None

        if self.phase == 'result':
            r = self.result_screen.update(events, keys)
            if r is not None:
                self._after_match()
            return None

        if self.phase == 'match' and self.match:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'menu'
            self.match.update(keys_p1=keys, keys_p2=None)
            if self.match.state == 'FULL_TIME':
                if self.player_fixture:
                    self.season.record_player_result(self.player_fixture,
                                                     list(self.match.score))
                save_season(self.season, self.save_path)
                self.phase = 'result'
                self.result_screen.on_enter(result=self.match.get_result(), next_screen=None)
            return None

        if self.phase == 'standings':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    if event.key == pygame.K_RETURN:
                        self._start_matchday()
        return None

    def _start_matchday(self):
        if not self.season:
            return
        md = self.season.current_matchday
        if md > self.season.total_matchdays:
            self.phase = 'season_end'
            return
        self.season.simulate_matchday(md)
        self.player_fixture = self.season.get_player_fixture(md)
        if self.player_fixture:
            hd = next(t for t in self.season.teams if t['name'] == self.player_fixture['home'])
            ad = next(t for t in self.season.teams if t['name'] == self.player_fixture['away'])
            is_home = (hd['name'] == self.season.player_team)
            hc = 'HUMAN_P1' if is_home else 'CPU'
            ac = 'CPU' if is_home else 'HUMAN_P1'
            self.match = Match(hd, ad, self.season.duration, hc, ac, self.season.difficulty)
            self.phase = 'match'
        else:
            # No player fixture this matchday
            self.season.advance_matchday()

    def _after_match(self):
        self.season.advance_matchday()
        save_season(self.season, self.save_path)
        if self.season.current_matchday > self.season.total_matchdays:
            self.phase = 'season_end'
        else:
            self.phase = 'standings'

    def draw(self, surface):
        surface.fill(BLACK)
        if self.phase == 'match' and self.match:
            draw_pitch(surface)
            self.match.home_team.draw(surface)
            self.match.away_team.draw(surface)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
        elif self.phase == 'result':
            self.result_screen.draw(surface)
        elif self.phase == 'standings':
            self._draw_standings(surface)
        elif self.phase == 'season_end':
            self._draw_season_end(surface)

    def _draw_standings(self, surface):
        if not self.season:
            return
        md = self.season.current_matchday
        title = self.font_h.render(
            f"{self.season.league_name}  —  Matchday {md} / {self.season.total_matchdays}",
            True, WHITE)
        surface.blit(title, (20, 10))

        header = self.font_m.render(
            f"{'#':>2}  {'TEAM':<22}{'P':>3}{'W':>3}{'D':>3}{'L':>3}{'GF':>4}{'GA':>4}{'GD':>5}{'PTS':>4}",
            True, GRAY)
        surface.blit(header, (20, 40))

        standings = calculate_standings(self.season.teams, self.season.fixtures)
        n = len(standings)
        for i, row in enumerate(standings):
            y = 60 + i * 21
            if y > SCREEN_H - 40:
                break
            color = (100, 180, 255) if i < 4 else (255, 100, 100) if i >= n - 3 else WHITE
            if row['team'] == self.season.player_team:
                pygame.draw.rect(surface, (0, 50, 0), (18, y - 2, SCREEN_W - 36, 20))
            line = self.font_m.render(
                f"{i+1:>2}  {row['team']:<22}{row['p']:>3}{row['w']:>3}{row['d']:>3}{row['l']:>3}{row['gf']:>4}{row['ga']:>4}{row['gd']:>+5}{row['pts']:>4}",
                True, color)
            surface.blit(line, (20, y))

        hint = self.font_s.render('Enter → Play matchday   Esc → Menu', True, GRAY)
        surface.blit(hint, (20, SCREEN_H - 22))

    def _draw_season_end(self, surface):
        font = pygame.font.SysFont('Arial', 36, bold=True)
        standings = calculate_standings(self.season.teams, self.season.fixtures)
        champion = standings[0]['team'] if standings else '?'
        for i, (text, color) in enumerate([
            ('SEASON COMPLETE', (255, 220, 0)),
            (f'Champion: {champion}', WHITE),
            ('', WHITE),
            ('Press any key to continue', GRAY),
        ]):
            surf = font.render(text, True, color)
            surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, 180 + i * 70)))
