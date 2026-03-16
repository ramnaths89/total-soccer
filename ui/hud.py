# ui/hud.py
import pygame
from settings import (
    SCREEN_W, PITCH_LEFT, PITCH_RIGHT, PITCH_TOP, PITCH_BOTTOM,
    PITCH_GREEN, PITCH_GREEN_ALT, CENTRE_X, CENTRE_Y,
    CENTRE_CIRCLE_RADIUS, GOAL_DEPTH, GOAL_TOP, GOAL_BOTTOM,
    PENALTY_W, PENALTY_H, WHITE, BLACK, GRAY, FPS,
)


def draw_pitch(surface):
    """Draw the football pitch background with markings."""
    stripe_w = 40
    for x in range(PITCH_LEFT, PITCH_RIGHT, stripe_w):
        color = PITCH_GREEN if (x // stripe_w) % 2 == 0 else PITCH_GREEN_ALT
        pygame.draw.rect(surface, color,
                         (x, PITCH_TOP, min(stripe_w, PITCH_RIGHT - x),
                          PITCH_BOTTOM - PITCH_TOP))
    # Border
    pygame.draw.rect(surface, WHITE,
                     (PITCH_LEFT, PITCH_TOP,
                      PITCH_RIGHT - PITCH_LEFT, PITCH_BOTTOM - PITCH_TOP), 2)
    # Centre line + circle
    pygame.draw.line(surface, WHITE, (CENTRE_X, PITCH_TOP), (CENTRE_X, PITCH_BOTTOM), 2)
    pygame.draw.circle(surface, WHITE, (CENTRE_X, CENTRE_Y), CENTRE_CIRCLE_RADIUS, 2)
    pygame.draw.circle(surface, WHITE, (CENTRE_X, CENTRE_Y), 3)
    # Goals (left and right)
    for gx, side in [(PITCH_LEFT - GOAL_DEPTH, 'left'), (PITCH_RIGHT, 'right')]:
        pygame.draw.rect(surface, (80, 80, 80),
                         (gx, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP))
        pygame.draw.rect(surface, WHITE,
                         (gx, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP), 2)
    # Penalty areas
    pen_top = CENTRE_Y - PENALTY_H // 2
    pygame.draw.rect(surface, WHITE,
                     (PITCH_LEFT, pen_top, PENALTY_W, PENALTY_H), 2)
    pygame.draw.rect(surface, WHITE,
                     (PITCH_RIGHT - PENALTY_W, pen_top, PENALTY_W, PENALTY_H), 2)


class HUD:
    def __init__(self):
        self.font_score  = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_timer  = pygame.font.SysFont('Arial', 24)
        self.font_banner = pygame.font.SysFont('Arial', 44, bold=True)
        self.font_small  = pygame.font.SysFont('Arial', 16)

    def draw(self, surface, match):
        pygame.draw.rect(surface, BLACK, (0, 0, SCREEN_W, 44))

        home = match.home_team
        away = match.away_team
        s = match.score
        score_str = f"{home.short_name}  {s[0]} - {s[1]}  {away.short_name}"
        score_surf = self.font_score.render(score_str, True, WHITE)
        surface.blit(score_surf, score_surf.get_rect(center=(SCREEN_W // 2, 22)))

        # Timer
        secs = max(0, match.remaining_frames // FPS)
        mins, sec = divmod(secs, 60)
        half = '2nd' if match.second_half else '1st'
        timer_surf = self.font_timer.render(f"{half}  {mins:02d}:{sec:02d}", True, GRAY)
        surface.blit(timer_surf, (SCREEN_W - 115, 12))

        # State banners
        if match.state == 'KICKOFF':
            self._banner(surface, 'KICK OFF')
        elif match.state == 'HALF_TIME':
            self._banner(surface, 'HALF TIME')
        elif match.state == 'GOAL_PAUSE':
            self._banner(surface, 'GOAL !')

    def _banner(self, surface, text):
        surf = self.font_banner.render(text, True, (255, 220, 0))
        rect = surf.get_rect(center=(SCREEN_W // 2, 300))
        pygame.draw.rect(surface, BLACK, rect.inflate(24, 12))
        surface.blit(surf, rect)
