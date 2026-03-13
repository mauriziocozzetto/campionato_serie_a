from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Montiamo la cartella per i file statici
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- MODELLI ---


class Scorer(BaseModel):
    name: str
    minute: int
    team_side: str


class Team(BaseModel):
    name: str
    logo_url: str


class Match(BaseModel):
    id: int
    date: str
    start_time: str
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    scorers: List[Scorer]

# --- DATABASE OTTIMIZZATO (DIZIONARI) ---


OFFICIAL_LOGOS = {
    "Napoli": "/static/logos/Napoli.png",
    "Torino": "/static/logos/Torino.webp",
    "Lazio": "/static/logos/Lazio.webp",
    "Genoa": "/static/logos/Genoa.webp",
    "Fiorentina": "/static/logos/Fiorentina.webp",
    "Juventus": "/static/logos/Juventus.png",
    "Cagliari": "/static/logos/Cagliari.webp",
    "Como": "/static/logos/Como.webp",
    "Atalanta": "/static/logos/Atalanta.webp",
    "Udinese": "/static/logos/Udinese.webp",
    "Milan": "/static/logos/Milan.webp",
    "Inter": "/static/logos/Inter.webp",
    "Roma": "/static/logos/Roma.webp",
    "Lecce": "/static/logos/Lecce.webp",
    "Cremonese": "/static/logos/Cremonese.webp",
    "Bologna": "/static/logos/Bologna.webp",
    "Verona": "/static/logos/Verona.webp",
    "Parma": "/static/logos/Parma.webp",
    "Pisa": "/static/logos/Pisa.webp"
}

# 1. Dizionario "Flat": Ricerca istantanea O(1) per ID
db_matches: Dict[int, Match] = {
    1: Match(id=1, date="6 Marzo 2026", start_time="20:45",
             home_team=Team(name="Napoli", logo_url=OFFICIAL_LOGOS["Napoli"]),
             away_team=Team(name="Torino", logo_url=OFFICIAL_LOGOS["Torino"]),
             home_score=0, away_score=0, scorers=[]),

    2: Match(id=2, date="7 Marzo 2026", start_time="15:00",
             home_team=Team(name="Cagliari",
                            logo_url=OFFICIAL_LOGOS["Cagliari"]),
             away_team=Team(name="Como", logo_url=OFFICIAL_LOGOS["Como"]),
             home_score=0, away_score=0, scorers=[]),

    3: Match(id=3, date="7 Marzo 2026", start_time="18:00",
             home_team=Team(name="Atalanta",
                            logo_url=OFFICIAL_LOGOS["Atalanta"]),
             away_team=Team(
                 name="Udinese", logo_url=OFFICIAL_LOGOS["Udinese"]),
             home_score=0, away_score=0, scorers=[]),

    4: Match(id=4, date="7 Marzo 2026", start_time="20:45",
             home_team=Team(name="Juventus",
                            logo_url=OFFICIAL_LOGOS["Juventus"]),
             away_team=Team(name="Pisa", logo_url=OFFICIAL_LOGOS["Pisa"]),
             home_score=0, away_score=0, scorers=[]),

    5: Match(id=5, date="8 Marzo 2026", start_time="12:30",
             home_team=Team(name="Lecce", logo_url=OFFICIAL_LOGOS["Lecce"]),
             away_team=Team(name="Cremonese",
                            logo_url=OFFICIAL_LOGOS["Cremonese"]),
             home_score=0, away_score=0, scorers=[]),

    6: Match(id=6, date="8 Marzo 2026", start_time="15:00",
             home_team=Team(
                 name="Bologna", logo_url=OFFICIAL_LOGOS["Bologna"]),
             away_team=Team(name="Verona", logo_url=OFFICIAL_LOGOS["Verona"]),
             home_score=0, away_score=0, scorers=[]),

    7: Match(id=7, date="8 Marzo 2026", start_time="15:00",
             home_team=Team(name="Fiorentina",
                            logo_url=OFFICIAL_LOGOS["Fiorentina"]),
             away_team=Team(name="Parma", logo_url=OFFICIAL_LOGOS["Parma"]),
             home_score=0, away_score=0, scorers=[]),

    8: Match(id=8, date="8 Marzo 2026", start_time="18:00",
             home_team=Team(name="Genoa", logo_url=OFFICIAL_LOGOS["Genoa"]),
             away_team=Team(name="Roma", logo_url=OFFICIAL_LOGOS["Roma"]),
             home_score=0, away_score=0, scorers=[]),

    9: Match(id=9, date="8 Marzo 2026", start_time="20:45",
             home_team=Team(name="Milan", logo_url=OFFICIAL_LOGOS["Milan"]),
             away_team=Team(name="Inter", logo_url=OFFICIAL_LOGOS["Inter"]),
             home_score=0, away_score=0, scorers=[])
}

# 2. Struttura delle Giornate: Organizza gli ID per la visualizzazione
db_matchdays_structure = {
    28: [1, 2, 3, 4, 5, 6, 7, 8, 9]
}

# --- ROTTE HTML ---


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.get("/matches/{match_id}")
async def read_detail(match_id: int):
    return FileResponse('static/detail.html')


@app.get("/matches/{match_id}/scorers/new")
async def read_add_scorer(match_id: int):
    return FileResponse('static/add_scorer.html')


@app.get("/add-scorer")
async def read_add_scorer():
    return FileResponse('static/add_scorer.html')

# --- API ENDPOINTS ---


@app.get("/api/matchdays")
async def get_matchdays():
    result = []
    for day_num in sorted(db_matchdays_structure.keys()):
        match_ids = db_matchdays_structure[day_num]
        matches_list = [db_matches[mid]
                        for mid in match_ids if mid in db_matches]
        result.append({"number": day_num, "matches": matches_list})
    return result


@app.get("/api/matchdays/{matchday_id}/matches/{match_id}")
async def get_match(matchday_id: int, match_id: int):
    # Verifica che la giornata esista e contenga la partita richiesta
    match_ids = db_matchdays_structure.get(matchday_id)
    if not match_ids or match_id not in match_ids:
        raise HTTPException(status_code=404, detail="Match not found")

    match = db_matches.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return match


@app.post("/api/matches/{match_id}/scorers")
async def add_scorer(match_id: int, player_name: str = Form(...),
                     minute: int = Form(...), team_side: str = Form(...)):

    match = db_matches.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.scorers.append(
        Scorer(name=player_name, minute=minute, team_side=team_side))

    if team_side == "home":
        match.home_score += 1
    else:
        match.away_score += 1

    return {"status": "success", "match_id": match_id}
