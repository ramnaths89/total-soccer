# Total Soccer — Design Spec
**Date:** 2026-03-16
**Platform:** Python + Pygame
**Status:** Approved

---

## Overview

A faithful remake of the classic 1997 PC game Total Soccer. Top-down 2D football with 11v11, five major European club leagues, three game modes (Quick Match, Tournament, League/Season), local 2-player support, and AI opponents.

---

## Technology

| Item | Choice |
|---|---|
| Language | Python 3.11+ |
| Framework | Pygame 2.x |
| Resolution | 800×600 pixels |
| Target FPS | 60 |
| Save format | JSON (`save.json`) |

---

## Project Structure

```
total_soccer/
├── main.py                  # Entry point, game loop, ScreenManager
├── settings.py              # All constants: pitch dimensions, colors, physics, keybindings, defaults
├── data/
│   └── teams.py             # All 5 leagues, club data (see Team Schema)
├── engine/
│   ├── ball.py              # Ball physics: velocity, friction, collision, bounce, goal detection
│   ├── player.py            # Player sprite, movement, role, active-player logic
│   ├── team.py              # Team formation, positional anchors, active player tracking
│   ├── match.py             # Match state machine, timer, score, restarts
│   └── ai.py                # AI controller per player: state machine + transitions
├── modes/
│   ├── quick_match.py       # Team select → match → result → menu
│   ├── tournament.py        # 16-team knockout bracket, golden goal extra time
│   └── league.py            # Round-robin season, simulated results, JSON save/load
└── ui/
    ├── menu.py              # Main menu screen
    ├── team_select.py       # Team picker with league filter
    ├── hud.py               # In-match overlay: score, countdown timer, possession bar
    ├── result.py            # Post-match result screen
    └── settings_screen.py   # Match duration, difficulty, controls display
```

---

## Settings & Constants (`settings.py`)

All magic numbers live here. Nothing is hardcoded elsewhere.

