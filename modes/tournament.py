# modes/tournament.py
import pygame
import random
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK, WHITE, GRAY, GREEN, SCREEN_W, SCREEN_H, FPS, EXTRA_TIME_MINUTES


class TournamentBracket:
    """Pure logic for 16-team knockout bracket."""

    def __init__(self, teams, player_team_name):
        self.teams = list(teams)
        random.shuffle(self.teams)
        # Ensure player team is always home (index 0) in their first match
        for i, t in enumerate(self.teams):
            if t['name'] == player_team_name:
                # Swap to position 0 so player is home in match 0
                self.teams[0], self.teams[i] = self.teams[i], self.teams[0]
                break
        self.player_team_name = player_team_name
        self.champion = None
        self.current_round_matches = self._pairs(self.teams)
        self.results = [None] * len(self.current_round_matches)

    def _pairs(self, lst):
        return [(lst[i], lst[i + 1]) for i in range(0, len(lst), 2)]

    def record_result(self, idx, winner_idx):
        home, away = self.current_round_matches[idx]
        self.results[idx] = home if winner_idx == 0 else away

    def advance_round(self):
        winners = [r for r in self.results if r is not None]
        if len(winners) == 1:
            self.champion = winners[0]
            self.current_round_matches = []
        else:
            self.current_round_matches = self._pairs(winners)
            self.results = [None] * len(self.current_round_matches)

    def get_player_match_idx(self):
        for i, (h, a) in enumerate(self.current_round_matches):
            if h['name'] == self.player_team_name or a['name'] == self.player_team_name:
                return i
        return None

    @property
    def round_name(self):
        return {8: 'Round of 16', 4: 'Quarter-Finals',
                2: 'Semi-Finals', 1: 'Final'}.get(len(self.current_round_matches), '?')


class TournamentMode:
    """
    Draw resolution when scores are level after full time:
      - Play up to 2 golden goal ET periods (EXTRA_TIME_MINUTES each)
      - If still level: AWAY TEAM ADVANCES (deterministic, per spec)
    """

    def __init__(self, manager):
        self.manager = manager
        self.bracket = None
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'setup'
        self.current_match_idx = None
        self.extra_time_periods = 0
        self.duration = 5
        self.difficulty = 'Medium'
        self.player_team = None
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_s = pygame.font.SysFont('Arial', 20)

    def on_enter(self, home=None, away=None, duration=5, difficulty='Medium', **kwargs):
        from data.teams import get_all_teams
        self.duration = duration
        self.difficulty = difficulty
        player_team = home  # home = player's chosen team

        all_teams = get_all_teams()
        if player_team is None:
            player_team = random.choice(all_teams)

        others = [t for t in all_teams if t['name'] != player_team['name']]
        selected = random.sample(others, 15) + [player_team]
        self.bracket = TournamentBracket(selected, player_team['name'])
        self.player_team = player_team
        self.phase = 'round_start'

    def update(self, events, keys):
        # Key handler for terminal phases
        if self.phase in ('trophy', 'eliminated'):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    return 'menu'
            return None

        if self.phase == 'result':
            result = self.result_screen.update(events, keys)
            if result is not None:
                self._after_match_result()
            return None

        if self.phase == 'match' and self.match:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'menu'
            self.match.update(keys_p1=keys, keys_p2=None)
            if self.match.state == 'FULL_TIME':
                self._on_match_full_time()
            return None

        if self.phase == 'round_start':
            self._simulate_cpu_matches()
            self._start_player_match()

        return None

    def _on_match_full_time(self):
        score = self.match.score
        if score[0] == score[1]:
            if self.extra_time_periods < 2:
                # Another golden goal ET period
                self.extra_time_periods += 1
                self.match.remaining_frames = EXTRA_TIME_MINUTES * 60 * FPS
                self.match.state = 'KICKOFF'
            else:
                # Still level after 2 ET periods: away team advances (spec rule)
                home, away = self.bracket.current_round_matches[self.current_match_idx]
                winner_idx = 1  # away team always advances on coin-flip rule
                self.bracket.record_result(self.current_match_idx, winner_idx)
                result = self.match.get_result()
                result['coin_flip'] = True
                result['coin_winner'] = away['name']
                self.phase = 'result'
                self.result_screen.on_enter(result=result, next_screen=None)
        else:
            winner_idx = 0 if score[0] > score[1] else 1
            self.bracket.record_result(self.current_match_idx, winner_idx)
            self.phase = 'result'
            self.result_screen.on_enter(result=self.match.get_result(), next_screen=None)

    def _simulate_cpu_matches(self):
        player_idx = self.bracket.get_player_match_idx()
        for i, (home, away) in enumerate(self.bracket.current_round_matches):
            if i == player_idx or self.bracket.results[i] is not None:
                continue
            self.bracket.record_result(i, _simulate_winner(home['rating'], away['rating']))

    def _start_player_match(self):
        idx = self.bracket.get_player_match_idx()
        if idx is None:
            return
        self.current_match_idx = idx
        home, away = self.bracket.current_round_matches[idx]
        self.match = Match(home, away, self.duration,
                           'HUMAN_P1', 'CPU', self.difficulty)
        self.extra_time_periods = 0
        self.phase = 'match'

    def _after_match_result(self):
        self.bracket.advance_round()
        if self.bracket.champion:
            self.phase = 'trophy'
        elif self.bracket.get_player_match_idx() is None:
            self.phase = 'eliminated'
        else:
            self.phase = 'round_start'

    def draw(self, surface):
        if self.phase == 'result':
            self.result_screen.draw(surface)
        elif self.phase == 'match' and self.match:
            surface.fill(BLACK)
            draw_pitch(surface)
            ball_pos = self.match.ball.pos
            self.match.home_team.draw(surface, ball_pos=ball_pos)
            self.match.away_team.draw(surface, ball_pos=ball_pos)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
            rnd = self.font_s.render(self.bracket.round_name, True, (150, 150, 150))
            surface.blit(rnd, (10, 48))
        elif self.phase == 'trophy':
            self._draw_end(surface, 'TOURNAMENT WINNER!',
                           self.bracket.champion['name'] if self.bracket.champion else '?',
                           (255, 220, 0))
        elif self.phase == 'eliminated':
            self._draw_end(surface, 'ELIMINATED',
                           'Better luck next time', WHITE)

    def _draw_end(self, surface, heading, subtext, color):
        surface.fill((5, 15, 5))
        for i, (text, col) in enumerate([(heading, color), (subtext, WHITE),
                                          ('', WHITE), ('Press any key', (150, 150, 150))]):
            surf = self.font.render(text, True, col)
            surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, 180 + i * 70)))


def _simulate_winner(home_rating, away_rating):
    home_eff = home_rating + 0.5
    prob_home = 1 / (1 + 10 ** ((away_rating - home_eff) / 2.5))
    return 0 if random.random() < prob_home else 1
