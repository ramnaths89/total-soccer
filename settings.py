# settings.py
# All game constants. Nothing is hardcoded elsewhere.

# --- Screen ---
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# --- Pitch layout (pixels) ---
PITCH_LEFT   = 60
PITCH_RIGHT  = 740
PITCH_TOP    = 50
PITCH_BOTTOM = 550
PITCH_W = PITCH_RIGHT - PITCH_LEFT   # 680
PITCH_H = PITCH_BOTTOM - PITCH_TOP   # 500

CENTRE_X = (PITCH_LEFT + PITCH_RIGHT) // 2   # 400
CENTRE_Y = (PITCH_TOP + PITCH_BOTTOM) // 2   # 300
CENTRE_CIRCLE_RADIUS = 50

# --- Goals ---
# GOAL_MOUTH = vertical opening span (top post to bottom post)
# GOAL_DEPTH = net depth behind goal line (visual only, not used for detection)
GOAL_MOUTH  = 80
GOAL_DEPTH  = 20
GOAL_TOP    = CENTRE_Y - GOAL_MOUTH // 2   # 260
GOAL_BOTTOM = CENTRE_Y + GOAL_MOUTH // 2   # 340
# Left goal net:  x=[PITCH_LEFT-GOAL_DEPTH .. PITCH_LEFT],  y=[GOAL_TOP .. GOAL_BOTTOM]
# Right goal net: x=[PITCH_RIGHT .. PITCH_RIGHT+GOAL_DEPTH], y=[GOAL_TOP .. GOAL_BOTTOM]
# Goal scored when: HOME scores → ball.x >= PITCH_RIGHT AND GOAL_TOP <= ball.y <= GOAL_BOTTOM
#                   AWAY scores → ball.x <= PITCH_LEFT  AND GOAL_TOP <= ball.y <= GOAL_BOTTOM

# --- Penalty areas ---
# Left:  x=[PITCH_LEFT .. PITCH_LEFT+PENALTY_W],    y=[CENTRE_Y-PENALTY_H//2 .. CENTRE_Y+PENALTY_H//2]
# Right: x=[PITCH_RIGHT-PENALTY_W .. PITCH_RIGHT],  y=[CENTRE_Y-PENALTY_H//2 .. CENTRE_Y+PENALTY_H//2]
PENALTY_W = 120   # horizontal depth from goal line
PENALTY_H = 200   # vertical span centered on CENTRE_Y

# --- Ball ---
BALL_RADIUS     = 6
BALL_FRICTION   = 0.97          # velocity multiplier per frame
KICK_POWER_BASE = 12            # px/frame, scaled by player rating/5
BALL_STOP_THRESHOLD = 0.05      # vel length below this → zero velocity

# --- Players ---
PLAYER_RADIUS    = 10
# Dict form used throughout (PLAYER_SPEED[role])
PLAYER_SPEED = {
    'GK':  3.0,
    'DEF': 3.5,
    'MID': 4.0,
    'FWD': 4.5,
}

# Active player switching hysteresis
ACTIVE_SWITCH_HYSTERESIS  = 30   # px: challenger must be this much closer to trigger switch
ACTIVE_SWITCH_MIN_FRAMES  = 10   # frames to hold before re-evaluating

# --- Match timing ---
DEFAULT_MATCH_MINUTES  = 5
GOAL_PAUSE_MS          = 2000   # ms pause after goal
HALF_TIME_PAUSE_MS     = 3000   # ms pause at half-time
EXTRA_TIME_MINUTES     = 2      # golden goal ET period length
SET_PIECE_WAIT_FRAMES  = 60     # frames all players freeze before set piece executes

# --- AI difficulty ---
AI_DIFFICULTY = {
    'Easy':   {'reaction': 120, 'accuracy': 0.6},
    'Medium': {'reaction': 80,  'accuracy': 0.8},
    'Hard':   {'reaction': 40,  'accuracy': 0.95},
}

# --- Colors ---
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (34,  139, 34)
DARK_GREEN = (0,   100, 0)
YELLOW     = (255, 255, 0)
RED        = (200, 0,   0)
BLUE       = (0,   0,   200)
GRAY       = (150, 150, 150)
DARK_GRAY  = (50,  50,  50)
PITCH_GREEN      = (45,  100, 35)
PITCH_GREEN_ALT  = (40,  90,  30)
