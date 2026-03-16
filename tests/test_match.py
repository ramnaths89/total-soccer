# tests/test_match.py
import pygame
import pytest
from engine.match import Match
from settings import FPS, CENTRE_X, CENTRE_Y, PITCH_LEFT, PITCH_RIGHT, GOAL_TOP, GOAL_BOTTOM


ARSENAL = {"name": "Arsenal", "short_name": "ARS", "league": "Premier League",
           "kit_primary": "#EF0107", "kit_secondary": "#FFFFFF", "rating": 4}
CHELSEA = {"name": "Chelsea", "short_name": "CHE", "league": "Premier League",
           "kit_primary": "#034694", "kit_secondary": "#FFFFFF", "rating": 4}


class TestMatchInit:
    def test_starts_in_kickoff_state(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        assert m.state == 'KICKOFF'

    def test_score_starts_zero(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        assert m.score == [0, 0]

    def test_timer_set_from_duration(self):
        m = Match(ARSENAL, CHELSEA, 3, 'HUMAN_P1', 'CPU')
        assert m.total_frames == 3 * 60 * FPS

    def test_second_half_false_at_start(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        assert m.second_half is False


class TestMatchGoals:
    def test_home_goal_increments_home_score(self):
        """home_scored = home team scored (ball in right/away goal)."""
        m = Match(ARSENAL, CHELSEA, 5, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.ball.pos = pygame.Vector2(PITCH_RIGHT + 1, CENTRE_Y)
        m._check_and_handle_goal()
        assert m.score[0] == 1   # home scored

    def test_away_goal_increments_away_score(self):
        """away_scored = away team scored (ball in left/home goal)."""
        m = Match(ARSENAL, CHELSEA, 5, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.ball.pos = pygame.Vector2(PITCH_LEFT - 1, CENTRE_Y)
        m._check_and_handle_goal()
        assert m.score[1] == 1   # away scored

    def test_no_goal_ball_in_pitch(self):
        m = Match(ARSENAL, CHELSEA, 5, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.ball.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        m._check_and_handle_goal()
        assert m.score == [0, 0]

    def test_goal_transitions_to_goal_pause(self):
        m = Match(ARSENAL, CHELSEA, 5, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.ball.pos = pygame.Vector2(PITCH_RIGHT + 1, CENTRE_Y)
        m._check_and_handle_goal()
        assert m.state == 'GOAL_PAUSE'


class TestMatchTiming:
    def test_half_time_triggers_at_midpoint(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.remaining_frames = m.total_frames // 2
        m._check_half_time()
        assert m.state == 'HALF_TIME'

    def test_half_time_not_triggered_before_midpoint(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.remaining_frames = m.total_frames // 2 + 10
        m._check_half_time()
        assert m.state == 'PLAYING'

    def test_second_half_set_after_half_time_pause(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        m.state = 'HALF_TIME'
        m.pause_frames = 0
        m._handle_half_time()
        assert m.second_half is True

    def test_full_time_when_timer_reaches_zero_in_second_half(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.second_half = True
        m.remaining_frames = 0
        m._check_full_time()
        assert m.state == 'FULL_TIME'

    def test_no_full_time_in_first_half(self):
        m = Match(ARSENAL, CHELSEA, 1, 'HUMAN_P1', 'CPU')
        m.state = 'PLAYING'
        m.second_half = False
        m.remaining_frames = 0
        m._check_full_time()
        assert m.state == 'PLAYING'
