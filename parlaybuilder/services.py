import requests
from bs4 import BeautifulSoup
import pandas as pd
team_abbreviations = {
        "ATL": "hawks",
        "BOS": "celtics",
        "BRK": "nets",
        "CHO": "hornets",
        "CHI": "bulls",
        "CLE": "cavs",
        "DAL": "mavs",
        "DEN": "nuggets",
        "DET": "pistons",
        "GSW": "warriors",
        "HOU": "rockets",
        "IND": "pacers",
        "LAC": "clippers",
        "LAL": "lakers",
        "MEM": "grizzlies",
        "MIA": "heat",
        "MIL": "bucks",
        "MIN": "timberwolves",
        "NO": "pelicans",
        "NY": "knicks",
        "ORL": "magic",
        "OKC": "thunder",
        "PHI": "sixers",
        "PHO": "suns",
        "POR": "blazers",
        "SA": "spurs",
        "SAC": "kings",
        "TOR": "raptors",
        "UTA": "jazz",
        "WAS": "wizards"
}
def GetStats(first_name, last_name):
    season_stats = GetSeasonStats(first_name, last_name)
    if  "season_stats" in season_stats:
        opponent_stats = GetNextOpponent(first_name, last_name, season_stats["next_team_abr"])
        response = {**season_stats, **opponent_stats}
    else: 
        response = {"error": season_stats["error"]}
    
    return response
    
    
def GetSeasonStats(first_name, last_name):
    response = requests.get(f'https://www.basketball-reference.com/players/{last_name[0]}/{last_name[:5]}{first_name[:2]}01.html')
    soup = BeautifulSoup(response.content, 'html.parser')
    all_stats = soup.find(class_="p1")
    if all_stats == None:
        return {"error": "Player not found."}
    separate = all_stats.find_all("p")
    if not separate[2].getText():
        return {"error": "Player not in the league."}
    else:
        points_this_season = separate[2].get_text()
        rebounds_this_season = separate[4].get_text()
        assists_this_season = separate[6].get_text()
        picdiv = soup.find(class_="media-item")
        pic = picdiv.find_all("img")
        season_stats = {"pts": points_this_season, "assist": assists_this_season, "reb": rebounds_this_season}
        # LAST 5 GAMES
        nu_row = []
        table = soup.find('table', id="last5")
        rows = table.find_all('tr')
        rows.pop(0)
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            nu_row.append([cols[0],cols[3],cols[4],cols[6],cols[7],cols[8],cols[10],cols[11],cols[18], cols[19], cols[20], cols[21], cols[24]])
        df1 = pd.DataFrame(nu_row, columns=['Date', 'Opp', 'Result', 'MP', 'FG', 'FGA', '3P', '3PA', 'REB', 'AST', 'STL', 'BLK', 'PTS'])
        # NEXT OPP ABR
        footer = soup.find('div', id="tfooter_last5")
        next = footer.find_all("a")
        team = next[0].get_text()
        return {"img": pic[0]["src"], "season_stats": season_stats, "last5": df1, "next_team_abr": team}


def GetNextOpponent(first_name, last_name, team):
    
    team_name = team_abbreviations[team]
    stat_response = requests.get(f'https://www.statmuse.com/nba/ask?q={first_name}+{last_name}+last+5+games+vs+{team_name}')
    soupy = BeautifulSoup(stat_response.content, 'html.parser')
    opp_table = soupy.find("table")
    opp_rows = opp_table.find_all("tr")
    opp_rows.pop(0)
    nu_row = []

    for row in opp_rows:
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        nu_row.append([cols[2],cols[5],cols[6],cols[7],cols[8],cols[9],cols[10],cols[11],cols[13], cols[14], cols[16], cols[17]])
    df2 = pd.DataFrame(nu_row, columns=['Date', 'Opp', 'MP', 'PTS', 'REB', 'AST','STL', 'BLK', 'FG', 'FGA', '3P', '3PA'])
    return {"last5opp": df2, "next_opponent": [team, team_name]}