```python
# Screen
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# Pitch layout (pixels) — centered in screen with margins
PITCH_LEFT   = 60
PITCH_RIGHT  = 740
PITCH_TOP    = 50
PITCH_BOTTOM = 550
PITCH_W = PITCH_RIGHT - PITCH_LEFT   # 680
PITCH_H = PITCH_BOTTOM - PITCH_TOP   # 500

# Centre
CENTRE_X = (PITCH_LEFT + PITCH_RIGHT) // 2   # 400
CENTRE_Y = (PITCH_TOP + PITCH_BOTTOM) // 2   # 300
CENTRE_CIRCLE_RADIUS = 50

# Goals — each goal is centered vertically on the pitch (at CENTRE_Y)
# GOAL_MOUTH = vertical span of the goal opening (top to bottom post)
# GOAL_DEPTH = how far the goal net extends behind the goal line (visual only, not used for detection)
GOAL_MOUTH  = 80                              # vertical opening in pixels
GOAL_DEPTH  = 20                              # net depth behind the line (visual only)
GOAL_TOP    = CENTRE_Y - GOAL_MOUTH // 2      # 260  (top post y)
GOAL_BOTTOM = CENTRE_Y + GOAL_MOUTH // 2      # 340  (bottom post y)
# Left goal net rect:  x=[PITCH_LEFT-GOAL_DEPTH .. PITCH_LEFT],  y=[GOAL_TOP .. GOAL_BOTTOM]
# Right goal net rect: x=[PITCH_RIGHT .. PITCH_RIGHT+GOAL_DEPTH], y=[GOAL_TOP .. GOAL_BOTTOM]
# Goal detection: ball CENTER crosses x<=PITCH_LEFT or x>=PITCH_RIGHT AND GOAL_TOP<=ball.y<=GOAL_BOTTOM
# (the ball only needs to cross the goal LINE — no extra depth check required)

# Penalty areas — one at each end, centered vertically on CENTRE_Y, flush with pitch boundary
# Left penalty area:  x=[PITCH_LEFT .. PITCH_LEFT+PENALTY_W],   y=[CENTRE_Y-PENALTY_H//2 .. CENTRE_Y+PENALTY_H//2]
# Right penalty area: x=[PITCH_RIGHT-PENALTY_W .. PITCH_RIGHT], y=[CENTRE_Y-PENALTY_H//2 .. CENTRE_Y+PENALTY_H//2]
PENALTY_W = 120   # horizontal depth from goal line into pitch
PENALTY_H = 200   # vertical span (centered on CENTRE_Y: y=200 to y=400)

# Ball
BALL_RADIUS   = 6
BALL_FRICTION = 0.97   # velocity multiplier per frame
KICK_POWER_BASE = 12   # pixels/frame, scaled by player rating

# Players
PLAYER_RADIUS   = 10
PLAYER_SPEED_GK = 3.0
PLAYER_SPEED_DEF = 3.5
PLAYER_SPEED_MID = 4.0
PLAYER_SPEED_FWD = 4.5

# Match defaults
DEFAULT_MATCH_MINUTES = 5
HALF_TIME_PAUSE_MS    = 3000   # 3 seconds pause at half-time
GOAL_PAUSE_MS         = 2000   # 2 seconds celebration pause after goal
EXTRA_TIME_MINUTES    = 2      # golden goal extra time per period
SET_PIECE_WAIT_FRAMES = 60     # frames all players freeze before set piece is taken

# Active player switching hysteresis
ACTIVE_SWITCH_HYSTERESIS   = 30   # px: new player must be this much closer to trigger switch
ACTIVE_SWITCH_MIN_FRAMES   = 10   # frames before another switch is evaluated

# AI difficulty multipliers (applied to reaction distance and kick accuracy)
AI_DIFFICULTY = {
    "Easy":   {"reaction": 120, "accuracy": 0.6},
    "Medium": {"reaction": 80,  "accuracy": 0.8},
    "Hard":   {"reaction": 40,  "accuracy": 0.95},
}
```

---

## Data: Teams (`data/teams.py`)

### Team Schema

```python
{
    "name":          "Arsenal",
    "short_name":    "ARS",
    "league":        "Premier League",
    "kit_primary":   "#EF0107",   # hex color
    "kit_secondary": "#FFFFFF",
    "rating":        4,            # 1–5 stars, used for AI match simulation
}
```

No individual player names needed — players are identified by squad number (1–11) and role only.

### Leagues & Clubs

- **Premier League** (20 clubs): Man Utd, Arsenal, Chelsea, Liverpool, Man City, Tottenham, Newcastle, Aston Villa, West Ham, Brighton, Brentford, Fulham, Crystal Palace, Wolves, Everton, Nottm Forest, Bournemouth, Luton, Burnley, Sheffield Utd
- **La Liga** (20 clubs): Real Madrid, Barcelona, Atletico Madrid, Sevilla, Real Sociedad, Villarreal, Athletic Bilbao, Valencia, Real Betis, Osasuna, Getafe, Celta Vigo, Girona, Cadiz, Almeria, Granada, Las Palmas, Mallorca, Rayo Vallecano, Alaves
- **Serie A** (20 clubs): Juventus, AC Milan, Inter Milan, AS Roma, Napoli, Lazio, Atalanta, Fiorentina, Torino, Bologna, Udinese, Sassuolo, Lecce, Monza, Empoli, Hellas Verona, Salernitana, Frosinone, Cagliari, Genoa
- **Bundesliga** (18 clubs): Bayern Munich, Borussia Dortmund, Bayer Leverkusen, RB Leipzig, Union Berlin, Freiburg, Eintracht Frankfurt, Wolfsburg, B. Monchengladbach, Mainz, Hoffenheim, Werder Bremen, Augsburg, Stuttgart, Bochum, Cologne, Darmstadt, Heidenheim
- **Ligue 1** (18 clubs): PSG, Marseille, Lyon, Monaco, Lille, Nice, Lens, Rennes, Strasbourg, Nantes, Reims, Toulouse, Lorient, Montpellier, Clermont, Le Havre, Metz, Brest

