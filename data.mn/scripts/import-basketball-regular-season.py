"""Import the saved 2025–26 MBA CSV export without changing its source files."""
import argparse
import csv
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/mongolian-basketball-2025-26-regular"
TEAMS = {
    "ХАСЫН ХҮЛЭГҮҮД": "KUL", "БИШРЭЛТ МЕТАЛЛ": "BTM",
    "ЗАВХАН БРОДЕРС": "ZVB", "ДАРХАН ЮНАЙТЕД": "DUA",
    "БИ СИ ЭЙЧ НАЙТС": "BCH", "СЭЛЭНГЭ БОДОНС": "SEL",
    "БҮРЭН СКОР МОНГОЛИАНС": "BSM", "ЭС ЖИ ЭЙПС": "SGA",
    "ОМНИ ЭРДЭНЭТ МАЙНЕРС": "ETM", "ХААН ШОНХОРУУД": "KHF",
}
PLAYER_FIELDS = {
    "fg_made": "made_field_goals", "fg_attempted": "attempted_field_goals",
    "two_pt_made": "made_two_point_field_goals", "two_pt_attempted": "attempted_two_point_field_goals",
    "three_pt_made": "made_three_point_field_goals", "three_pt_attempted": "attempted_three_point_field_goals",
    "ft_made": "made_free_throws", "ft_attempted": "attempted_free_throws",
    "off_rebounds": "offensive_rebounds", "def_rebounds": "defensive_rebounds",
    "total_rebounds": "total_rebounds", "assists": "assists", "turnovers": "turnovers",
    "steals": "steals", "blocks": "blocks", "personal_fouls": "personal_fouls",
    "efficiency": "efficiency", "points": "points",
}
TEAM_FIELDS = {
    "fg_made": "fieldGoalMade", "fg_attempted": "fieldGoalAttempt",
    "two_pt_made": "twoPointMade", "two_pt_attempted": "twoPointAttempt",
    "three_pt_made": "threePointMade", "three_pt_attempted": "threePointAttempt",
    "ft_made": "freeThrowMade", "ft_attempted": "freeThrowAttempt",
    "off_rebounds": "offensiveRebound", "def_rebounds": "defensiveRebound",
    "total_rebounds": "rebound", "assists": "assist", "turnovers": "turnover",
    "steals": "steal", "blocks": "block", "personal_fouls": "personalFoul",
    "efficiency": "efficiency", "points": "point",
}


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(value):
    if value is None or str(value).strip() == "":
        return None
    n = float(value)
    return int(n) if n.is_integer() else n


def import_collection(source):
    (OUT / "sources").mkdir(parents=True, exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    files = {
        "games": "mba-regular-season-games-2025-2026",
        "players": "mba-player-game-stats-2025-2026",
        "totals": "mba-team-game-stats-2025-2026",
    }
    for stem in files.values():
        for language in ("en", "mn"):
            filename = f"{stem}-{language}.csv"
            shutil.copy2(source / filename, OUT / "sources" / filename)
    raw = {key: rows(OUT / "sources" / f"{stem}-en.csv") for key, stem in files.items()}
    collection = {"games": [], "players": [], "team_totals": [], "qa_checks": [], "missing_games": []}
    game_lookup = {}
    for g in raw["games"]:
        if g["status"] != "EndGame":
            raise ValueError(f"Unfinished game in regular-season export: {g['game_id']}")
        game = {
            "game_id": "MBA-" + g["game_id"], "source_game_id": g["game_id"],
            "season": "2025-26", "phase": "Regular season", "round": "Regular season",
            "date": g["date"], "team1_code": TEAMS[g["home_team"]], "team2_code": TEAMS[g["away_team"]],
            "team1_score": number(g["home_score"]), "team2_score": number(g["away_score"]),
            "boxscore_available": True, "overtime_periods": None,
            "source_file": f"{files['games']}-en.csv · MBA game {g['game_id']}",
            "source_type": "MBA saved API export",
        }
        if g["game_id"] in game_lookup:
            raise ValueError(f"Duplicate game ID: {g['game_id']}")
        game_lookup[g["game_id"]] = game
        collection["games"].append(game)
    for p in raw["players"]:
        game = game_lookup[p["game_id"]]
        stats = {key: number(p[field]) for key, field in PLAYER_FIELDS.items()}
        seconds = number(p["played_minutes_seconds"])
        if seconds is None and p["played_minutes_string"] in ("0:00", "00:00", "00:00:00"):
            seconds = 0
        # The numeric seconds field avoids spreadsheet-style 40:00:00 strings.
        minutes = f"{int(seconds)//60:02}:{int(seconds)%60:02}" if seconds is not None else None
        dnp = seconds == 0 and all(stats[k] == 0 for k in (
            "points", "total_rebounds", "assists", "steals", "blocks", "turnovers",
            "fg_attempted", "ft_attempted", "personal_fouls"))
        row = {
            "game_id": game["game_id"], "team_code": TEAMS[p["teamId_name"]],
            "player_name_mn": (p["playerId_first_name"] + " " + p["playerId_last_name"]).strip(),
            "source_player_id": p["playerId_id"],
            "jersey_no": number(p["seasonTeamPlayer_jerseyNumber"] or p["jerseyNumber"] or p["playerNumber"]),
            "starter": p["is_starter"].lower() == "true", "did_not_play": dnp,
            "minutes": minutes, "plus_minus": None, **stats,
        }
        collection["players"].append(row)
        if (seconds is None or seconds == 0) and not dnp:
            collection["qa_checks"].append({"game_id": game["game_id"], "team_code": row["team_code"],
                "stat": "minutes", "issue": "Playing time is missing or zero alongside recorded activity in the saved MBA export; player statistics retained."})
    for t in raw["totals"]:
        game = game_lookup[t["game_id"]]
        team = TEAMS[t["team"]]
        parts = [float(n) for n in t["minute"].split(":")] if t["minute"] else []
        total_seconds = round(parts[0]*3600 + parts[1]*60 + parts[2]) if len(parts) == 3 else None
        minutes = f"{total_seconds//60}:{total_seconds%60:02}" if total_seconds is not None else None
        stats = {key: number(t[field]) for key, field in TEAM_FIELDS.items()}
        # Use the game-level fields, never team_* season summaries in the same CSV.
        margin = game["team1_score"] - game["team2_score"]
        collection["team_totals"].append({"game_id": game["game_id"], "team_code": team,
            "minutes": minutes, "plus_minus": margin if team == game["team1_code"] else -margin, **stats})
    target = OUT / "data/collection.json"
    target.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# 2025–26 regular-season import\n\n"
        "Imported from the saved MBA API export in the September 24 project. "
        "Contains 135 completed regular-season games, 270 team game rows, and 3,415 player rows. "
        "The original EN/MN CSV pairs are copied unchanged into sources/.\n\n"
        "Game IDs use the MBA- prefix to keep the API namespace separate from FIBA report IDs. "
        "Team names are mapped to the website's stable team codes. Player names are retained as supplied. "
        "Numeric playing time is formatted as minutes:seconds. Zero-time rows with all activity statistics "
        "equal to zero are treated as DNP; absent time remains unavailable. "
        "Team totals use game-level fields, not embedded season summaries. "
        "The source does not provide quarter scores or player plus/minus.\n",
        encoding="utf-8",
    )
    print(json.dumps({key: len(value) for key, value in collection.items()}))
    print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory with the six language-paired MBA CSV files")
    import_collection(parser.parse_args().source)
