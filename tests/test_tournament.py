# tests/test_tournament.py
import pytest
from modes.tournament import TournamentBracket


def _teams(n=16):
    return [{'name': f'Team {i}', 'short_name': f'T{i:02d}', 'league': 'T',
             'kit_primary': '#FF0000', 'kit_secondary': '#FFFFFF',
             'rating': (i % 5) + 1}
            for i in range(1, n + 1)]


class TestTournamentBracket:
    def test_bracket_has_16_teams(self):
        b = TournamentBracket(_teams(16), 'Team 1')
        assert len(b.teams) == 16

    def test_round_of_16_has_8_matches(self):
        b = TournamentBracket(_teams(16), 'Team 1')
        assert len(b.current_round_matches) == 8

    def test_advance_round_reduces_to_quarter_finals(self):
        b = TournamentBracket(_teams(16), 'Team 1')
        for i in range(8):
            b.record_result(i, winner_idx=0)
        b.advance_round()
        assert len(b.current_round_matches) == 4

    def test_champion_set_after_final(self):
        b = TournamentBracket(_teams(2), 'Team 1')
        b.record_result(0, winner_idx=0)
        b.advance_round()
        assert b.champion is not None
        assert b.champion['name'] == 'Team 1'

    def test_player_team_in_draw(self):
        b = TournamentBracket(_teams(16), 'Team 7')
        all_names = [t['name'] for t in b.teams]
        assert 'Team 7' in all_names

    def test_get_player_match_idx_finds_player_team(self):
        b = TournamentBracket(_teams(16), 'Team 1')
        idx = b.get_player_match_idx()
        assert idx is not None
        home, away = b.current_round_matches[idx]
        assert home['name'] == 'Team 1' or away['name'] == 'Team 1'