---

## Pitch Layout

```
 x=60                        x=400                       x=740
  |__________________________|___________________________|
  |          PITCH_TOP=50                                |
  |  [GK]  [DEF][DEF][DEF][DEF]  [MID]x4  [FWD][FWD]  |
  |                          (o)                         |  y=300
  |  [FWD][FWD]  [MID]x4  [DEF][DEF][DEF][DEF]  [GK]  |
  |          PITCH_BOTTOM=550                            |
  |________________________________________________________
```

- Home team attacks left→right (starts on left half)
- Away team attacks right→left (starts on right half)
- Teams switch ends at half-time

---

## Formation: 4-4-2 Positional Anchors

Anchors are expressed as fractions of pitch width/height, flipped for away team.

| Role | #  | Home anchor (x%, y%) |
|------|----|----------------------|
| GK   | 1  | (5%, 50%)            |
| DEF  | 2  | (20%, 25%)           |
| DEF  | 3  | (20%, 42%)           |
| DEF  | 4  | (20%, 58%)           |
| DEF  | 5  | (20%, 75%)           |
| MID  | 6  | (40%, 25%)           |
| MID  | 7  | (40%, 42%)           |
| MID  | 8  | (40%, 58%)           |
| MID  | 9  | (40%, 75%)           |
| FWD  | 10 | (60%, 38%)           |
| FWD  | 11 | (60%, 62%)           |

Anchors shift forward/backward as a block based on team AI mode (DEFENSIVE / OFFENSIVE), clamped to own/opponent half respectively.

---

## Engine

### Ball (`engine/ball.py`)

- `pos`: `pygame.Vector2`
- `vel`: `pygame.Vector2`, decays by `BALL_FRICTION` each frame
- **Boundary collision:** if ball exits pitch left/right sideline → throw-in; if exits top/bottom byline → corner kick or goal kick depending on which team touched last
- **Goal detection:** a goal is scored when the ball's center crosses the goal line (x ≤ PITCH_LEFT or x ≥ PITCH_RIGHT) AND its y is between `GOAL_TOP` and `GOAL_BOTTOM`
- **Kick:** when a player collides with the ball (distance < PLAYER_RADIUS + BALL_RADIUS), ball velocity is set toward the player's facing direction at `KICK_POWER_BASE * (player.rating / 5.0)` + small random spread for accuracy

### Player (`engine/player.py`)

- `pos`: `pygame.Vector2`
- `vel`: `pygame.Vector2`
- `role`: `GK | DEF | MID | FWD`
- `team`: reference to owning `Team`
- `is_active`: bool — the one player per team currently controlled (human or AI-directed)
- `speed`: float, from `settings.py` per role
- **Active switching:** the active player is the one with the shortest distance to the ball. To prevent flickering when two players trade proximity rapidly, a **hysteresis rule** applies: the current active player retains control until a different player is closer by at least `ACTIVE_SWITCH_HYSTERESIS = 30` pixels (defined in `settings.py`). Additionally, after a switch the new active player holds for a minimum of `ACTIVE_SWITCH_MIN_FRAMES = 10` frames before another switch is evaluated. Tie-breaking (equal distance): lowest squad number wins.
- **Non-active players:** AI-controlled regardless of human/CPU team — they follow their positional anchors adjusted by team AI mode

### Team (`engine/team.py`)

- Holds list of 11 `Player` instances
- `ai_mode`: `DEFENSIVE | OFFENSIVE` — set each frame based on ball x position relative to centre
- `controlled_by`: `HUMAN_P1 | HUMAN_P2 | CPU`
- Each frame: update `ai_mode`, call active-player selection, call AI update for all non-active players

