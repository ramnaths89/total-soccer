# Total Soccer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python + Pygame remake of the classic 1997 Total Soccer game with 11v11 top-down gameplay, five European club leagues, Quick Match / Tournament / League season modes, and local 2-player support.

**Architecture:** Module-per-feature split: `engine/` owns pure game logic (ball, players, AI, match state machine) with no rendering; `ui/` owns all Pygame drawing; `modes/` wires engine + ui into the three game modes; `main.py` owns the screen manager and game loop. All packages live at the repo root.

**Tech Stack:** Python 3.11+, Pygame 2.x, pytest, stdlib only (no external game libraries)

---

## File Map

| File | Responsibility |
|---|---|
| `main.py` | Entry point, `ScreenManager`, `config` dict, main loop |
| `settings.py` | All constants (pitch, physics, timing, AI) |
| `data/__init__.py` | Empty |
| `data/teams.py` | Team dicts for all 5 leagues |
| `engine/__init__.py` | Empty |
| `engine/ball.py` | `Ball` class: physics, boundary detection, goal detection |
| `engine/player.py` | `Player` class: position, role, active-switching logic |
| `engine/team.py` | `Team` class: formation anchors, active player selection, AI mode |
| `engine/ai.py` | `update_player_ai()`, `try_kick()`: per-player state machine |
| `engine/match.py` | `Match` class: state machine, timer, score, set pieces |
| `ui/__init__.py` | Empty |
| `ui/menu.py` | `MenuScreen`: main menu drawing + navigation |
| `ui/team_select.py` | `TeamSelectScreen`: league filter, team list, kit preview (all modes) |
| `ui/hud.py` | `draw_pitch()` + `HUD`: in-match pitch + score/timer overlay |
| `ui/result.py` | `ResultScreen`: full-time result display |
| `ui/settings_screen.py` | `SettingsScreen`: duration, difficulty, controls |
| `modes/__init__.py` | Empty |
| `modes/quick_match.py` | `QuickMatchMode`: team select → match → result flow |
| `modes/tournament.py` | `TournamentMode` + `TournamentBracket`: bracket draw, round progression |
| `modes/league.py` | `LeagueMode` + `Season`: season fixture list, standings, save/load |
| `tests/__init__.py` | Empty |
| `tests/conftest.py` | pygame headless init fixture |
| `tests/test_ball.py` | Ball physics + goal detection tests |
| `tests/test_player.py` | Player active-switching + kick direction tests |
| `tests/test_team.py` | Formation anchors + ai_mode tests |
| `tests/test_ai.py` | AI state transition tests |
| `tests/test_match.py` | Match state machine tests |
| `tests/test_league.py` | Standings calculation + save/load tests |
| `tests/test_tournament.py` | Bracket progression + draw resolution tests |

---

## Chunk 1: Foundation — Project Setup, Settings, Data

### Task 1.1: Scaffold project structure and install dependencies

**Files:**
- Create: `requirements.txt`
- Create: `data/__init__.py`, `engine/__init__.py`, `ui/__init__.py`, `modes/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Create directories at repo root (not in a subdirectory)**

```bash
mkdir -p data engine ui modes tests
```

All packages live at the repo root next to `main.py`. Do NOT create a `total_soccer/` subdirectory.

- [ ] **Step 2: Create requirements.txt**

```
pygame==2.5.2
pytest==8.1.1
```

- [ ] **Step 3: Create empty `__init__.py` files**

Create an empty `__init__.py` in each package: `data/`, `engine/`, `ui/`, `modes/`, `tests/`.

- [ ] **Step 4: Create pytest.ini to set pythonpath**

```ini
[pytest]
pythonpath = .
```

This ensures `from engine.ball import Ball` works without installing the package.

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: Pygame and pytest install without errors.

- [ ] **Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: scaffold project structure"
```

---

### Task 1.2: Write settings.py

**Files:**
- Create: `settings.py`

- [ ] **Step 1: Write settings.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add settings.py
git commit -m "feat: add settings constants"
```

---

### Task 1.3: Write data/teams.py

**Files:**
- Create: `data/teams.py`

- [ ] **Step 1: Write data/teams.py**

```python
# data/teams.py
# All club teams for 5 leagues. Kit colors are inspired approximations.

