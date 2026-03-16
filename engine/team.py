# engine/team.py
import pygame
from engine.player import Player, get_active_player
from settings import CENTRE_X, ACTIVE_SWITCH_MIN_FRAMES, POSSESSION_LOCK_RADIUS


# 4-4-2 formation: (role, x_pct, y_pct) — home-team perspective
FORMATION_442 = [
    ('GK',  0.05, 0.50),
    ('DEF', 0.20, 0.25),
    ('DEF', 0.20, 0.42),
    ('DEF', 0.20, 0.58),
    ('DEF', 0.20, 0.75),
    ('MID', 0.40, 0.25),
    ('MID', 0.40, 0.42),
    ('MID', 0.40, 0.58),
    ('MID', 0.40, 0.75),
    ('FWD', 0.60, 0.38),
    ('FWD', 0.60, 0.62),
]


class Team:
    def __init__(self, team_data, side, controlled_by):
        self.name          = team_data['name']
        self.short_name    = team_data['short_name']
        self.kit_primary   = team_data['kit_primary']
        self.kit_secondary = team_data['kit_secondary']
        self.rating        = team_data['rating']
        self.side          = side             # 'home' | 'away'
        self.controlled_by = controlled_by   # 'HUMAN_P1' | 'HUMAN_P2' | 'CPU'
        self.ai_mode       = 'DEFENSIVE'
        self._active_idx   = 0
        self._hold_frames  = ACTIVE_SWITCH_MIN_FRAMES

        self.players = self._create_players()
        # match_kit may be overridden by Match if kits clash with the opponent
        self.match_kit_primary   = self.kit_primary
        self.match_kit_secondary = self.kit_secondary

    def _create_players(self):
        return [Player(number=i + 1, role=role, team_side=self.side,
                       anchor_x_pct=xp, anchor_y_pct=yp)
                for i, (role, xp, yp) in enumerate(FORMATION_442)]

    def update_ai_mode(self, ball_pos):
        if self.side == 'home':
            self.ai_mode = 'OFFENSIVE' if ball_pos.x > CENTRE_X else 'DEFENSIVE'
        else:
            self.ai_mode = 'OFFENSIVE' if ball_pos.x < CENTRE_X else 'DEFENSIVE'

    def update_active_player(self, ball_pos):
        active = self.players[self._active_idx]
        # Possession lock: never auto-switch away from a player who is touching the ball
        if (active.pos - ball_pos).length() < POSSESSION_LOCK_RADIUS:
            self._hold_frames += 1
            for i, p in enumerate(self.players):
                p.is_active = (i == self._active_idx)
            return
        new_idx = get_active_player(self.players, ball_pos,
                                    self._active_idx, self._hold_frames)
        if new_idx != self._active_idx:
            self._active_idx = new_idx
            self._hold_frames = 0
        else:
            self._hold_frames += 1
        for i, p in enumerate(self.players):
            p.is_active = (i == self._active_idx)

    def get_active_player(self):
        return self.players[self._active_idx]

    def get_gk(self):
        return next(p for p in self.players if p.role == 'GK')

    def reset_to_formation(self, second_half=False):
        for player in self.players:
            anchor = player.get_anchor_pos('DEFENSIVE', second_half)
            player.pos = pygame.Vector2(anchor.x, anchor.y)
            player.vel = pygame.Vector2(0, 0)
        self._hold_frames = ACTIVE_SWITCH_MIN_FRAMES

    def draw(self, surface, ball_pos=None):
        for player in self.players:
            player.draw(surface, self.match_kit_primary, self.match_kit_secondary,
                        ball_pos=ball_pos)
            if player.is_active:
                pygame.draw.circle(surface, (255, 255, 0),
                                   (int(player.pos.x), int(player.pos.y)), 14, 2)