### Match State Machine (`engine/match.py`)

```
KICKOFF ──(space/any key)──► PLAYING
PLAYING ──(goal scored)────► GOAL_PAUSE (2s) ──► KICKOFF
PLAYING ──(half elapsed)───► HALF_TIME (3s) ──► KICKOFF (swap ends)
PLAYING ──(full time)──────► FULL_TIME ──► result screen
PLAYING ──(set piece event)► SET_PIECE_WAIT (60 frames) ──► PLAYING
FULL_TIME (tournament draw)► EXTRA_TIME ──(golden goal or time up)──► FULL_TIME
```

- **Timer:** counts DOWN from `match_minutes * 60` seconds (displayed as MM:SS)
- **Half-time trigger:** when `remaining_time == match_minutes * 30` seconds (half elapsed)
- **Score:** `(home_goals, away_goals)` updated on goal

### AI Controller (`engine/ai.py`)

Each non-active player runs a per-player state machine every frame.

**States and transitions:**

| State | Behavior | Transition to ATTACK | Transition to DEFEND | Transition to SUPPORT |
|---|---|---|---|---|
| `SUPPORT` | Move toward positional anchor | Ball in own third AND nearest to ball | Ball in opponent third AND not nearest | — |
| `ATTACK` | Sprint toward ball, kick if in range | — | Ball crosses into own half | No longer nearest to ball |
| `DEFEND` | Track nearest opponent; GK stays on goal line | Ball enters opponent half | — | Own team regains possession |

**Team AI mode** (set in `team.py`, influences anchor positions):
- `OFFENSIVE`: anchors shift 20% toward opponent goal
- `DEFENSIVE`: anchors shift 20% toward own goal

**GK special rule:** Always stays within 30px of goal line. If ball enters penalty area, GK sprints toward ball regardless of state.

**Simulated match results** (used for non-player fixtures in league mode):
- Winner probability weighted by `rating` difference + uniform random noise (±1 simulated rating)
- Possible outcomes: home win, draw, away win
- Goals scored: Poisson-distributed around `rating * 0.6`

---

## Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Move | W / A / S / D | ↑ / ← / ↓ / → |
| Kick | Left Shift | Right Ctrl |
| Pause | Escape | — |

**Kick behavior:** pressing Kick while near the ball (distance < PLAYER_RADIUS + BALL_RADIUS + 4px tolerance) kicks it in the player's current movement direction (normalized velocity vector). If the player is stationary (velocity magnitude < 0.1), the ball is kicked toward the center of the opponent's goal — i.e., toward `(PITCH_RIGHT, CENTRE_Y)` for home team or `(PITCH_LEFT, CENTRE_Y)` for away team. The same button is used for shooting and passing — direction determines outcome.

**2-player mode:** P1 controls the home team's active player (nearest to ball), P2 controls the away team's active player. All other players on both teams are AI-controlled.

**1-player vs AI mode:** P1 controls home team, CPU controls away team entirely.

---

## Game Modes

### Quick Match (`modes/quick_match.py`)
1. Filter by league (All / specific league)
2. Pick home team
3. Pick away team
4. Set match duration: 1 / 3 / 5 / 10 min (default 5)
5. Choose 1P vs AI or 2P local
6. Play match
7. Result screen → return to menu

### Tournament (`modes/tournament.py`)
- 16 teams drawn at random (from all leagues combined)
- Player picks their team; AI controls all others
- Single-leg knockout: R16 → QF → SF → Final
- **Draw resolution:** if scores are level at full time → play one golden goal extra time period (`EXTRA_TIME_MINUTES = 2` minutes, from `settings.py`). First goal scored wins immediately. If no goal after those 2 minutes → play a second golden goal period (another 2 minutes). If still no goal after both periods → away team advances by coin flip, result displayed on screen with "AWAY TEAM ADVANCES (COIN FLIP)" banner. Maximum 2 ET periods before coin flip.
- No save — completes in one session (~4 matches)
- Trophy screen on winning the Final

