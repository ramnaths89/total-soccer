# tests/test_league.py
import json
import pytest
from modes.league import Season, calculate_standings, simulate_match_score, save_season, load_season


def _teams(n=4):
    return [{'name': f'Team {i}', 'short_name': f'T0{i}', 'league': 'Test',
             'kit_primary': '#FF0000', 'kit_secondary': '#FFFFFF', 'rating': i}
            for i in range(1, n + 1)]


class TestStandings:
    def test_win_gives_three_points(self):
        teams = _teams(2)
        fixtures = [{'matchday': 1, 'home': 'Team 1', 'away': 'Team 2',
                     'played': True, 'score': [2, 1]}]
        s = calculate_standings(teams, fixtures)
        t1 = next(r for r in s if r['team'] == 'Team 1')
        assert t1['pts'] == 3

    def test_draw_gives_one_point_each(self):
        teams = _teams(2)
        fixtures = [{'matchday': 1, 'home': 'Team 1', 'away': 'Team 2',
                     'played': True, 'score': [1, 1]}]
        s = calculate_standings(teams, fixtures)
        for row in s:
            assert row['pts'] == 1

    def test_table_sorted_by_points(self):
        teams = _teams(3)
        fixtures = [
            {'matchday': 1, 'home': 'Team 1', 'away': 'Team 2', 'played': True, 'score': [2, 0]},
            {'matchday': 1, 'home': 'Team 3', 'away': 'Team 1', 'played': True, 'score': [0, 1]},
        ]
        s = calculate_standings(teams, fixtures)
        assert s[0]['pts'] >= s[1]['pts']

    def test_goal_difference_calculated(self):
        teams = _teams(2)
        fixtures = [{'matchday': 1, 'home': 'Team 1', 'away': 'Team 2',
                     'played': True, 'score': [3, 0]}]
        s = calculate_standings(teams, fixtures)
        t1 = next(r for r in s if r['team'] == 'Team 1')
        assert t1['gd'] == 3
        assert t1['gf'] == 3
        assert t1['ga'] == 0


class TestSeasonFixtures:
    def test_round_robin_fixture_count(self):
        teams = _teams(4)  # 4 teams: 4*3=12 fixtures
        season = Season('Test', 'Team 1', teams, duration=5, difficulty='Medium')
        assert len(season.fixtures) == 12

    def test_each_team_plays_home_and_away(self):
        teams = _teams(4)
        season = Season('Test', 'Team 1', teams, duration=5, difficulty='Medium')
        for team in teams:
            home_count = sum(1 for f in season.fixtures if f['home'] == team['name'])
            away_count = sum(1 for f in season.fixtures if f['away'] == team['name'])
            assert home_count == len(teams) - 1
            assert away_count == len(teams) - 1


class TestSaveLoad:
    def test_save_and_load_round_trips(self, tmp_path):
        teams = _teams(4)
        season = Season('Test', 'Team 1', teams, duration=5, difficulty='Medium')
        path = str(tmp_path / 'save.json')
        save_season(season, path)
        loaded = load_season(path, teams)
        assert loaded.player_team == 'Team 1'
        assert loaded.league_name == 'Test'
        assert len(loaded.fixtures) == len(season.fixtures)
        assert loaded.current_matchday == season.current_matchday
