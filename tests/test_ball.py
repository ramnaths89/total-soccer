# tests/test_ball.py
import pygame
import pytest
from engine.ball import Ball
from settings import (
    CENTRE_X, CENTRE_Y, BALL_FRICTION, KICK_POWER_BASE,
    PITCH_LEFT, PITCH_RIGHT, PITCH_TOP, PITCH_BOTTOM,
    GOAL_TOP, GOAL_BOTTOM, PLAYER_RADIUS, BALL_RADIUS,
)


class TestBallPhysics:
    def test_ball_starts_at_centre(self):
        ball = Ball()
        assert ball.pos.x == CENTRE_X
        assert ball.pos.y == CENTRE_Y

    def test_ball_velocity_zero_at_start(self):
        ball = Ball()
        assert ball.vel.length() == 0

    def test_ball_moves_each_frame(self):
        ball = Ball()
        ball.vel = pygame.Vector2(10, 0)
        ball.update()
        assert ball.pos.x > CENTRE_X

    def test_ball_friction_reduces_velocity(self):
        ball = Ball()
        ball.vel = pygame.Vector2(10, 0)
        ball.update()
        assert abs(ball.vel.x - 10 * BALL_FRICTION) < 0.001

    def test_ball_kick_sets_velocity(self):
        ball = Ball()
        direction = pygame.Vector2(1, 0)
        ball.kick(direction, KICK_POWER_BASE)
        assert abs(ball.vel.x - KICK_POWER_BASE) < 0.1

    def test_ball_kick_normalizes_direction(self):
        ball = Ball()
        ball.kick(pygame.Vector2(3, 4), 10)  # unnormalized — length=5
        assert abs(ball.vel.length() - 10) < 0.1


class TestBallGoalDetection:
    def test_home_scores_right_goal_in_posts(self):
        """Ball crosses right goal line (away's goal) within posts → home scored."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, CENTRE_Y)
        assert ball.check_goal() == 'home_scored'

    def test_away_scores_left_goal_in_posts(self):
        """Ball crosses left goal line (home's goal) within posts → away scored."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 1, CENTRE_Y)
        assert ball.check_goal() == 'away_scored'

    def test_no_goal_ball_above_posts_right(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, GOAL_TOP - 10)
        assert ball.check_goal() is None

    def test_no_goal_ball_below_posts_right(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, GOAL_BOTTOM + 10)
        assert ball.check_goal() is None

    def test_no_goal_ball_in_pitch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        assert ball.check_goal() is None


class TestBallBoundary:
    def test_no_boundary_event_in_pitch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        assert ball.check_boundary() is None

    def test_sideline_exit_top(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, PITCH_TOP - 5)
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'throw_in'

    def test_sideline_exit_bottom(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, PITCH_BOTTOM + 5)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'throw_in'

    def test_left_byline_defending_home_last_touch(self):
        """Home defending left goal, home last touched → corner for away."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 5, 200)  # y outside goal mouth
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'corner_kick'

    def test_left_byline_attacking_away_last_touch(self):
        """Away attacked left byline, away last touched → goal kick for home."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 5, 200)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'goal_kick'

    def test_right_byline_defending_away_last_touch(self):
        """Away defending right goal, away last touched → corner for home."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 5, 200)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'corner_kick'

    def test_right_byline_attacking_home_last_touch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 5, 200)
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'goal_kick'

    def test_reset_clears_last_touch_team(self):
        ball = Ball()
        ball.last_touch_team = 'home'
        ball.reset()
        assert ball.last_touch_team is None

    def test_boundary_none_last_touch_defaults_to_goal_kick(self):
        """When last_touch_team is None, boundary defaults to goal_kick (documented behavior)."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 5, 200)
        ball.last_touch_team = None
        assert ball.check_boundary() == 'goal_kick'
