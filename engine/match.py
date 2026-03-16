# engine/match.py
import pygame
from engine.ball import Ball
from engine.team import Team
from engine.ai import update_player_ai, try_kick
from settings import (
    FPS, PITCH_LEFT, PITCH_RIGHT, PITCH_TOP, PITCH_BOTTOM,
    CENTRE_X, CENTRE_Y, PLAYER_RADIUS, BALL_RADIUS, KICK_POWER_BASE,
    GOAL_PAUSE_MS, HALF_TIME_PAUSE_MS, SET_PIECE_WAIT_FRAMES,
    PLAYER_SPEED,
)


class Match:
    """
    All game logic for one match. No rendering.
    update() → None normally, or event string:
      'goal_home', 'goal_away', 'half_time', 'full_time'
    """

    def __init__(self, home_data, away_data, duration_minutes,
                 home_controlled_by, away_controlled_by, difficulty='Medium'):
        self.home_team = Team(home_data, 'home', home_controlled_by)
        self.away_team = Team(away_data, 'away', away_controlled_by)
        self.ball = Ball()
        self.difficulty = difficulty

        self.state = 'KICKOFF'
        self.score = [0, 0]
        self.total_frames = duration_minutes * 60 * FPS
        self.remaining_frames = self.total_frames
        self.second_half = False
        self.pause_frames = 0
        self.set_piece_wait = 0
        self.last_event = None

    # ----------------------------------------------------------------
    # Public update
    # ----------------------------------------------------------------

    def update(self, keys_p1=None, keys_p2=None):
        self.last_event = None

        if self.state == 'KICKOFF':
            # Auto-advance for CPU vs CPU, otherwise wait for human key press
            if (self.home_team.controlled_by == 'CPU'
                    and self.away_team.controlled_by == 'CPU'):
                self.state = 'PLAYING'
            elif keys_p1 is not None and any(keys_p1):
                self.state = 'PLAYING'

        elif self.state == 'PLAYING':
            self._handle_playing(keys_p1, keys_p2)

        elif self.state == 'GOAL_PAUSE':
            self.pause_frames -= 1
            if self.pause_frames <= 0:
                self._reset_for_kickoff()
                self.state = 'KICKOFF'

        elif self.state == 'HALF_TIME':
            self._handle_half_time()

        elif self.state == 'SET_PIECE_WAIT':
            self.set_piece_wait -= 1
            if self.set_piece_wait <= 0:
                self.state = 'PLAYING'

        return self.last_event

    # ----------------------------------------------------------------
    # PLAYING handler
    # ----------------------------------------------------------------

    def _handle_playing(self, keys_p1, keys_p2):
        # Human input
        if self.home_team.controlled_by != 'CPU':
            self._handle_human_input(self.home_team, keys_p1,
                                     pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d,
                                     pygame.K_LSHIFT,
                                     k_shoot=pygame.K_h, k_pass=pygame.K_j)
        if self.away_team.controlled_by != 'CPU':
            self._handle_human_input(self.away_team, keys_p2,
                                     pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT,
                                     pygame.K_RIGHT, pygame.K_RCTRL,
                                     k_shoot=pygame.K_KP0, k_pass=pygame.K_KP_PERIOD)

        # AI for all non-human-active players
        all_players = self.home_team.players + self.away_team.players
        for team in [self.home_team, self.away_team]:
            for player in team.players:
                if team.controlled_by == 'CPU' or not player.is_active:
                    update_player_ai(player, self.ball, team, all_players,
                                     self.difficulty, self.second_half)
                if team.controlled_by == 'CPU' and player.is_active:
                    try_kick(player, self.ball, team, self.difficulty)

        # Active player selection
        self.home_team.update_ai_mode(self.ball.pos)
        self.away_team.update_ai_mode(self.ball.pos)
        self.home_team.update_active_player(self.ball.pos)
        self.away_team.update_active_player(self.ball.pos)

        # Ball physics
        self.ball.update()

        # Goal detection (before boundary)
        self._check_and_handle_goal()
        if self.state != 'PLAYING':
            return

        # Boundary → set piece
        boundary = self.ball.check_boundary()
        if boundary:
            self._trigger_set_piece(boundary)
            return

        # Timer
        self.remaining_frames -= 1
        self._check_half_time()
        if self.state == 'PLAYING':
            self._check_full_time()

    def _handle_human_input(self, team, keys, k_up, k_down, k_left, k_right, k_kick,
                            k_shoot=None, k_pass=None):
        if keys is None:
            return
        player = team.get_active_player()
        speed = PLAYER_SPEED[player.role]
        vel = pygame.Vector2(0, 0)
        if keys[k_up]:    vel.y -= speed
        if keys[k_down]:  vel.y += speed
        if keys[k_left]:  vel.x -= speed
        if keys[k_right]: vel.x += speed
        player.vel = vel
        player.pos += vel
        # Clamp to pitch
        player.pos.x = max(PITCH_LEFT, min(PITCH_RIGHT, player.pos.x))
        player.pos.y = max(PITCH_TOP, min(PITCH_BOTTOM, player.pos.y))
        # Kick (generic direction)
        dist = (player.pos - self.ball.pos).length()
        in_range = dist < PLAYER_RADIUS + BALL_RADIUS + 4
        power = KICK_POWER_BASE * (team.rating / 5.0)
        if k_shoot and keys[k_shoot] and in_range:
            # Dedicated shoot: always aim at opponent goal
            self.ball.kick(player.get_shoot_direction(), power)
            self.ball.last_touch_team = team.side
        elif k_pass and keys[k_pass] and in_range:
            # Dedicated pass: aim at nearest teammate
            teammates = team.players
            self.ball.kick(player.get_pass_direction(teammates), power * 0.75)
            self.ball.last_touch_team = team.side
        elif keys[k_kick] and in_range:
            # Legacy kick: velocity-based direction
            self.ball.kick(player.get_kick_direction(), power)
            self.ball.last_touch_team = team.side

    # ----------------------------------------------------------------
    # Goal + timing
    # ----------------------------------------------------------------

    def _check_and_handle_goal(self):
        result = self.ball.check_goal()
        if result == 'home_scored':
            self.score[0] += 1
            self.last_event = 'goal_home'
            self.pause_frames = int(GOAL_PAUSE_MS / 1000 * FPS)
            self.state = 'GOAL_PAUSE'
        elif result == 'away_scored':
            self.score[1] += 1
            self.last_event = 'goal_away'
            self.pause_frames = int(GOAL_PAUSE_MS / 1000 * FPS)
            self.state = 'GOAL_PAUSE'

    def _check_half_time(self):
        if not self.second_half and self.remaining_frames <= self.total_frames // 2:
            self.state = 'HALF_TIME'
            self.pause_frames = int(HALF_TIME_PAUSE_MS / 1000 * FPS)
            self.last_event = 'half_time'

    def _check_full_time(self):
        if self.second_half and self.remaining_frames <= 0:
            self.state = 'FULL_TIME'
            self.last_event = 'full_time'

    def _handle_half_time(self):
        self.pause_frames -= 1
        if self.pause_frames <= 0:
            self.second_half = True
            self._reset_for_kickoff()
            self.state = 'KICKOFF'

    # ----------------------------------------------------------------
    # Set pieces
    # ----------------------------------------------------------------

    def _trigger_set_piece(self, event_type):
        last = self.ball.last_touch_team
        receiving = self.away_team if last == 'home' else self.home_team

        if event_type == 'throw_in':
            bx = max(PITCH_LEFT + 10, min(PITCH_RIGHT - 10, self.ball.pos.x))
            by = PITCH_TOP if self.ball.pos.y < CENTRE_Y else PITCH_BOTTOM
            self.ball.pos = pygame.Vector2(bx, by)
            self.ball.vel = pygame.Vector2(0, 0)
            self._set_kicker_nearest_outfield(receiving)

        elif event_type == 'corner_kick':
            cx = PITCH_LEFT  if self.ball.pos.x < CENTRE_X else PITCH_RIGHT
            cy = PITCH_TOP   if self.ball.pos.y < CENTRE_Y else PITCH_BOTTOM
            self.ball.pos = pygame.Vector2(cx, cy)
            self.ball.vel = pygame.Vector2(0, 0)
            self._set_kicker_nearest_outfield(receiving)

        elif event_type == 'goal_kick':
            defending = self.home_team if self.ball.pos.x < CENTRE_X else self.away_team
            gkx = PITCH_LEFT + 30 if defending.side == 'home' else PITCH_RIGHT - 30
            self.ball.pos = pygame.Vector2(gkx, CENTRE_Y)
            self.ball.vel = pygame.Vector2(0, 0)
            self._set_kicker_gk(defending)

        self.set_piece_wait = SET_PIECE_WAIT_FRAMES
        self.state = 'SET_PIECE_WAIT'

    def _set_kicker_nearest_outfield(self, team):
        candidates = [p for p in team.players if p.role != 'GK']
        if not candidates:
            return
        nearest = min(candidates, key=lambda p: (p.pos - self.ball.pos).length())
        for p in team.players:
            p.is_active = (p is nearest)
        team._active_idx = team.players.index(nearest)

    def _set_kicker_gk(self, team):
        gk = team.get_gk()
        for p in team.players:
            p.is_active = (p is gk)
        team._active_idx = team.players.index(gk)

    def _reset_for_kickoff(self):
        self.ball.reset()
        self.home_team.reset_to_formation(self.second_half)
        self.away_team.reset_to_formation(self.second_half)

    # ----------------------------------------------------------------
    # Result helpers
    # ----------------------------------------------------------------

    def get_result(self):
        return {
            'home_name':  self.home_team.name,
            'away_name':  self.away_team.name,
            'home_short': self.home_team.short_name,
            'away_short': self.away_team.short_name,
            'score':      list(self.score),
            'man_of_match': self._get_man_of_match(),
        }

    def _get_man_of_match(self):
        """Return description of the best active player: highest-rated team's active player."""
        if self.score[0] > self.score[1]:
            winner = self.home_team
        elif self.score[1] > self.score[0]:
            winner = self.away_team
        else:
            winner = self.home_team  # draw: credit home
        player = winner.get_active_player()
        return f"#{player.number} ({winner.short_name})"
