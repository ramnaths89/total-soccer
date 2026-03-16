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
