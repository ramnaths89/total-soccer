# engine/ai.py
import pygame
import random
from settings import (
    PITCH_LEFT, PITCH_W, CENTRE_Y,
    PLAYER_RADIUS, BALL_RADIUS, KICK_POWER_BASE,
    PENALTY_W, PENALTY_H, PITCH_RIGHT,
    AI_DIFFICULTY,
)


def get_ai_state(player, player_dist, nearest_dist, ball_in_own_third, ball_in_opp_third):
    """
    Pure function: compute next AI state for a non-active player.

    player_dist:        distance from this player to ball
    nearest_dist:       distance of nearest player (any team) to ball
    ball_in_own_third:  ball is in this player's team's defensive third
    ball_in_opp_third:  ball is in the opponent's defensive third
    """
    # GK always defends
    if player.role == 'GK':
        return 'DEFEND'

    is_nearest = player_dist <= nearest_dist + 1.0
    current = player.ai_state

    if current == 'SUPPORT':
        if is_nearest and ball_in_own_third:
            return 'ATTACK'
        if not is_nearest and ball_in_opp_third:
            return 'DEFEND'
        return 'SUPPORT'

    if current == 'ATTACK':
        if not is_nearest and ball_in_own_third:
            return 'DEFEND'   # ball in own third, not nearest → drop back
        if not is_nearest:
            return 'SUPPORT'  # lost proximity
        return 'ATTACK'

    if current == 'DEFEND':
        if ball_in_opp_third:
            return 'SUPPORT'
        return 'DEFEND'

    return current


def update_player_ai(player, ball, team, all_players, difficulty='Medium', second_half=False):
    """Update a non-active player's state and position for one frame."""
    ball_pos = ball.pos
    player_dist = (player.pos - ball_pos).length()
    nearest_dist = min((p.pos - ball_pos).length() for p in all_players)

    third_w = PITCH_W / 3
    if team.side == 'home':
        ball_in_own_third = ball_pos.x <= PITCH_LEFT + third_w
        ball_in_opp_third = ball_pos.x >= PITCH_LEFT + 2 * third_w
    else:
        ball_in_own_third = ball_pos.x >= PITCH_LEFT + 2 * third_w
        ball_in_opp_third = ball_pos.x <= PITCH_LEFT + third_w

    player.ai_state = get_ai_state(
        player, player_dist, nearest_dist, ball_in_own_third, ball_in_opp_third)

    diff_cfg = AI_DIFFICULTY[difficulty]

    if player.role == 'GK':
        _update_gk(player, ball, team)
        return

    if player.ai_state == 'ATTACK':
        if player_dist < diff_cfg['reaction']:
            player.move_toward(ball_pos)
    elif player.ai_state == 'DEFEND':
        if player_dist < diff_cfg['reaction'] * 1.5:
            player.move_toward(ball_pos)
    else:  # SUPPORT
        anchor = player.get_anchor_pos(team.ai_mode, second_half)
        player.move_toward(anchor)


def _update_gk(player, ball, team):
    """GK stays near goal line; dives toward ball if it enters penalty area."""
    if team.side == 'home':
        pen_x_max = PITCH_LEFT + PENALTY_W
        ball_in_pen = (PITCH_LEFT <= ball.pos.x <= pen_x_max and
                       abs(ball.pos.y - CENTRE_Y) <= PENALTY_H // 2)
        goal_line_x = PITCH_LEFT + 20
    else:
        pen_x_min = PITCH_RIGHT - PENALTY_W
        ball_in_pen = (pen_x_min <= ball.pos.x <= PITCH_RIGHT and
                       abs(ball.pos.y - CENTRE_Y) <= PENALTY_H // 2)
        goal_line_x = PITCH_RIGHT - 20

    if ball_in_pen:
        player.move_toward(ball.pos)
    else:
        target_y = max(CENTRE_Y - 40, min(CENTRE_Y + 40, ball.pos.y))
        player.move_toward(pygame.Vector2(goal_line_x, target_y))


def try_kick(player, ball, team, difficulty='Medium'):
    """
    If player is in kick range, kick the ball.
    Decides shoot vs pass based on role and randomness.
    Returns True if kick was made.
    """
    dist = (player.pos - ball.pos).length()
    if dist > PLAYER_RADIUS + BALL_RADIUS + 4:
        return False

    diff_cfg  = AI_DIFFICULTY[difficulty]
    power     = KICK_POWER_BASE * (team.rating / 5.0)

    # Pass probability: midfielders and defenders pass more; forwards shoot more
    pass_chance = {'GK': 0.7, 'DEF': 0.5, 'MID': 0.4, 'FWD': 0.15}.get(player.role, 0.3)
    teammates   = [p for p in team.players if p is not player]

    if teammates and random.random() < pass_chance:
        direction = player.get_pass_direction(team.players)
        ball.kick(direction, power * 0.75)
    else:
        direction = player.get_shoot_direction()
        max_noise_deg = (1.0 - diff_cfg['accuracy']) * 40.0
        noise_deg     = random.uniform(-max_noise_deg, max_noise_deg)
        direction     = direction.rotate(noise_deg)
        ball.kick(direction, power)

    ball.last_touch_team = team.side
    return True
