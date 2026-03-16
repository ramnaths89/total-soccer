# tests/test_team.py
import pygame
import pytest
from engine.team import Team
from settings import CENTRE_X, PITCH_LEFT, PITCH_W, PITCH_H, PITCH_TOP


ARSENAL = {"name": "Arsenal", "short_name": "ARS", "league": "Premier League",
           "kit_primary": "#EF0107", "kit_secondary": "#FFFFFF", "rating": 4}


class TestTeamCreation:
    def test_team_has_11_players(self):
        assert len(Team(ARSENAL, 'home', 'HUMAN_P1').players) == 11

    def test_team_formation_roles(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        roles = [p.role for p in t.players]
        assert roles.count('GK') == 1
        assert roles.count('DEF') == 4
        assert roles.count('MID') == 4
        assert roles.count('FWD') == 2

    def test_home_gk_starts_left_side(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        gk = next(p for p in t.players if p.role == 'GK')
        assert gk.pos.x < CENTRE_X

    def test_away_gk_starts_right_side(self):
        t = Team(ARSENAL, 'away', 'CPU')
        gk = next(p for p in t.players if p.role == 'GK')
        assert gk.pos.x > CENTRE_X


class TestTeamAIMode:
    def test_home_offensive_ball_right_of_centre(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.update_ai_mode(pygame.Vector2(CENTRE_X + 100, 300))
        assert t.ai_mode == 'OFFENSIVE'

    def test_home_defensive_ball_left_of_centre(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.update_ai_mode(pygame.Vector2(CENTRE_X - 100, 300))
        assert t.ai_mode == 'DEFENSIVE'

    def test_away_offensive_ball_left_of_centre(self):
        t = Team(ARSENAL, 'away', 'CPU')
        t.update_ai_mode(pygame.Vector2(CENTRE_X - 100, 300))
        assert t.ai_mode == 'OFFENSIVE'


class TestTeamReset:
    def test_reset_returns_players_to_anchors(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.players[0].pos = pygame.Vector2(700, 500)
        t.reset_to_formation(second_half=False)
        gk = next(p for p in t.players if p.role == 'GK')
        expected_x = PITCH_LEFT + 0.05 * PITCH_W
        assert abs(gk.pos.x - expected_x) < 2
