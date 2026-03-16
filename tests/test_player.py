# tests/test_player.py
import pygame
import pytest
from engine.player import Player, get_active_player
from settings import (
    PITCH_LEFT, PITCH_W, PITCH_H, PITCH_TOP,
    CENTRE_X, CENTRE_Y, PITCH_RIGHT,
    ACTIVE_SWITCH_HYSTERESIS, ACTIVE_SWITCH_MIN_FRAMES,
    PLAYER_SPEED,
)


def make_player(number=1, role='MID', side='home', x_pct=0.4, y_pct=0.5):
    return Player(number=number, role=role, team_side=side,
                  anchor_x_pct=x_pct, anchor_y_pct=y_pct)


class TestPlayerCreation:
    def test_player_has_correct_role_speed(self):
        p = make_player(role='FWD')
        assert p.speed == PLAYER_SPEED['FWD']

    def test_player_starts_at_home_anchor(self):
        p = make_player(side='home', x_pct=0.4, y_pct=0.5)
        expected_x = PITCH_LEFT + 0.4 * PITCH_W
        expected_y = PITCH_TOP + 0.5 * PITCH_H
        assert abs(p.pos.x - expected_x) < 1
        assert abs(p.pos.y - expected_y) < 1

    def test_away_player_anchor_mirrored(self):
        away = make_player(side='away', x_pct=0.2, y_pct=0.5)
        expected_x = PITCH_LEFT + (1.0 - 0.2) * PITCH_W
        assert abs(away.pos.x - expected_x) < 1


class TestActivePlayerSwitching:
    def test_select_nearest_to_ball(self):
        players = [
            make_player(number=1, x_pct=0.1, y_pct=0.5),   # far left
            make_player(number=2, x_pct=0.5, y_pct=0.5),   # centre
            make_player(number=3, x_pct=0.9, y_pct=0.5),   # far right
        ]
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.5 * PITCH_W, CENTRE_Y)
        result = get_active_player(players, ball_pos, current_idx=0, hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 1

    def test_hysteresis_keeps_current_when_margin_small(self):
        p1 = make_player(number=1, x_pct=0.40, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.41, y_pct=0.5)
        # ball just slightly closer to p2 — within hysteresis
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.42 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 0  # keeps p1

    def test_min_hold_frames_prevents_switch(self):
        p1 = make_player(number=1, x_pct=0.1, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.9, y_pct=0.5)
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.9 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES - 1)
        assert result == 0  # not enough hold frames to switch

    def test_switch_allowed_after_min_frames(self):
        p1 = make_player(number=1, x_pct=0.1, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.9, y_pct=0.5)
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.9 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 1


class TestKickDirection:
    def test_kick_direction_moving_player(self):
        p = make_player(role='MID', side='home')
        p.vel = pygame.Vector2(5, 0)
        direction = p.get_kick_direction()
        assert direction.x > 0
        assert abs(direction.y) < 0.01

    def test_kick_direction_stationary_home_aims_right_goal(self):
        p = make_player(role='MID', side='home')
        p.vel = pygame.Vector2(0, 0)
        direction = p.get_kick_direction()
        target = pygame.Vector2(PITCH_RIGHT, CENTRE_Y)
        expected = (target - p.pos).normalize()
        assert abs(direction.x - expected.x) < 0.01

    def test_kick_direction_stationary_away_aims_left_goal(self):
        p = make_player(role='MID', side='away')
        p.vel = pygame.Vector2(0, 0)
        direction = p.get_kick_direction()
        target = pygame.Vector2(PITCH_LEFT, CENTRE_Y)
        expected = (target - p.pos).normalize()
        assert abs(direction.x - expected.x) < 0.01
