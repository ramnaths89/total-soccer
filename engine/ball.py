# engine/ball.py
import pygame
from settings import (
    CENTRE_X, CENTRE_Y, BALL_FRICTION, BALL_RADIUS,
    PITCH_LEFT, PITCH_RIGHT, PITCH_TOP, PITCH_BOTTOM,
    GOAL_TOP, GOAL_BOTTOM,
)


class Ball:
    def __init__(self):
        self.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        self.vel = pygame.Vector2(0, 0)
        self.last_touch_team = None  # 'home' or 'away'

    def reset(self):
        self.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        self.vel = pygame.Vector2(0, 0)

    def kick(self, direction, power):
        """Set ball velocity. direction is normalized internally."""
        if direction.length() > 0:
            self.vel = direction.normalize() * power

    def update(self):
        """Advance ball one frame: move + apply friction."""
        self.pos += self.vel
        self.vel *= BALL_FRICTION
        if self.vel.length() < 0.05:
            self.vel = pygame.Vector2(0, 0)

    def check_goal(self):
        """
        Returns 'home_scored' (home team scored, ball in right/away goal),
                'away_scored' (away team scored, ball in left/home goal),
                or None.

        home attacks left→right: home scores by crossing PITCH_RIGHT.
        away attacks right→left: away scores by crossing PITCH_LEFT.
        """
        in_y = GOAL_TOP <= self.pos.y <= GOAL_BOTTOM
        if not in_y:
            return None
        if self.pos.x >= PITCH_RIGHT:
            return 'home_scored'   # ball in away's (right) goal
        if self.pos.x <= PITCH_LEFT:
            return 'away_scored'   # ball in home's (left) goal
        return None

    def check_boundary(self):
        """
        Returns set-piece type or None. Only meaningful when check_goal() is None.

        Sideline (top/bottom) → 'throw_in'
        Left byline:
          home last touched → 'corner_kick' (home defending left goal, own-goal threat)
          away last touched → 'goal_kick'   (away attacked and missed)
        Right byline:
          away last touched → 'corner_kick'
          home last touched → 'goal_kick'
        """
        if self.pos.y < PITCH_TOP or self.pos.y > PITCH_BOTTOM:
            return 'throw_in'

        if self.pos.x < PITCH_LEFT:
            # Left byline — home defends here
            return 'corner_kick' if self.last_touch_team == 'home' else 'goal_kick'

        if self.pos.x > PITCH_RIGHT:
            # Right byline — away defends here
            return 'corner_kick' if self.last_touch_team == 'away' else 'goal_kick'

        return None

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255),
                           (int(self.pos.x), int(self.pos.y)), BALL_RADIUS)
        pygame.draw.circle(surface, (0, 0, 0),
                           (int(self.pos.x), int(self.pos.y)), BALL_RADIUS, 1)