TEAMS = {
    "Premier League": [
        {"name": "Manchester United", "short_name": "MUN", "kit_primary": "#DA291C", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Arsenal",           "short_name": "ARS", "kit_primary": "#EF0107", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Chelsea",           "short_name": "CHE", "kit_primary": "#034694", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Liverpool",         "short_name": "LIV", "kit_primary": "#C8102E", "kit_secondary": "#FFFFFF", "rating": 5},
        {"name": "Manchester City",   "short_name": "MCI", "kit_primary": "#6CABDD", "kit_secondary": "#FFFFFF", "rating": 5},
        {"name": "Tottenham",         "short_name": "TOT", "kit_primary": "#FFFFFF", "kit_secondary": "#132257", "rating": 3},
        {"name": "Newcastle",         "short_name": "NEW", "kit_primary": "#241F20", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Aston Villa",       "short_name": "AVL", "kit_primary": "#95BFE5", "kit_secondary": "#770020", "rating": 3},
        {"name": "West Ham",          "short_name": "WHU", "kit_primary": "#7A263A", "kit_secondary": "#1BB1E7", "rating": 3},
        {"name": "Brighton",          "short_name": "BHA", "kit_primary": "#0057B8", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Brentford",         "short_name": "BRE", "kit_primary": "#E30613", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Fulham",            "short_name": "FUL", "kit_primary": "#FFFFFF", "kit_secondary": "#000000", "rating": 2},
        {"name": "Crystal Palace",    "short_name": "CRY", "kit_primary": "#1B458F", "kit_secondary": "#C4122E", "rating": 2},
        {"name": "Wolves",            "short_name": "WOL", "kit_primary": "#FDB913", "kit_secondary": "#000000", "rating": 2},
        {"name": "Everton",           "short_name": "EVE", "kit_primary": "#003399", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Nottm Forest",      "short_name": "NFO", "kit_primary": "#DD0000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Bournemouth",       "short_name": "BOU", "kit_primary": "#DA291C", "kit_secondary": "#000000", "rating": 2},
        {"name": "Luton",             "short_name": "LUT", "kit_primary": "#F78F1E", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Burnley",           "short_name": "BUR", "kit_primary": "#6C1D45", "kit_secondary": "#99D6EA", "rating": 1},
        {"name": "Sheffield Utd",     "short_name": "SHU", "kit_primary": "#EE2737", "kit_secondary": "#000000", "rating": 1},
    ],
    "La Liga": [
        {"name": "Real Madrid",      "short_name": "RMA", "kit_primary": "#FFFFFF", "kit_secondary": "#00529F", "rating": 5},
        {"name": "Barcelona",        "short_name": "BAR", "kit_primary": "#A50044", "kit_secondary": "#004D98", "rating": 5},
        {"name": "Atletico Madrid",  "short_name": "ATM", "kit_primary": "#CE3524", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Sevilla",          "short_name": "SEV", "kit_primary": "#FFFFFF", "kit_secondary": "#D71920", "rating": 3},
        {"name": "Real Sociedad",    "short_name": "RSO", "kit_primary": "#0070B5", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Villarreal",       "short_name": "VIL", "kit_primary": "#FFFF00", "kit_secondary": "#009FC7", "rating": 3},
        {"name": "Athletic Bilbao",  "short_name": "ATH", "kit_primary": "#EE2523", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Valencia",         "short_name": "VAL", "kit_primary": "#FFFFFF", "kit_secondary": "#F5A000", "rating": 3},
        {"name": "Real Betis",       "short_name": "BET", "kit_primary": "#00954C", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Osasuna",          "short_name": "OSA", "kit_primary": "#D2122E", "kit_secondary": "#000000", "rating": 2},
        {"name": "Getafe",           "short_name": "GET", "kit_primary": "#005999", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Celta Vigo",       "short_name": "CEL", "kit_primary": "#9DC3E6", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Girona",           "short_name": "GIR", "kit_primary": "#990000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Cadiz",            "short_name": "CAD", "kit_primary": "#FFFF00", "kit_secondary": "#0000FF", "rating": 1},
        {"name": "Almeria",          "short_name": "ALM", "kit_primary": "#CE1126", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Granada",          "short_name": "GRA", "kit_primary": "#C8102E", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Las Palmas",       "short_name": "LPA", "kit_primary": "#FFFF00", "kit_secondary": "#000080", "rating": 1},
        {"name": "Mallorca",         "short_name": "MAL", "kit_primary": "#C8102E", "kit_secondary": "#000000", "rating": 2},
        {"name": "Rayo Vallecano",   "short_name": "RAY", "kit_primary": "#FFFFFF", "kit_secondary": "#CC0000", "rating": 2},
        {"name": "Alaves",           "short_name": "ALA", "kit_primary": "#005FAE", "kit_secondary": "#FFFFFF", "rating": 1},
    ],
    "Serie A": [
        {"name": "Juventus",       "short_name": "JUV", "kit_primary": "#000000", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "AC Milan",       "short_name": "MIL", "kit_primary": "#FB090B", "kit_secondary": "#000000", "rating": 4},
        {"name": "Inter Milan",    "short_name": "INT", "kit_primary": "#010E80", "kit_secondary": "#000000", "rating": 5},
        {"name": "AS Roma",        "short_name": "ROM", "kit_primary": "#8B0000", "kit_secondary": "#F5C518", "rating": 3},
        {"name": "Napoli",         "short_name": "NAP", "kit_primary": "#12A0C3", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Lazio",          "short_name": "LAZ", "kit_primary": "#87CEEB", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Atalanta",       "short_name": "ATA", "kit_primary": "#1C6BB0", "kit_secondary": "#000000", "rating": 4},
        {"name": "Fiorentina",     "short_name": "FIO", "kit_primary": "#4D2781", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Torino",         "short_name": "TOR", "kit_primary": "#8B0000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Bologna",        "short_name": "BOL", "kit_primary": "#C8102E", "kit_secondary": "#000080", "rating": 3},
        {"name": "Udinese",        "short_name": "UDI", "kit_primary": "#000000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Sassuolo",       "short_name": "SAS", "kit_primary": "#008000", "kit_secondary": "#000000", "rating": 2},
        {"name": "Lecce",          "short_name": "LEC", "kit_primary": "#F5A623", "kit_secondary": "#CC0000", "rating": 2},
        {"name": "Monza",          "short_name": "MON", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Empoli",         "short_name": "EMP", "kit_primary": "#1E90FF", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Hellas Verona",  "short_name": "HEL", "kit_primary": "#FFD700", "kit_secondary": "#000080", "rating": 1},
        {"name": "Salernitana",    "short_name": "SAL", "kit_primary": "#8B0000", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Frosinone",      "short_name": "FRO", "kit_primary": "#F5C518", "kit_secondary": "#000080", "rating": 1},
        {"name": "Cagliari",       "short_name": "CAG", "kit_primary": "#CC0000", "kit_secondary": "#000080", "rating": 2},
        {"name": "Genoa",          "short_name": "GEN", "kit_primary": "#CC0000", "kit_secondary": "#000080", "rating": 2},
    ],
    "Bundesliga": [
        {"name": "Bayern Munich",      "short_name": "BAY", "kit_primary": "#DC052D", "kit_secondary": "#FFFFFF", "rating": 5},
        {"name": "Borussia Dortmund",  "short_name": "BVB", "kit_primary": "#FDE100", "kit_secondary": "#000000", "rating": 4},
        {"name": "Bayer Leverkusen",   "short_name": "LEV", "kit_primary": "#E32221", "kit_secondary": "#000000", "rating": 4},
        {"name": "RB Leipzig",         "short_name": "RBL", "kit_primary": "#CC0E2D", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Union Berlin",       "short_name": "UNB", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Freiburg",           "short_name": "FRE", "kit_primary": "#CC0000", "kit_secondary": "#000000", "rating": 3},
        {"name": "Eintracht Frankfurt","short_name": "EIN", "kit_primary": "#E1000F", "kit_secondary": "#000000", "rating": 3},
        {"name": "Wolfsburg",          "short_name": "WOB", "kit_primary": "#64A32D", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "B. Monchengladbach", "short_name": "BMG", "kit_primary": "#000000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Mainz",              "short_name": "MAI", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Hoffenheim",         "short_name": "HOF", "kit_primary": "#1763AF", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Werder Bremen",      "short_name": "WER", "kit_primary": "#1D9053", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Augsburg",           "short_name": "AUG", "kit_primary": "#BA3733", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Stuttgart",          "short_name": "STU", "kit_primary": "#E32221", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Bochum",             "short_name": "BOC", "kit_primary": "#005CA9", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Cologne",            "short_name": "KOE", "kit_primary": "#FFFFFF", "kit_secondary": "#CC0000", "rating": 2},
        {"name": "Darmstadt",          "short_name": "DAR", "kit_primary": "#005CA9", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Heidenheim",         "short_name": "HDH", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 1},
    ],
    "Ligue 1": [
        {"name": "PSG",         "short_name": "PSG", "kit_primary": "#004170", "kit_secondary": "#DA291C", "rating": 5},
        {"name": "Marseille",   "short_name": "MAR", "kit_primary": "#00B2E3", "kit_secondary": "#FFFFFF", "rating": 4},
        {"name": "Lyon",        "short_name": "LYO", "kit_primary": "#FFFFFF", "kit_secondary": "#003B8E", "rating": 3},
        {"name": "Monaco",      "short_name": "MCO", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 3},
        {"name": "Lille",       "short_name": "LIL", "kit_primary": "#CC0000", "kit_secondary": "#000000", "rating": 3},
        {"name": "Nice",        "short_name": "NIC", "kit_primary": "#CC0000", "kit_secondary": "#000000", "rating": 3},
        {"name": "Lens",        "short_name": "LEN", "kit_primary": "#CC0000", "kit_secondary": "#F5A623", "rating": 3},
        {"name": "Rennes",      "short_name": "REN", "kit_primary": "#CC0000", "kit_secondary": "#000000", "rating": 3},
        {"name": "Strasbourg",  "short_name": "STR", "kit_primary": "#003399", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Nantes",      "short_name": "NAN", "kit_primary": "#F5A623", "kit_secondary": "#000000", "rating": 2},
        {"name": "Reims",       "short_name": "REI", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Toulouse",    "short_name": "TOU", "kit_primary": "#7B2582", "kit_secondary": "#FFFFFF", "rating": 2},
        {"name": "Lorient",     "short_name": "LOR", "kit_primary": "#F5A623", "kit_secondary": "#000000", "rating": 1},
        {"name": "Montpellier", "short_name": "MTP", "kit_primary": "#F5A623", "kit_secondary": "#000080", "rating": 2},
        {"name": "Clermont",    "short_name": "CLE", "kit_primary": "#CC0000", "kit_secondary": "#F5A623", "rating": 1},
        {"name": "Le Havre",    "short_name": "LEH", "kit_primary": "#005FAE", "kit_secondary": "#FFFFFF", "rating": 1},
        {"name": "Metz",        "short_name": "MET", "kit_primary": "#7B2582", "kit_secondary": "#000000", "rating": 1},
        {"name": "Brest",       "short_name": "BRE", "kit_primary": "#CC0000", "kit_secondary": "#FFFFFF", "rating": 2},
    ],
}

ALL_LEAGUES = list(TEAMS.keys())


def get_all_teams():
    """Return flat list of all team dicts across all leagues, each with 'league' key."""
    result = []
    for league, teams in TEAMS.items():
        for team in teams:
            result.append({**team, "league": league})
    return result


def get_team_by_name(name):
    for team in get_all_teams():
        if team["name"] == name:
            return team
    return None
```

- [ ] **Step 2: Commit**

```bash
git add data/teams.py data/__init__.py
git commit -m "feat: add team data for all 5 leagues"
```

---

### Task 1.4: Write tests/conftest.py

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py**

```python
# tests/conftest.py
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import pygame
import pytest


@pytest.fixture(scope='session', autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()
```

- [ ] **Step 2: Verify pytest collects zero tests with no errors**

```bash
pytest tests/ -v
```

Expected: "no tests ran", zero errors.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py tests/__init__.py pytest.ini
git commit -m "test: add pytest conftest with headless pygame"
```

---

## Chunk 2: Ball & Player Engine

### Task 2.1: Ball physics, boundary detection, and goal detection

**Files:**
- Create: `engine/ball.py`
- Create: `tests/test_ball.py`

**Naming convention used throughout:**
- `'home_scored'` = **home team scored** (ball crossed right goal line into away's goal)
- `'away_scored'` = **away team scored** (ball crossed left goal line into home's goal)

- [ ] **Step 1: Write failing tests for ball physics**

```python
# tests/test_ball.py
import pygame
import pytest
from engine.ball import Ball
from settings import (
    CENTRE_X, CENTRE_Y, BALL_FRICTION, KICK_POWER_BASE,
    PITCH_LEFT, PITCH_RIGHT, PITCH_TOP, PITCH_BOTTOM,
    GOAL_TOP, GOAL_BOTTOM, PLAYER_RADIUS, BALL_RADIUS,
)


class TestBallPhysics:
    def test_ball_starts_at_centre(self):
        ball = Ball()
        assert ball.pos.x == CENTRE_X
        assert ball.pos.y == CENTRE_Y

    def test_ball_velocity_zero_at_start(self):
        ball = Ball()
        assert ball.vel.length() == 0

    def test_ball_moves_each_frame(self):
        ball = Ball()
        ball.vel = pygame.Vector2(10, 0)
        ball.update()
        assert ball.pos.x > CENTRE_X

    def test_ball_friction_reduces_velocity(self):
        ball = Ball()
        ball.vel = pygame.Vector2(10, 0)
        ball.update()
        assert abs(ball.vel.x - 10 * BALL_FRICTION) < 0.001

    def test_ball_kick_sets_velocity(self):
        ball = Ball()
        direction = pygame.Vector2(1, 0)
        ball.kick(direction, KICK_POWER_BASE)
        assert abs(ball.vel.x - KICK_POWER_BASE) < 0.1

    def test_ball_kick_normalizes_direction(self):
        ball = Ball()
        ball.kick(pygame.Vector2(3, 4), 10)  # unnormalized — length=5
        assert abs(ball.vel.length() - 10) < 0.1


class TestBallGoalDetection:
    def test_home_scores_right_goal_in_posts(self):
        """Ball crosses right goal line (away's goal) within posts → home scored."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, CENTRE_Y)
        assert ball.check_goal() == 'home_scored'

    def test_away_scores_left_goal_in_posts(self):
        """Ball crosses left goal line (home's goal) within posts → away scored."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 1, CENTRE_Y)
        assert ball.check_goal() == 'away_scored'

    def test_no_goal_ball_above_posts_right(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, GOAL_TOP - 10)
        assert ball.check_goal() is None

    def test_no_goal_ball_below_posts_right(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 1, GOAL_BOTTOM + 10)
        assert ball.check_goal() is None

    def test_no_goal_ball_in_pitch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        assert ball.check_goal() is None


class TestBallBoundary:
    def test_no_boundary_event_in_pitch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, CENTRE_Y)
        assert ball.check_boundary() is None

    def test_sideline_exit_top(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, PITCH_TOP - 5)
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'throw_in'

    def test_sideline_exit_bottom(self):
        ball = Ball()
        ball.pos = pygame.Vector2(CENTRE_X, PITCH_BOTTOM + 5)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'throw_in'

    def test_left_byline_defending_home_last_touch(self):
        """Home defending left goal, home last touched → corner for away."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 5, 200)  # y outside goal mouth
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'corner_kick'

    def test_left_byline_attacking_away_last_touch(self):
        """Away attacked left byline, away last touched → goal kick for home."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_LEFT - 5, 200)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'goal_kick'

    def test_right_byline_defending_away_last_touch(self):
        """Away defending right goal, away last touched → corner for home."""
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 5, 200)
        ball.last_touch_team = 'away'
        assert ball.check_boundary() == 'corner_kick'

    def test_right_byline_attacking_home_last_touch(self):
        ball = Ball()
        ball.pos = pygame.Vector2(PITCH_RIGHT + 5, 200)
        ball.last_touch_team = 'home'
        assert ball.check_boundary() == 'goal_kick'
```

- [ ] **Step 2: Run tests to confirm they all fail**

```bash
pytest tests/test_ball.py -v
```

Expected: `ModuleNotFoundError` — `engine/ball.py` doesn't exist yet.

- [ ] **Step 3: Implement engine/ball.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they all pass**

```bash
pytest tests/test_ball.py -v
```

Expected: All green.

- [ ] **Step 5: Commit**

```bash
git add engine/ball.py engine/__init__.py tests/test_ball.py
git commit -m "feat: implement Ball physics, boundary detection, goal detection"
```

---

### Task 2.2: Player class — movement, active switching, kick direction

**Files:**
- Create: `engine/player.py`
- Create: `tests/test_player.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_player.py
import pygame
import pytest
from engine.player import Player, get_active_player
from settings import (
    PITCH_LEFT, PITCH_W, PITCH_H, PITCH_TOP,
    CENTRE_X, CENTRE_Y, PITCH_RIGHT,
    ACTIVE_SWITCH_HYSTERESIS, ACTIVE_SWITCH_MIN_FRAMES,
    PLAYER_SPEED,
)


def make_player(number=1, role='MID', side='home', x_pct=0.4, y_pct=0.5):
    return Player(number=number, role=role, team_side=side,
                  anchor_x_pct=x_pct, anchor_y_pct=y_pct)


class TestPlayerCreation:
    def test_player_has_correct_role_speed(self):
        p = make_player(role='FWD')
        assert p.speed == PLAYER_SPEED['FWD']

    def test_player_starts_at_home_anchor(self):
        p = make_player(side='home', x_pct=0.4, y_pct=0.5)
        expected_x = PITCH_LEFT + 0.4 * PITCH_W
        expected_y = PITCH_TOP + 0.5 * PITCH_H
        assert abs(p.pos.x - expected_x) < 1
        assert abs(p.pos.y - expected_y) < 1

    def test_away_player_anchor_mirrored(self):
        away = make_player(side='away', x_pct=0.2, y_pct=0.5)
        expected_x = PITCH_LEFT + (1.0 - 0.2) * PITCH_W
        assert abs(away.pos.x - expected_x) < 1


class TestActivePlayerSwitching:
    def test_select_nearest_to_ball(self):
        players = [
            make_player(number=1, x_pct=0.1, y_pct=0.5),   # far left
            make_player(number=2, x_pct=0.5, y_pct=0.5),   # centre
            make_player(number=3, x_pct=0.9, y_pct=0.5),   # far right
        ]
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.5 * PITCH_W, CENTRE_Y)
        result = get_active_player(players, ball_pos, current_idx=0, hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 1

    def test_hysteresis_keeps_current_when_margin_small(self):
        p1 = make_player(number=1, x_pct=0.40, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.41, y_pct=0.5)
        # ball just slightly closer to p2 — within hysteresis
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.42 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 0  # keeps p1

    def test_min_hold_frames_prevents_switch(self):
        p1 = make_player(number=1, x_pct=0.1, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.9, y_pct=0.5)
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.9 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES - 1)
        assert result == 0  # not enough hold frames to switch

    def test_switch_allowed_after_min_frames(self):
        p1 = make_player(number=1, x_pct=0.1, y_pct=0.5)
        p2 = make_player(number=2, x_pct=0.9, y_pct=0.5)
        ball_pos = pygame.Vector2(PITCH_LEFT + 0.9 * PITCH_W, CENTRE_Y)
        result = get_active_player([p1, p2], ball_pos, current_idx=0,
                                   hold_frames=ACTIVE_SWITCH_MIN_FRAMES)
        assert result == 1


class TestKickDirection:
    def test_kick_direction_moving_player(self):
        p = make_player(role='MID', side='home')
        p.vel = pygame.Vector2(5, 0)
        direction = p.get_kick_direction()
        assert direction.x > 0
        assert abs(direction.y) < 0.01

    def test_kick_direction_stationary_home_aims_right_goal(self):
        p = make_player(role='MID', side='home')
        p.vel = pygame.Vector2(0, 0)
        direction = p.get_kick_direction()
        target = pygame.Vector2(PITCH_RIGHT, CENTRE_Y)
        expected = (target - p.pos).normalize()
        assert abs(direction.x - expected.x) < 0.01

    def test_kick_direction_stationary_away_aims_left_goal(self):
        p = make_player(role='MID', side='away')
        p.vel = pygame.Vector2(0, 0)
        direction = p.get_kick_direction()
        target = pygame.Vector2(PITCH_LEFT, CENTRE_Y)
        expected = (target - p.pos).normalize()
        assert abs(direction.x - expected.x) < 0.01
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_player.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement engine/player.py**

```python
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
        target = (pygame.Vector2(PITCH_RIGHT, CENTRE_Y) if self.team_side == 'home'
                  else pygame.Vector2(PITCH_LEFT, CENTRE_Y))
        diff = target - self.pos
        return diff.normalize() if diff.length() > 0 else pygame.Vector2(1, 0)

    def draw(self, surface, kit_primary, kit_secondary):
        if self._font is None:
            self._font = pygame.font.SysFont(None, 14)
        color  = _hex_to_rgb(kit_primary)
        border = _hex_to_rgb(kit_secondary)
        pygame.draw.circle(surface, color,  (int(self.pos.x), int(self.pos.y)), PLAYER_RADIUS)
        pygame.draw.circle(surface, border, (int(self.pos.x), int(self.pos.y)), PLAYER_RADIUS, 2)
        num_surf = self._font.render(str(self.number), True, border)
        surface.blit(num_surf, num_surf.get_rect(center=(int(self.pos.x), int(self.pos.y))))


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
            best_dist = d

    return best_idx


def _hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
```

- [ ] **Step 4: Run tests to confirm they all pass**

```bash
pytest tests/test_player.py -v
```

Expected: All green.

- [ ] **Step 5: Commit**

```bash
git add engine/player.py tests/test_player.py
git commit -m "feat: implement Player with active-switching, hysteresis, kick direction"
```

---

## Chunk 3: Match Engine — Team, AI, Match State Machine

### Task 3.1: Team class — formation, anchors, ai_mode, active player selection

**Files:**
- Create: `engine/team.py`
- Create: `tests/test_team.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_team.py
import pygame
import pytest
from engine.team import Team
from settings import CENTRE_X, PITCH_LEFT, PITCH_W, PITCH_H, PITCH_TOP


ARSENAL = {"name": "Arsenal", "short_name": "ARS", "league": "Premier League",
           "kit_primary": "#EF0107", "kit_secondary": "#FFFFFF", "rating": 4}


class TestTeamCreation:
    def test_team_has_11_players(self):
        assert len(Team(ARSENAL, 'home', 'HUMAN_P1').players) == 11

    def test_team_formation_roles(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        roles = [p.role for p in t.players]
        assert roles.count('GK') == 1
        assert roles.count('DEF') == 4
        assert roles.count('MID') == 4
        assert roles.count('FWD') == 2

    def test_home_gk_starts_left_side(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        gk = next(p for p in t.players if p.role == 'GK')
        assert gk.pos.x < CENTRE_X

    def test_away_gk_starts_right_side(self):
        t = Team(ARSENAL, 'away', 'CPU')
        gk = next(p for p in t.players if p.role == 'GK')
        assert gk.pos.x > CENTRE_X


class TestTeamAIMode:
    def test_home_offensive_ball_right_of_centre(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.update_ai_mode(pygame.Vector2(CENTRE_X + 100, 300))
        assert t.ai_mode == 'OFFENSIVE'

    def test_home_defensive_ball_left_of_centre(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.update_ai_mode(pygame.Vector2(CENTRE_X - 100, 300))
        assert t.ai_mode == 'DEFENSIVE'

    def test_away_offensive_ball_left_of_centre(self):
        t = Team(ARSENAL, 'away', 'CPU')
        t.update_ai_mode(pygame.Vector2(CENTRE_X - 100, 300))
        assert t.ai_mode == 'OFFENSIVE'


class TestTeamReset:
    def test_reset_returns_players_to_anchors(self):
        t = Team(ARSENAL, 'home', 'HUMAN_P1')
        t.players[0].pos = pygame.Vector2(700, 500)
        t.reset_to_formation(second_half=False)
        gk = next(p for p in t.players if p.role == 'GK')
        expected_x = PITCH_LEFT + 0.05 * PITCH_W
        assert abs(gk.pos.x - expected_x) < 2
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_team.py -v
```

- [ ] **Step 3: Implement engine/team.py**

```python
# engine/team.py
import pygame
from engine.player import Player, get_active_player
from settings import CENTRE_X, ACTIVE_SWITCH_MIN_FRAMES


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
        self.name        = team_data['name']
        self.short_name  = team_data['short_name']
        self.kit_primary = team_data['kit_primary']
        self.kit_secondary = team_data['kit_secondary']
        self.rating      = team_data['rating']
        self.side        = side             # 'home' | 'away'
        self.controlled_by = controlled_by  # 'HUMAN_P1' | 'HUMAN_P2' | 'CPU'
        self.ai_mode     = 'DEFENSIVE'
        self._active_idx = 0
        self._hold_frames = ACTIVE_SWITCH_MIN_FRAMES

        self.players = self._create_players()

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

    def draw(self, surface):
        for player in self.players:
            player.draw(surface, self.kit_primary, self.kit_secondary)
            if player.is_active:
                pygame.draw.circle(surface, (255, 255, 0),
                                   (int(player.pos.x), int(player.pos.y)), 14, 2)
```

- [ ] **Step 4: Run tests to confirm they all pass**

```bash
pytest tests/test_team.py -v
```

- [ ] **Step 5: Commit**

```bash
git add engine/team.py tests/test_team.py
git commit -m "feat: implement Team with 4-4-2 formation and active player selection"
```

---

### Task 3.2: AI controller — per-player state machine

**Files:**
- Create: `engine/ai.py`
- Create: `tests/test_ai.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_ai.py
import pygame
import pytest
from engine.player import Player
from engine.ai import get_ai_state


def make_player(number=5, role='MID', side='home', x_pct=0.4, y_pct=0.5):
    return Player(number=number, role=role, team_side=side,
                  anchor_x_pct=x_pct, anchor_y_pct=y_pct)


class TestAIStateTransitions:
    """
    get_ai_state(player, player_dist, nearest_dist, ball_in_own_third, ball_in_opp_third)
    player_dist:   distance from this player to ball
    nearest_dist:  distance from the nearest player (any team) to ball
    is_nearest when player_dist <= nearest_dist + 1.0
    """

    def test_support_stays_support_not_nearest_mid_field(self):
        p = make_player(role='MID')
        p.ai_state = 'SUPPORT'
        # Not nearest, ball in middle third
        state = get_ai_state(p, 200, 50, False, False)
        assert state == 'SUPPORT'

    def test_support_to_attack_when_nearest_and_ball_in_own_third(self):
        p = make_player(role='MID')
        p.ai_state = 'SUPPORT'
        # This player IS nearest, ball in own third
        state = get_ai_state(p, 50, 50, True, False)
        assert state == 'ATTACK'

    def test_support_to_defend_when_not_nearest_and_ball_in_opp_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'SUPPORT'
        state = get_ai_state(p, 200, 50, False, True)
        assert state == 'DEFEND'

    def test_attack_stays_attack_when_nearest(self):
        p = make_player(role='MID')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 50, 50, False, False)
        assert state == 'ATTACK'

    def test_attack_to_support_when_not_nearest(self):
        p = make_player(role='MID')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 200, 50, False, False)
        assert state == 'SUPPORT'

    def test_attack_to_defend_when_ball_in_own_third_and_not_nearest(self):
        """Spec: ATTACK → DEFEND when ball crosses into own half and player not nearest."""
        p = make_player(role='DEF')
        p.ai_state = 'ATTACK'
        state = get_ai_state(p, 200, 50, True, False)
        assert state == 'DEFEND'

    def test_defend_to_support_when_ball_in_opp_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'DEFEND'
        state = get_ai_state(p, 200, 50, False, True)
        assert state == 'SUPPORT'

    def test_defend_stays_defend_when_ball_in_own_third(self):
        p = make_player(role='DEF')
        p.ai_state = 'DEFEND'
        state = get_ai_state(p, 200, 50, True, False)
        assert state == 'DEFEND'

    def test_gk_always_defend_regardless_of_ball(self):
        gk = make_player(role='GK')
        gk.ai_state = 'ATTACK'
        state = get_ai_state(gk, 50, 50, False, True)
        assert state == 'DEFEND'
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_ai.py -v
```

- [ ] **Step 3: Implement engine/ai.py**

```python
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
    Returns True if kick was made.
    Inaccuracy: noise is in degrees (not radians). Easy=~23°, Hard=~3°.
    """
    dist = (player.pos - ball.pos).length()
    if dist > PLAYER_RADIUS + BALL_RADIUS + 4:
        return False

    diff_cfg = AI_DIFFICULTY[difficulty]
    direction = player.get_kick_direction()

    # Angle noise in degrees: (1 - accuracy) * 40° max spread
    max_noise_deg = (1.0 - diff_cfg['accuracy']) * 40.0
    noise_deg = random.uniform(-max_noise_deg, max_noise_deg)
    direction = direction.rotate(noise_deg)

    power = KICK_POWER_BASE * (team.rating / 5.0)
    ball.kick(direction, power)
    ball.last_touch_team = team.side
    return True
```

- [ ] **Step 4: Run tests to confirm they all pass**

```bash
pytest tests/test_ai.py -v
```

Expected: All green.

- [ ] **Step 5: Commit**

```bash
git add engine/ai.py tests/test_ai.py
git commit -m "feat: implement AI state machine with SUPPORT/ATTACK/DEFEND transitions"
```

---

### Task 3.3: Match state machine — timer, score, set pieces

**Files:**
- Create: `engine/match.py`
- Create: `tests/test_match.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_match.py -v
```

- [ ] **Step 3: Implement engine/match.py**

```python
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
            if keys_p1 is not None and any(keys_p1):
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
                                     pygame.K_LSHIFT)
        if self.away_team.controlled_by != 'CPU':
            self._handle_human_input(self.away_team, keys_p2,
                                     pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT,
                                     pygame.K_RIGHT, pygame.K_RCTRL)

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

    def _handle_human_input(self, team, keys, k_up, k_down, k_left, k_right, k_kick):
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
        # Kick
        if keys[k_kick]:
            dist = (player.pos - self.ball.pos).length()
            if dist < PLAYER_RADIUS + BALL_RADIUS + 4:
                power = KICK_POWER_BASE * (team.rating / 5.0)
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
```

- [ ] **Step 4: Run all tests so far**

```bash
pytest tests/ -v
```

Expected: All green (ball + player + team + ai + match).

- [ ] **Step 5: Commit**

```bash
git add engine/match.py tests/test_match.py
git commit -m "feat: implement Match state machine with goals, half-time, set pieces"
```

---

## Chunk 4: UI Layer

### Task 4.1: ScreenManager and main.py

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write main.py**

```python
# main.py
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'directx')  # Windows default

import pygame
import sys
from settings import SCREEN_W, SCREEN_H, FPS, BLACK


class ScreenManager:
    """
    Manages active screen. Each screen has:
      update(events, keys) -> None | str | dict
      draw(surface) -> None
      on_enter(**kwargs) -> None (optional)
    Transition dict: {'screen': 'name', ...kwargs passed to on_enter}
    """

    def __init__(self, surface):
        self.surface = surface
        self.screens = {}
        self.current = None
        # Shared config: duration and difficulty flow through here
        self.config = {'duration': 5, 'difficulty': 'Medium'}

    def register(self, name, screen):
        self.screens[name] = screen

    def switch(self, name, **kwargs):
        screen = self.screens[name]
        if hasattr(screen, 'on_enter'):
            screen.on_enter(**kwargs)
        self.current = screen

    def run(self):
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            self.surface.fill(BLACK)

            if self.current:
                result = self.current.update(events, keys)
                self.current.draw(self.surface)
                if result:
                    self._handle_transition(result)

            pygame.display.flip()
            clock.tick(FPS)

    def _handle_transition(self, result):
        if isinstance(result, str):
            self.switch(result)
        elif isinstance(result, dict):
            name = result.pop('screen')
            self.switch(name, **result)


def main():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Total Soccer')

    manager = ScreenManager(surface)

    from ui.menu import MenuScreen
    from ui.team_select import TeamSelectScreen
    from ui.settings_screen import SettingsScreen
    from modes.quick_match import QuickMatchMode
    from modes.tournament import TournamentMode
    from modes.league import LeagueMode

    manager.register('menu',        MenuScreen(manager))
    manager.register('team_select', TeamSelectScreen(manager))
    manager.register('settings',    SettingsScreen(manager))
    manager.register('quick_match', QuickMatchMode(manager))
    manager.register('tournament',  TournamentMode(manager))
    manager.register('league',      LeagueMode(manager))

    manager.switch('menu')
    manager.run()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Commit main.py skeleton**

```bash
git add main.py
git commit -m "feat: add ScreenManager and main entry point"
```

---

### Task 4.2: ui/menu.py

**Files:**
- Create: `ui/menu.py`

- [ ] **Step 1: Write ui/menu.py**

Menu items return dicts so kwargs (mode, duration, etc.) flow through ScreenManager.

```python
# ui/menu.py
import pygame
import sys
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


class MenuScreen:
    """
    Returns dict transitions so kwargs flow cleanly to downstream screens.
    """

    def __init__(self, manager):
        self.manager = manager
        self.selected = 0
        self.font_title = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_item  = pygame.font.SysFont('Arial', 28)
        self.font_sub   = pygame.font.SysFont('Arial', 18)

    # Menu items: (label, action_fn)
    # Each action_fn returns a transition dict or string
    def _items(self):
        cfg = self.manager.config
        return [
            ('New Quick Match', lambda: {'screen': 'team_select', 'mode': 'quick_match',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('New Tournament',  lambda: {'screen': 'team_select', 'mode': 'tournament',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('New Season',      lambda: {'screen': 'team_select', 'mode': 'league',
                                         'duration': cfg['duration'],
                                         'difficulty': cfg['difficulty']}),
            ('Load Season',     lambda: {'screen': 'league', 'load': True}),
            ('Settings',        lambda: 'settings'),
            ('Quit',            lambda: self._quit()),
        ]

    def _quit(self):
        pygame.quit()
        sys.exit()

    def on_enter(self, **kwargs):
        self.selected = 0

    def update(self, events, keys):
        items = self._items()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return items[self.selected][1]()
        return None

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_title.render('TOTAL SOCCER', True, GREEN)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 120)))
        sub = self.font_sub.render('Classic 1997 Remake  |  Python + Pygame', True, GRAY)
        surface.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 165)))

        items = self._items()
        start_y = 240
        for i, (label, _) in enumerate(items):
            y = start_y + i * 48
            if i == self.selected:
                pygame.draw.rect(surface, (0, 80, 0),
                                 (SCREEN_W // 2 - 140, y - 8, 280, 38), border_radius=4)
            color = WHITE if i == self.selected else GRAY
            text = self.font_item.render(label, True, color)
            surface.blit(text, text.get_rect(center=(SCREEN_W // 2, y + 8)))
```

- [ ] **Step 2: Commit**

```bash
git add ui/menu.py ui/__init__.py
git commit -m "feat: add main menu screen"
```

---

### Task 4.3: ui/team_select.py

**Files:**
- Create: `ui/team_select.py`

- [ ] **Step 1: Write ui/team_select.py**

Handles three modes via `on_enter(mode=...)`:
- `'quick_match'`: pick home team, then away team
- `'tournament'` and `'league'`: pick single player team, then pass through

```python
# ui/team_select.py
import pygame
from data.teams import TEAMS, ALL_LEAGUES, get_all_teams
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class TeamSelectScreen:
    """
    mode='quick_match': two-stage pick (home then away)
    mode='tournament' : single pick (player's team)
    mode='league'     : single pick (player's team + league carried over)
    """

    def __init__(self, manager):
        self.manager = manager
        self.font_h = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_m = pygame.font.SysFont('Arial', 20)
        self.font_s = pygame.font.SysFont('Arial', 15)

        self.mode = 'quick_match'
        self.duration = 5
        self.difficulty = 'Medium'
        self.leagues = ['All'] + ALL_LEAGUES
        self.league_idx = 0
        self.team_idx = 0
        self.team_scroll = 0
        self.stage = 'home'
        self.home_team = None

    def on_enter(self, mode='quick_match', duration=5, difficulty='Medium', **kwargs):
        self.mode = mode
        self.duration = duration
        self.difficulty = difficulty
        self.stage = 'home'
        self.home_team = None
        self.league_idx = 0
        self.team_idx = 0
        self.team_scroll = 0

    def _filtered_teams(self):
        league = self.leagues[self.league_idx]
        if league == 'All':
            return get_all_teams()
        return [{**t, 'league': league} for t in TEAMS[league]]

    @property
    def _stage_label(self):
        if self.mode == 'quick_match':
            return 'SELECT HOME TEAM' if self.stage == 'home' else 'SELECT AWAY TEAM'
        return 'SELECT YOUR TEAM'

    def update(self, events, keys):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            k = event.key
            if k == pygame.K_ESCAPE:
                return 'menu'

            teams = self._filtered_teams()
            if k == pygame.K_LEFT:
                self.league_idx = (self.league_idx - 1) % len(self.leagues)
                self.team_idx = 0; self.team_scroll = 0
            elif k == pygame.K_RIGHT:
                self.league_idx = (self.league_idx + 1) % len(self.leagues)
                self.team_idx = 0; self.team_scroll = 0
            elif k == pygame.K_UP:
                self.team_idx = max(0, self.team_idx - 1)
                if self.team_idx < self.team_scroll:
                    self.team_scroll = self.team_idx
            elif k == pygame.K_DOWN:
                self.team_idx = min(len(teams) - 1, self.team_idx + 1)
                if self.team_idx >= self.team_scroll + 12:
                    self.team_scroll += 1
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                selected = teams[self.team_idx]
                return self._on_select(selected)
        return None

    def _on_select(self, selected):
        if self.mode == 'quick_match':
            if self.stage == 'home':
                self.home_team = selected
                self.stage = 'away'
                self.team_idx = 0; self.team_scroll = 0
                return None
            else:
                return {'screen': 'quick_match',
                        'home': self.home_team,
                        'away': selected,
                        'duration': self.duration,
                        'difficulty': self.difficulty,
                        'multiplayer': False}

        elif self.mode == 'tournament':
            return {'screen': 'tournament',
                    'home': selected,
                    'duration': self.duration,
                    'difficulty': self.difficulty}

        elif self.mode == 'league':
            league = self.leagues[self.league_idx]
            if league == 'All':
                league = selected.get('league', ALL_LEAGUES[0])
            teams_in_league = [{**t, 'league': league} for t in TEAMS[league]]
            return {'screen': 'league',
                    'league_name': league,
                    'player_team': selected['name'],
                    'teams': teams_in_league,
                    'duration': self.duration,
                    'difficulty': self.difficulty}

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_h.render(self._stage_label, True, (255, 255, 255))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 20))

        # League tabs
        tx = 40
        for i, league in enumerate(self.leagues):
            col = GREEN if i == self.league_idx else GRAY
            tab = self.font_s.render(league, True, col)
            surface.blit(tab, (tx, 58))
            tx += tab.get_width() + 18

        # Team list
        teams = self._filtered_teams()
        for i, team in enumerate(teams[self.team_scroll:self.team_scroll + 12]):
            abs_idx = self.team_scroll + i
            y = 90 + i * 36
            selected = abs_idx == self.team_idx
            pygame.draw.rect(surface, (0, 60, 0) if selected else (10, 20, 10),
                             (40, y, 340, 34))
            # Kit swatch
            pygame.draw.rect(surface, _hex_to_rgb(team['kit_primary']),
                             (44, y + 4, 20, 26))
            pygame.draw.rect(surface, _hex_to_rgb(team['kit_secondary']),
                             (44, y + 17, 20, 13))
            col = (255, 255, 255) if selected else GRAY
            surface.blit(self.font_m.render(team['name'], True, col), (70, y + 8))
            stars = '* ' * team['rating'] + '  ' * (5 - team['rating'])
            surface.blit(self.font_s.render(stars.strip(), True, (220, 180, 0)), (300, y + 10))

        if self.mode == 'quick_match' and self.stage == 'away' and self.home_team:
            preview = self.font_s.render(f"Home: {self.home_team['name']}", True, (180, 255, 180))
            surface.blit(preview, (420, 90))

        hint = self.font_s.render(
            'Left/Right: League  Up/Down: Team  Enter: Select  Esc: Back', True, GRAY)
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 28))
```

- [ ] **Step 2: Commit**

```bash
git add ui/team_select.py
git commit -m "feat: add team select screen supporting quick match, tournament, league modes"
```

---

### Task 4.4: ui/hud.py and ui/result.py

**Files:**
- Create: `ui/hud.py`
- Create: `ui/result.py`

- [ ] **Step 1: Write ui/hud.py**

```python
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
```

- [ ] **Step 2: Write ui/result.py**

```python
# ui/result.py
import pygame
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY


class ResultScreen:
    """
    Displays match result. on_enter(result=dict, next_screen='menu', **extra_kwargs).
    On any key press, transitions to next_screen with extra_kwargs.
    """

    def __init__(self, manager):
        self.manager = manager
        self.result = {}
        self.next_screen = 'menu'
        self.extra_kwargs = {}
        self.font_big   = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_med   = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 20)

    def on_enter(self, result=None, next_screen='menu', **kwargs):
        self.result = result or {}
        self.next_screen = next_screen
        self.extra_kwargs = kwargs

    def update(self, events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.next_screen:
                    if self.extra_kwargs:
                        return {'screen': self.next_screen, **self.extra_kwargs}
                    return self.next_screen
        return None

    def draw(self, surface):
        surface.fill((5, 15, 5))
        r = self.result
        cx = SCREEN_W // 2

        ft = self.font_small.render('FULL TIME', True, GRAY)
        surface.blit(ft, ft.get_rect(center=(cx, 120)))

        score_str = f"{r.get('home_short','?')}  {r.get('score',[0,0])[0]} - {r.get('score',[0,0])[1]}  {r.get('away_short','?')}"
        surface.blit(self.font_big.render(score_str, True, WHITE),
                     self.font_big.render(score_str, True, WHITE).get_rect(center=(cx, 200)))

        names = f"{r.get('home_name','')}  vs  {r.get('away_name','')}"
        surface.blit(self.font_small.render(names, True, GRAY),
                     self.font_small.render(names, True, GRAY).get_rect(center=(cx, 258)))

        # Coin flip notice (tournament draws)
        if r.get('coin_flip'):
            cf = self.font_small.render(
                f"Draw — {r['coin_winner']} advances (away rule)", True, (255, 200, 0))
            surface.blit(cf, cf.get_rect(center=(cx, 300)))

        mom = self.font_small.render(
            f"Man of the Match: {r.get('man_of_match','N/A')}", True, (220, 200, 0))
        surface.blit(mom, mom.get_rect(center=(cx, 330)))

        cont = self.font_small.render('Press any key to continue', True, GRAY)
        surface.blit(cont, cont.get_rect(center=(cx, SCREEN_H - 60)))
```

- [ ] **Step 3: Commit**

```bash
git add ui/hud.py ui/result.py
git commit -m "feat: add HUD (pitch + score overlay) and result screen"
```

---

### Task 4.5: ui/settings_screen.py

**Files:**
- Create: `ui/settings_screen.py`

- [ ] **Step 1: Write ui/settings_screen.py**

Settings writes back to `manager.config` so duration and difficulty flow into all game modes.

```python
# ui/settings_screen.py
import pygame
from settings import SCREEN_W, SCREEN_H, WHITE, GRAY, GREEN


class SettingsScreen:
    DURATIONS    = [1, 3, 5, 10]
    DIFFICULTIES = ['Easy', 'Medium', 'Hard']

    def __init__(self, manager):
        self.manager = manager
        self.selected_row = 0
        self.font_h = pygame.font.SysFont('Arial', 30, bold=True)
        self.font_m = pygame.font.SysFont('Arial', 22)
        self.font_s = pygame.font.SysFont('Arial', 17)

    @property
    def _duration_idx(self):
        d = self.manager.config.get('duration', 5)
        return self.DURATIONS.index(d) if d in self.DURATIONS else 2

    @property
    def _difficulty_idx(self):
        d = self.manager.config.get('difficulty', 'Medium')
        return self.DIFFICULTIES.index(d) if d in self.DIFFICULTIES else 1

    def on_enter(self, **kwargs):
        self.selected_row = 0

    def update(self, events, keys):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            k = event.key
            if k == pygame.K_ESCAPE or k == pygame.K_RETURN:
                return 'menu'
            if k == pygame.K_UP:
                self.selected_row = max(0, self.selected_row - 1)
            if k == pygame.K_DOWN:
                self.selected_row = min(1, self.selected_row + 1)
            if k == pygame.K_LEFT:
                if self.selected_row == 0:
                    idx = (self._duration_idx - 1) % len(self.DURATIONS)
                    self.manager.config['duration'] = self.DURATIONS[idx]
                else:
                    idx = (self._difficulty_idx - 1) % len(self.DIFFICULTIES)
                    self.manager.config['difficulty'] = self.DIFFICULTIES[idx]
            if k == pygame.K_RIGHT:
                if self.selected_row == 0:
                    idx = (self._duration_idx + 1) % len(self.DURATIONS)
                    self.manager.config['duration'] = self.DURATIONS[idx]
                else:
                    idx = (self._difficulty_idx + 1) % len(self.DIFFICULTIES)
                    self.manager.config['difficulty'] = self.DIFFICULTIES[idx]
        return None

    def draw(self, surface):
        surface.fill((10, 20, 10))
        title = self.font_h.render('SETTINGS', True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 60)))

        rows = [
            ('Match Duration',
             f"{self.manager.config.get('duration', 5)} min",
             ' / '.join(f"{d}m" for d in self.DURATIONS)),
            ('AI Difficulty',
             self.manager.config.get('difficulty', 'Medium'),
             ' / '.join(self.DIFFICULTIES)),
        ]
        for i, (label, value, options) in enumerate(rows):
            y = 160 + i * 80
            selected = (i == self.selected_row)
            if selected:
                pygame.draw.rect(surface, (0, 50, 0),
                                 (SCREEN_W // 2 - 220, y - 10, 440, 55), border_radius=6)
            color = WHITE if selected else GRAY
            surface.blit(self.font_m.render(label, True, color), (SCREEN_W // 2 - 200, y))
            val_surf = self.font_m.render(f'< {value} >', True, GREEN if selected else GRAY)
            surface.blit(val_surf, (SCREEN_W // 2 + 40, y))
            surface.blit(self.font_s.render(options, True, (100, 100, 100)),
                         (SCREEN_W // 2 - 200, y + 28))

        # Controls reference
        surface.blit(self.font_m.render('Controls', True, WHITE), (SCREEN_W // 2 - 200, 340))
        controls = [
            'Player 1:  WASD to move  |  Left Shift to kick',
            'Player 2:  Arrow Keys    |  Right Ctrl to kick',
            'Pause / Back:  Escape',
        ]
        for j, line in enumerate(controls):
            surface.blit(self.font_s.render(line, True, GRAY),
                         (SCREEN_W // 2 - 200, 370 + j * 26))

        hint = self.font_s.render(
            'Up/Down: Navigate   Left/Right: Change   Enter/Esc: Back', True, GRAY)
        surface.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 28)))
```

- [ ] **Step 2: Commit**

```bash
git add ui/settings_screen.py
git commit -m "feat: add settings screen wired to manager.config"
```

---

## Chunk 5: Game Modes + Integration

### Task 5.1: modes/quick_match.py

**Files:**
- Create: `modes/quick_match.py`

- [ ] **Step 1: Write modes/quick_match.py**

```python
# modes/quick_match.py
import pygame
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK


class QuickMatchMode:
    """Quick match flow: match phase → result phase → back to menu."""

    def __init__(self, manager):
        self.manager = manager
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'match'
        self.multiplayer = False

    def on_enter(self, home=None, away=None, duration=5, multiplayer=False,
                 difficulty='Medium', **kwargs):
        if home is None or away is None:
            return
        self.multiplayer = multiplayer
        home_ctrl = 'HUMAN_P1'
        away_ctrl = 'HUMAN_P2' if multiplayer else 'CPU'
        self.match = Match(home, away, duration, home_ctrl, away_ctrl, difficulty)
        self.phase = 'match'

    def update(self, events, keys):
        if self.phase == 'result':
            result = self.result_screen.update(events, keys)
            if result is not None:
                return result
            return None

        if self.match is None:
            return 'menu'

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'menu'

        # P1 always gets keys; P2 gets keys only in multiplayer, else None
        keys_p2 = keys if self.multiplayer else None
        self.match.update(keys_p1=keys, keys_p2=keys_p2)

        if self.match.state == 'FULL_TIME':
            self.phase = 'result'
            self.result_screen.on_enter(result=self.match.get_result(), next_screen='menu')

        return None

    def draw(self, surface):
        if self.phase == 'result':
            self.result_screen.draw(surface)
            return
        surface.fill(BLACK)
        if self.match:
            draw_pitch(surface)
            self.match.home_team.draw(surface)
            self.match.away_team.draw(surface)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
```

- [ ] **Step 2: Commit**

```bash
git add modes/quick_match.py modes/__init__.py
git commit -m "feat: implement QuickMatchMode"
```

---

### Task 5.2: modes/tournament.py — bracket, golden goal, away-team-advances rule

**Files:**
- Create: `modes/tournament.py`
- Create: `tests/test_tournament.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_tournament.py -v
```

- [ ] **Step 3: Write modes/tournament.py**

```python
# modes/tournament.py
import pygame
import random
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK, WHITE, GRAY, GREEN, SCREEN_W, SCREEN_H, FPS, EXTRA_TIME_MINUTES


class TournamentBracket:
    """Pure logic for 16-team knockout bracket."""

    def __init__(self, teams, player_team_name):
        self.teams = list(teams)
        random.shuffle(self.teams)
        self.player_team_name = player_team_name
        self.champion = None
        self.current_round_matches = self._pairs(self.teams)
        self.results = [None] * len(self.current_round_matches)

    def _pairs(self, lst):
        return [(lst[i], lst[i + 1]) for i in range(0, len(lst), 2)]

    def record_result(self, idx, winner_idx):
        home, away = self.current_round_matches[idx]
        self.results[idx] = home if winner_idx == 0 else away

    def advance_round(self):
        winners = [r for r in self.results if r is not None]
        if len(winners) == 1:
            self.champion = winners[0]
            self.current_round_matches = []
        else:
            self.current_round_matches = self._pairs(winners)
            self.results = [None] * len(self.current_round_matches)

    def get_player_match_idx(self):
        for i, (h, a) in enumerate(self.current_round_matches):
            if h['name'] == self.player_team_name or a['name'] == self.player_team_name:
                return i
        return None

    @property
    def round_name(self):
        return {8: 'Round of 16', 4: 'Quarter-Finals',
                2: 'Semi-Finals', 1: 'Final'}.get(len(self.current_round_matches), '?')


class TournamentMode:
    """
    Draw resolution when scores are level after full time:
      - Play up to 2 golden goal ET periods (EXTRA_TIME_MINUTES each)
      - If still level: AWAY TEAM ADVANCES (deterministic, per spec)
    """

    def __init__(self, manager):
        self.manager = manager
        self.bracket = None
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'setup'
        self.current_match_idx = None
        self.extra_time_periods = 0
        self.duration = 5
        self.difficulty = 'Medium'
        self.player_team = None
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_s = pygame.font.SysFont('Arial', 20)

    def on_enter(self, home=None, away=None, duration=5, difficulty='Medium', **kwargs):
        from data.teams import get_all_teams
        self.duration = duration
        self.difficulty = difficulty
        player_team = home  # home = player's chosen team

        all_teams = get_all_teams()
        if player_team is None:
            player_team = random.choice(all_teams)

        others = [t for t in all_teams if t['name'] != player_team['name']]
        selected = random.sample(others, 15) + [player_team]
        self.bracket = TournamentBracket(selected, player_team['name'])
        self.player_team = player_team
        self.phase = 'round_start'

    def update(self, events, keys):
        # Key handler for terminal phases
        if self.phase in ('trophy', 'eliminated'):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    return 'menu'
            return None

        if self.phase == 'result':
            result = self.result_screen.update(events, keys)
            if result is not None:
                self._after_match_result()
            return None

        if self.phase == 'match' and self.match:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'menu'
            self.match.update(keys_p1=keys, keys_p2=None)
            if self.match.state == 'FULL_TIME':
                self._on_match_full_time()
            return None

        if self.phase == 'round_start':
            self._simulate_cpu_matches()
            self._start_player_match()

        return None

    def _on_match_full_time(self):
        score = self.match.score
        if score[0] == score[1]:
            if self.extra_time_periods < 2:
                # Another golden goal ET period
                self.extra_time_periods += 1
                self.match.remaining_frames = EXTRA_TIME_MINUTES * 60 * FPS
                self.match.state = 'KICKOFF'
            else:
                # Still level after 2 ET periods: away team advances (spec rule)
                home, away = self.bracket.current_round_matches[self.current_match_idx]
                winner_is_away = (self.match.away_team.name == away['name'])
                winner_idx = 1  # away team always advances on coin-flip rule
                self.bracket.record_result(self.current_match_idx, winner_idx)
                result = self.match.get_result()
                result['coin_flip'] = True
                result['coin_winner'] = away['name']
                self.phase = 'result'
                self.result_screen.on_enter(result=result, next_screen=None)
        else:
            winner_idx = 0 if score[0] > score[1] else 1
            self.bracket.record_result(self.current_match_idx, winner_idx)
            self.phase = 'result'
            self.result_screen.on_enter(result=self.match.get_result(), next_screen=None)

    def _simulate_cpu_matches(self):
        player_idx = self.bracket.get_player_match_idx()
        for i, (home, away) in enumerate(self.bracket.current_round_matches):
            if i == player_idx or self.bracket.results[i] is not None:
                continue
            self.bracket.record_result(i, _simulate_winner(home['rating'], away['rating']))

    def _start_player_match(self):
        idx = self.bracket.get_player_match_idx()
        if idx is None:
            return
        self.current_match_idx = idx
        home, away = self.bracket.current_round_matches[idx]
        self.match = Match(home, away, self.duration,
                           'HUMAN_P1', 'CPU', self.difficulty)
        self.extra_time_periods = 0
        self.phase = 'match'

    def _after_match_result(self):
        self.bracket.advance_round()
        if self.bracket.champion:
            self.phase = 'trophy'
        elif self.bracket.get_player_match_idx() is None:
            self.phase = 'eliminated'
        else:
            self.phase = 'round_start'

    def draw(self, surface):
        if self.phase == 'result':
            self.result_screen.draw(surface)
        elif self.phase == 'match' and self.match:
            surface.fill(BLACK)
            draw_pitch(surface)
            self.match.home_team.draw(surface)
            self.match.away_team.draw(surface)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
            rnd = self.font_s.render(self.bracket.round_name, True, (150, 150, 150))
            surface.blit(rnd, (10, 48))
        elif self.phase == 'trophy':
            self._draw_end(surface, 'TOURNAMENT WINNER!',
                           self.bracket.champion['name'] if self.bracket.champion else '?',
                           (255, 220, 0))
        elif self.phase == 'eliminated':
            self._draw_end(surface, 'ELIMINATED',
                           'Better luck next time', WHITE)

    def _draw_end(self, surface, heading, subtext, color):
        surface.fill((5, 15, 5))
        for i, (text, col) in enumerate([(heading, color), (subtext, WHITE),
                                          ('', WHITE), ('Press any key', (150, 150, 150))]):
            surf = self.font.render(text, True, col)
            surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, 180 + i * 70)))


def _simulate_winner(home_rating, away_rating):
    home_eff = home_rating + 0.5
    prob_home = 1 / (1 + 10 ** ((away_rating - home_eff) / 2.5))
    return 0 if random.random() < prob_home else 1
```

- [ ] **Step 4: Run tournament tests**

```bash
pytest tests/test_tournament.py -v
```

Expected: All green.

- [ ] **Step 5: Commit**

```bash
git add modes/tournament.py tests/test_tournament.py
git commit -m "feat: implement TournamentMode with bracket, golden goal ET, away-team-advances rule"
```

---

### Task 5.3: modes/league.py — season, standings, save/load

**Files:**
- Create: `modes/league.py`
- Create: `tests/test_league.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests to confirm failure**

```bash
pytest tests/test_league.py -v
```

- [ ] **Step 3: Implement modes/league.py**

```python
# modes/league.py
import json
import random
import itertools
import pygame
from engine.match import Match
from ui.hud import HUD, draw_pitch
from ui.result import ResultScreen
from settings import BLACK, WHITE, GRAY, GREEN, SCREEN_W, SCREEN_H, FPS


# ----------------------------------------------------------------
# Pure helpers
# ----------------------------------------------------------------

def calculate_standings(teams, fixtures):
    table = {t['name']: {'team': t['name'], 'p': 0, 'w': 0, 'd': 0, 'l': 0,
                          'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}
             for t in teams}
    for f in fixtures:
        if not f.get('played'):
            continue
        h, a = f['home'], f['away']
        hg, ag = f['score']
        for key, delta in [(h, (1, hg, ag)), (a, (1, ag, hg))]:
            table[key]['p'] += delta[0]
            table[key]['gf'] += delta[1]
            table[key]['ga'] += delta[2]
        if hg > ag:
            table[h]['w'] += 1; table[h]['pts'] += 3; table[a]['l'] += 1
        elif hg < ag:
            table[a]['w'] += 1; table[a]['pts'] += 3; table[h]['l'] += 1
        else:
            table[h]['d'] += 1; table[h]['pts'] += 1
            table[a]['d'] += 1; table[a]['pts'] += 1
    for r in table.values():
        r['gd'] = r['gf'] - r['ga']
    return sorted(table.values(), key=lambda r: (-r['pts'], -r['gd'], -r['gf'], r['team']))


def simulate_match_score(home_rating, away_rating):
    home_eff = home_rating + 0.5
    prob_home = 1 / (1 + 10 ** ((away_rating - home_eff) / 2.5))
    r = random.random()
    if r < prob_home * 0.65:
        hg = random.randint(1, max(1, home_rating)); ag = random.randint(0, max(0, hg - 1))
    elif r < prob_home * 0.65 + 0.25:
        g = random.randint(0, max(1, min(home_rating, away_rating))); hg = ag = g
    else:
        ag = random.randint(1, max(1, away_rating)); hg = random.randint(0, max(0, ag - 1))
    return hg, ag


def _generate_fixtures(teams):
    names = [t['name'] for t in teams]
    pairs = list(itertools.permutations(names, 2))
    random.shuffle(pairs)
    fixtures = []
    matchday = 1
    remaining = list(pairs)
    while remaining:
        used = set()
        day = []
        leftover = []
        for home, away in remaining:
            if home not in used and away not in used:
                day.append({'matchday': matchday, 'home': home, 'away': away,
                            'played': False, 'score': None})
                used.add(home); used.add(away)
            else:
                leftover.append((home, away))
        if day:
            fixtures.extend(day); matchday += 1
        remaining = leftover
        if remaining and not day:
            for home, away in remaining:
                fixtures.append({'matchday': matchday, 'home': home, 'away': away,
                                 'played': False, 'score': None})
                matchday += 1
            break
    return fixtures


class Season:
    def __init__(self, league_name, player_team, teams, duration=5, difficulty='Medium'):
        self.league_name = league_name
        self.player_team = player_team
        self.teams = teams
        self.duration = duration
        self.difficulty = difficulty
        self.fixtures = _generate_fixtures(teams)
        self.current_matchday = 1
        self.total_matchdays = max((f['matchday'] for f in self.fixtures), default=0)

    def get_player_fixture(self, matchday):
        for f in self.fixtures:
            if f['matchday'] == matchday and not f['played']:
                if f['home'] == self.player_team or f['away'] == self.player_team:
                    return f
        return None

    def simulate_matchday(self, matchday):
        """Simulate all non-player fixtures on matchday."""
        for f in self.fixtures:
            if f['matchday'] != matchday or f['played']:
                continue
            if f['home'] == self.player_team or f['away'] == self.player_team:
                continue
            hd = next((t for t in self.teams if t['name'] == f['home']), None)
            ad = next((t for t in self.teams if t['name'] == f['away']), None)
            if hd and ad:
                f['score'] = list(simulate_match_score(hd['rating'], ad['rating']))
                f['played'] = True

    def record_player_result(self, fixture, score):
        fixture['score'] = list(score)
        fixture['played'] = True

    def advance_matchday(self):
        self.current_matchday += 1


def save_season(season, path='save.json'):
    data = {
        'league': season.league_name,
        'season': 1,
        'player_team': season.player_team,
        'match_duration_minutes': season.duration,
        'difficulty': season.difficulty,
        'current_matchday': season.current_matchday,
        'total_matchdays': season.total_matchdays,
        'standings': calculate_standings(season.teams, season.fixtures),
        'fixtures': season.fixtures,
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_season(path, teams):
    """Load season state from JSON file. teams: list of team dicts for the league."""
    with open(path, 'r') as f:
        data = json.load(f)
    season = Season.__new__(Season)
    season.league_name = data['league']
    season.player_team = data['player_team']
    season.teams = teams
    season.duration = data.get('match_duration_minutes', 5)
    season.difficulty = data.get('difficulty', 'Medium')
    season.current_matchday = data['current_matchday']
    season.total_matchdays = data['total_matchdays']
    season.fixtures = data['fixtures']
    return season


# ----------------------------------------------------------------
# LeagueMode screen
# ----------------------------------------------------------------

class LeagueMode:
    def __init__(self, manager):
        self.manager = manager
        self.season = None
        self.match = None
        self.hud = HUD()
        self.result_screen = ResultScreen(manager)
        self.phase = 'standings'
        self.player_fixture = None
        self.save_path = 'save.json'
        self.font_h = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_m = pygame.font.SysFont('Courier New', 16)
        self.font_s = pygame.font.SysFont('Arial', 14)

    def on_enter(self, league_name=None, player_team=None, teams=None,
                 duration=5, difficulty='Medium', load=False, **kwargs):
        if load:
            try:
                self.season = load_season(self.save_path, teams or [])
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return  # silently stay on menu if save file bad
        else:
            if league_name and player_team and teams:
                self.season = Season(league_name, player_team, teams, duration, difficulty)
        self.phase = 'standings'

    def update(self, events, keys):
        if self.phase == 'season_end':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    return 'menu'
            return None

        if self.phase == 'result':
            r = self.result_screen.update(events, keys)
            if r is not None:
                self._after_match()
            return None

        if self.phase == 'match' and self.match:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'menu'
            self.match.update(keys_p1=keys, keys_p2=None)
            if self.match.state == 'FULL_TIME':
                if self.player_fixture:
                    self.season.record_player_result(self.player_fixture,
                                                     list(self.match.score))
                save_season(self.season, self.save_path)
                self.phase = 'result'
                self.result_screen.on_enter(result=self.match.get_result(), next_screen=None)
            return None

        if self.phase == 'standings':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    if event.key == pygame.K_RETURN:
                        self._start_matchday()
        return None

    def _start_matchday(self):
        if not self.season:
            return
        md = self.season.current_matchday
        if md > self.season.total_matchdays:
            self.phase = 'season_end'
            return
        self.season.simulate_matchday(md)
        self.player_fixture = self.season.get_player_fixture(md)
        if self.player_fixture:
            hd = next(t for t in self.season.teams if t['name'] == self.player_fixture['home'])
            ad = next(t for t in self.season.teams if t['name'] == self.player_fixture['away'])
            is_home = (hd['name'] == self.season.player_team)
            hc = 'HUMAN_P1' if is_home else 'CPU'
            ac = 'CPU' if is_home else 'HUMAN_P1'
            self.match = Match(hd, ad, self.season.duration, hc, ac, self.season.difficulty)
            self.phase = 'match'
        else:
            # No player fixture this matchday
            self.season.advance_matchday()

    def _after_match(self):
        self.season.advance_matchday()
        save_season(self.season, self.save_path)
        if self.season.current_matchday > self.season.total_matchdays:
            self.phase = 'season_end'
        else:
            self.phase = 'standings'

    def draw(self, surface):
        surface.fill(BLACK)
        if self.phase == 'match' and self.match:
            draw_pitch(surface)
            self.match.home_team.draw(surface)
            self.match.away_team.draw(surface)
            self.match.ball.draw(surface)
            self.hud.draw(surface, self.match)
        elif self.phase == 'result':
            self.result_screen.draw(surface)
        elif self.phase == 'standings':
            self._draw_standings(surface)
        elif self.phase == 'season_end':
            self._draw_season_end(surface)

    def _draw_standings(self, surface):
        if not self.season:
            return
        md = self.season.current_matchday
        title = self.font_h.render(
            f"{self.season.league_name}  —  Matchday {md} / {self.season.total_matchdays}",
            True, WHITE)
        surface.blit(title, (20, 10))

        header = self.font_m.render(
            f"{'#':>2}  {'TEAM':<22}{'P':>3}{'W':>3}{'D':>3}{'L':>3}{'GF':>4}{'GA':>4}{'GD':>5}{'PTS':>4}",
            True, GRAY)
        surface.blit(header, (20, 40))

        standings = calculate_standings(self.season.teams, self.season.fixtures)
        n = len(standings)
        for i, row in enumerate(standings):
            y = 60 + i * 21
            if y > SCREEN_H - 40:
                break
            color = (100, 180, 255) if i < 4 else (255, 100, 100) if i >= n - 3 else WHITE
            if row['team'] == self.season.player_team:
                pygame.draw.rect(surface, (0, 50, 0), (18, y - 2, SCREEN_W - 36, 20))
            line = self.font_m.render(
                f"{i+1:>2}  {row['team']:<22}{row['p']:>3}{row['w']:>3}{row['d']:>3}{row['l']:>3}{row['gf']:>4}{row['ga']:>4}{row['gd']:>+5}{row['pts']:>4}",
                True, color)
            surface.blit(line, (20, y))

        hint = self.font_s.render('Enter → Play matchday   Esc → Menu', True, GRAY)
        surface.blit(hint, (20, SCREEN_H - 22))

    def _draw_season_end(self, surface):
        font = pygame.font.SysFont('Arial', 36, bold=True)
        standings = calculate_standings(self.season.teams, self.season.fixtures)
        champion = standings[0]['team'] if standings else '?'
        for i, (text, color) in enumerate([
            ('SEASON COMPLETE', (255, 220, 0)),
            (f'Champion: {champion}', WHITE),
            ('', WHITE),
            ('Press any key to continue', GRAY),
        ]):
            surf = font.render(text, True, color)
            surface.blit(surf, surf.get_rect(center=(SCREEN_W // 2, 180 + i * 70)))
```

- [ ] **Step 4: Run league tests**

```bash
pytest tests/test_league.py -v
```

Expected: All green.

- [ ] **Step 5: Commit**

```bash
git add modes/league.py tests/test_league.py
git commit -m "feat: implement League season with standings, simulation, save/load"
```

---

### Task 5.4: Full integration smoke test

- [ ] **Step 1: Run the complete test suite**

```bash
pytest tests/ -v
```

Expected: All tests pass (green). Zero failures.

- [ ] **Step 2: Verify main.py imports without error**

All modules are now written. Verify:

```bash
python -c "import main; print('OK')"
```

Expected: `OK` — no ImportError.

- [ ] **Step 3: Launch the game**

```bash
python main.py
```

Expected:
- 800×600 window opens
- Dark green main menu with 6 items
- Arrow keys navigate, Enter selects, Esc returns to menu from any screen

- [ ] **Step 4: Smoke test — Quick Match**

1. Menu → "New Quick Match"
2. Select any league, pick a home team, pick an away team
3. Match loads: striped pitch, 22 players, ball at centre
4. Press W/A/S/D: home team active player moves (yellow highlight ring)
5. Hold Left Shift near ball: ball is kicked
6. Countdown timer visible in top-right (MM:SS)
7. "HALF TIME" banner at midpoint; teams swap ends
8. "FULL TIME" triggers result screen showing final score
9. Any key returns to menu

- [ ] **Step 5: Smoke test — Tournament**

1. Menu → "New Tournament"
2. TeamSelectScreen: pick one team
3. Tournament auto-draws 16 teams; CPU matches simulated instantly
4. Player's match plays live (full match mechanics)
5. Win → next round; lose → eliminated screen
6. Win the final → trophy screen
7. Any key returns to menu

- [ ] **Step 6: Smoke test — League Season**

1. Menu → "New Season"
2. Pick a league + team
3. Standings table shows (sorted by points)
4. Press Enter: player's fixture loads and is playable
5. After full time: standings update, matchday advances
6. `save.json` exists in repo root with correct schema fields
7. Menu → "Load Season" loads it back

- [ ] **Step 7: Verify save.json schema**

After playing one league matchday, check:

```bash
python -c "
import json
with open('save.json') as f:
    d = json.load(f)
required = ['league','season','player_team','match_duration_minutes',
            'difficulty','current_matchday','total_matchdays','standings','fixtures']
for k in required:
    assert k in d, f'Missing key: {k}'
print('Schema OK')
"
```

Expected: `Schema OK`

- [ ] **Step 8: Final commit**

```bash
git add .
git commit -m "feat: complete Total Soccer v1 — all modes playable"
```

---

## Summary

| Chunk | Tasks | Key deliverables |
|---|---|---|
| 1 | 1.1–1.4 | Project scaffold (root-level packages), settings, 96 club teams, test infra |
| 2 | 2.1–2.2 | Ball physics + goal detection, Player with hysteresis switching |
| 3 | 3.1–3.3 | Team (4-4-2), AI state machine (SUPPORT/ATTACK/DEFEND), Match state machine |
| 4 | 4.1–4.5 | ScreenManager with config dict, all 5 UI screens, settings wired to gameplay |
| 5 | 5.1–5.4 | Quick Match, Tournament (away-team-advances ET), League + save/load, integration |

**Run `pytest tests/ -v` after every task. All tests must stay green throughout.**
