# tests/test_ai.py
import pygame
import pytest
from engine.player import Player
from engine.ai import get_ai_state


def make_player(number=5, role='MID', side='home', x_pct=0.4, y_pct=0.5):
    return Player(number=number, role=role, team_side=side,
                  anchor_x_pct=x_pct, anchor_y_pct=y_pct)


class TestAIStateTransitions:
    """
    get_ai_state(player, player_dist, nearest_dist, ball_in_own_third, ball_in_opp_third)
    player_dist:   distance from this player to ball
    nearest_dist:  distance from the nearest player (any team) to ball
    is_nearest when player_dist <= nearest_dist + 1.0
    """

    def test_support_stays_support_not_nearest_mid_field(self):
        p = make_player(role='MID')
        p.ai_state = 'SUPPORT'
        # Not nearest, ball in middle third
        state = get_ai_state(p, 200, 50, False, False)
        assert state == 'SUPPORT'

    def test_support_to_attack_when_nearest_and_ball_in_own_third(self):
        p = make_player(role='MID')
        p.ai_state = 'SUPPORT'
        # This player IS nearest, ball in own third
        state = get_ai_state(p, 50, 50, True, False)
        assert state == 'ATTACK'

    def test_support_to_defend_when_not_nearest_and_ball_in_opp_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'SUPPORT'
        state = get_ai_state(p, 200, 50, False, True)
        assert state == 'DEFEND'

    def test_attack_stays_attack_when_nearest(self):
        p = make_player(role='MID')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 50, 50, False, False)
        assert state == 'ATTACK'

    def test_attack_to_support_when_not_nearest(self):
        p = make_player(role='MID')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 200, 50, False, False)
        assert state == 'SUPPORT'

    def test_attack_to_defend_when_ball_in_own_third_and_not_nearest(self):
        """Spec: ATTACK → DEFEND when ball crosses into own half and player not nearest."""
        p = make_player(role='DEF')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 200, 50, True, False)
        assert state == 'DEFEND'

    def test_defend_to_support_when_ball_in_opp_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'DEFEND'
        state = get_ai_state(p, 200, 50, False, True)
        assert state == 'SUPPORT'

    def test_defend_stays_defend_when_ball_in_own_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'DEFEND'
        state = get_ai_state(p, 200, 50, True, False)
        assert state == 'DEFEND'

    def test_gk_always_defend_regardless_of_ball(self):
        gk = make_player(role='GK')
        gk.ai_state = 'ATTACK'
        state = get_ai_state(gk, 50, 50, False, True)
        assert state == 'DEFEND'