### League / Season (`modes/league.py`)
- Player picks one of the 5 leagues
- Full round-robin: each team plays every other team home and away
- Each matchday: player plays their one fixture; all others simulated instantly using ratings
- **Standings columns:** P W D L GF GA GD Pts (3 pts win, 1 pt draw, 0 loss)
- **Tiebreaker order:** Pts → GD → GF → head-to-head (simplified: coin flip if still equal)
- Season end: champion declared, bottom 3 marked relegated (cosmetic — no actual promotion in v1)
- **Save state** persisted to `save.json` after each matchday (single save slot)

### Saved Game Schema (`save.json`)

```json
{
  "league": "Premier League",
  "season": 1,
  "player_team": "Arsenal",
  "match_duration_minutes": 5,
  "current_matchday": 14,
  "total_matchdays": 38,
  "standings": [
    {
      "team": "Arsenal",
      "p": 13, "w": 9, "d": 2, "l": 2,
      "gf": 28, "ga": 12, "gd": 16, "pts": 29
    }
  ],
  "fixtures": [
    {
      "matchday": 1,
      "home": "Arsenal", "away": "Chelsea",
      "played": true, "score": [2, 1]
    }
  ]
}
```

---

## UI Screens

| Screen | Key content |
|---|---|
| Main Menu | New Quick Match / New Tournament / New Season / Load Season / Settings / Quit |
| Team Select | League dropdown (All + 5 leagues), scrollable team list, kit color swatch preview |
| HUD | Score (top center, e.g. `ARS 2 – 1 CHE`), countdown timer (MM:SS), possession bar |
| Half Time | "HALF TIME" banner, current score, 3-second auto-resume |
| Result | Final score, "FULL TIME" banner, Man of the Match (highest-rated active player) |
| Standings | Full league table, top 4 highlighted in blue (Champions League spots), bottom 3 in red |
| Settings | Match duration picker, AI difficulty (Easy / Medium / Hard), controls reference card |
| Tournament Bracket | Visual bracket showing all 16 teams, current round highlighted |

---

## Set Pieces (v1 Scope)

All set pieces use the same simple execution model: ball is teleported to the restart position, match state enters `SET_PIECE_WAIT`, all players freeze for 60 frames, then the designated kicker gets `is_active = True` and `SET_PIECE_WAIT` transitions to `PLAYING`. There is no "press button to take" mechanic — the kicker acts automatically.

| Event | Trigger | Ball position | Kicker |
|---|---|---|---|
| Throw-in | Ball exits top/bottom sideline | Ball placed at exit x, clamped to sideline y | Nearest non-active player of receiving team |
| Corner kick | Ball exits left/right byline; last touch = defending team | Nearest corner of the byline (4 corners: `(PITCH_LEFT, PITCH_TOP)`, `(PITCH_LEFT, PITCH_BOTTOM)`, `(PITCH_RIGHT, PITCH_TOP)`, `(PITCH_RIGHT, PITCH_BOTTOM)`) | Nearest outfield player of attacking team |
| Goal kick | Ball exits left/right byline; last touch = attacking team | Home goal kick: `(PITCH_LEFT + 30, CENTRE_Y)` / Away goal kick: `(PITCH_RIGHT - 30, CENTRE_Y)` | Defending team's GK |
| Goal | Ball center crosses goal line within GOAL_TOP/GOAL_BOTTOM | — | 2s pause → score update → all players reset to formation anchors → kickoff |

**Last-touch tracking:** `match.py` stores `last_touch_team` (updated whenever a player kicks the ball). Used to determine corner vs goal kick.

---

## Out of Scope (v1)

- Free kicks, penalties, offside rule
- Individual player names/stats
- Sound effects / music
- Online multiplayer
- Official team/player licenses
- Multiple save slots
- Promotion/relegation actually changing league rosters
