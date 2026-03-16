# engine/player.py
import pygame
from settings import (
    PITCH_LEFT, PITCH_RIGHT, PITCH_W, PITCH_H, PITCH_TOP,
    CENTRE_Y, PLAYER_SPEED, PLAYER_RADIUS,
    ACTIVE_SWITCH_HYSTERESIS, ACTIVE_SWITCH_MIN_FRAMES,
)


class Player:
    def __init__(self, number, role, team_side, anchor_x_pct, anchor_y_pct):
        self.number = number
        self.role = role
        self.team_side = team_side          # 'home' | 'away'
        self.anchor_x_pct = anchor_x_pct   # home-perspective fraction
        self.anchor_y_pct = anchor_y_pct
        self.speed = PLAYER_SPEED[role]
        self.is_active = False
        self.ai_state = 'SUPPORT'           # 'SUPPORT' | 'ATTACK' | 'DEFEND'
        self.vel = pygame.Vector2(0, 0)
        self._font = None                   # initialized lazily on first draw

        self.pos = pygame.Vector2(*self._anchor_pixels(anchor_x_pct, anchor_y_pct))

    def _anchor_pixels(self, x_pct, y_pct):
        actual_x_pct = (1.0 - x_pct) if self.team_side == 'away' else x_pct
        x = PITCH_LEFT + actual_x_pct * PITCH_W
        y = PITCH_TOP + y_pct * PITCH_H
        return x, y

    def get_anchor_pos(self, team_mode, second_half):
        """
        Return anchor position adjusted for team mode and half-time end-swap.
        OFFENSIVE: shift x_pct +20% toward opponent goal (capped at 0.90)
        DEFENSIVE: shift x_pct -20% toward own goal (floored at 0.05)
        Second half: mirror x_pct (teams swap ends).

        Note: `team_mode` must be passed from the calling Team's perspective.
        The Team class handles this — home and away teams both pass the same
        ai_mode string and the x_pct mirroring in `_anchor_pixels` handles
        the directionality.
        """
        x_pct = self.anchor_x_pct
        y_pct = self.anchor_y_pct

        if second_half:
            x_pct = 1.0 - x_pct

        if team_mode == 'OFFENSIVE':
            x_pct = min(x_pct + 0.20, 0.90)
        elif team_mode == 'DEFENSIVE':
            x_pct = max(x_pct - 0.20, 0.05)

        return pygame.Vector2(*self._anchor_pixels(x_pct, y_pct))

    def move_toward(self, target):
        diff = target - self.pos
        if diff.length() > self.speed:
            self.vel = diff.normalize() * self.speed
        else:
            self.vel = diff
        self.pos += self.vel

    def get_kick_direction(self):
        """
        Return normalized Vector2 for kick direction.
        Moving (vel >= 0.1): use current velocity direction.
        Stationary: kick toward opponent goal center.
        """
        if self.vel.length() >= 0.1:
            return self.vel.normalize()
        return self.get_shoot_direction()

    def get_shoot_direction(self):
        """Always kick toward the center of the opponent goal."""
        target = (pygame.Vector2(PITCH_RIGHT, CENTRE_Y) if self.team_side == 'home'
                  else pygame.Vector2(PITCH_LEFT, CENTRE_Y))
        diff = target - self.pos
        return diff.normalize() if diff.length() > 0 else pygame.Vector2(1, 0)

    def get_pass_direction(self, teammates):
        """Kick toward the nearest teammate (excluding self)."""
        others = [p for p in teammates if p is not self]
        if not others:
            return self.get_shoot_direction()
        nearest = min(others, key=lambda p: (p.pos - self.pos).length())
        diff = nearest.pos - self.pos
        return diff.normalize() if diff.length() > 0 else self.get_shoot_direction()

    def draw(self, surface, kit_primary, kit_secondary, ball_pos=None):
        """Draw Sensible-Soccer-style sprite: legs → body → head → number."""
        if self._font is None:
            self._font = pygame.font.SysFont(None, 10)

        kit_col   = _hex_to_rgb(kit_primary)
        short_col = _hex_to_rgb(kit_secondary)
        skin_col  = (220, 185, 140)
        hair_col  = (70,  45,  15)

        # Determine facing direction
        if self.vel.length() > 0.5:
            facing = self.vel.normalize()
        elif ball_pos is not None:
            diff = ball_pos - self.pos
            facing = diff.normalize() if diff.length() > 1 else pygame.Vector2(0, 1)
        else:
            facing = pygame.Vector2(0, 1)

        right = pygame.Vector2(-facing.y, facing.x)

        # 1. Legs / boots (behind body, kit_secondary colour)
        leg_base = self.pos - facing * 5
        lfoot    = leg_base - right * 3
        rfoot    = leg_base + right * 3
        pygame.draw.circle(surface, short_col,
                           (int(lfoot.x), int(lfoot.y)), 3)
        pygame.draw.circle(surface, short_col,
                           (int(rfoot.x), int(rfoot.y)), 3)

        # 2. Body (jersey colour)
        pos_i = (int(self.pos.x), int(self.pos.y))
        pygame.draw.circle(surface, kit_col, pos_i, 7)
        pygame.draw.circle(surface, _darken(kit_col), pos_i, 7, 1)

        # 3. Head (skin, offset forward in facing direction)
        head = self.pos + facing * 6
        pygame.draw.circle(surface, skin_col, (int(head.x), int(head.y)), 4)
        pygame.draw.circle(surface, hair_col, (int(head.x), int(head.y)), 4, 1)

        # 4. Squad number on body
        num_surf = self._font.render(str(self.number), True, (255, 255, 255))
        surface.blit(num_surf, num_surf.get_rect(center=pos_i))


def get_active_player(players, ball_pos, current_idx, hold_frames):
    """
    Return index of active player using hysteresis.
    - If hold_frames < ACTIVE_SWITCH_MIN_FRAMES, return current.
    - Only switch if challenger is closer by >= ACTIVE_SWITCH_HYSTERESIS px.
    - Tie-break: lowest index (lowest squad number).
    """
    if hold_frames < ACTIVE_SWITCH_MIN_FRAMES:
        return current_idx

    current_dist = (players[current_idx].pos - ball_pos).length()
    best_idx = current_idx
    best_dist = current_dist

    for i, p in enumerate(players):
        d = (p.pos - ball_pos).length()
        if d < best_dist - ACTIVE_SWITCH_HYSTERESIS:
            best_dist = d
            best_idx = i
        elif abs(d - best_dist) < 0.001 and i < best_idx:
            best_idx = i

    return best_idx


def _darken(rgb, factor=0.65):
    """Return a darker version of an RGB tuple."""
    return tuple(max(0, int(c * factor)) for c in rgb)


def _hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
