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
        "NOP": "pelicans",
        "NY": "knicks",
        "ORL": "magic",
        "OKC": "thunder",
        "PHI": "sixers",
        "PHO": "suns",
        "POR": "blazers",
        "SAS": "spurs",
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

def GetMvpList():
    rows = GetTable('https://www.basketball-reference.com/friv/mvp.html', "players")
    top5 = rows[:5]
    new_rows = []
    for row in top5:
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        new_rows.append([cols[0], cols[1], cols[2], cols[3], cols[4], cols[9], cols[10], cols[12], cols[13], cols[24], cols[25], cols[26], cols[27], cols[30]])
    df1 = pd.DataFrame(new_rows, columns=['Rank', 'Player', 'Team', 'W', 'L', 'FG', 'FGA', '3P', '3PA', 'REB', 'AST', 'STL', 'BLK', 'PTS'])
    return df1


def GetTable(url, table_id):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id=table_id)
    rows = table.find_all("tr")
    rows.pop(0)
    return rows


def GetTodaysGames():
    rows = GetTable('https://www.foxsports.com/nba/schedule', "table-0")
    nu_row = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        imgs = [ele.img for ele in cols]
        cols = [ele.text.strip() for ele in cols]
        nu_row.append([cols[0], imgs[0]['src'], cols[2], imgs[2]['src']])
    return nu_row
    
    
def GetSeasonStats(first_name, last_name):
    # 02 for jaylen brown, anthony davis
    index = ""
    full_name = first_name + " " + last_name
    if full_name == "jaylen brown":
        index = "2"
    elif full_name == "anthony davis":
        index = "2"
    else:
        index = "1"
        
    response = requests.get(f'https://www.basketball-reference.com/players/{last_name[0]}/{last_name[:5]}{first_name[:2]}0{index}.html')
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

def GetTeamPlayers(team):
    # phx to pho
    team_name = ''
    if team == "PHX":
        team_name = "PHO"
    elif team == "BKN":
        team_name = "BRK"
    elif team == "CHA":
        team_name = "CHO"
    else:
        team_name = team

    # bkn to brk
    # cha to CHO
    rows = GetTable(f'https://www.basketball-reference.com/teams/{team_name}/2024.html', "per_game")
    top8 = rows[:9]
    new_rows = []
    for row in top8:
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        new_rows.append([cols[1], cols[6], cols[7], cols[9], cols[10], cols[21], cols[22], cols[23], cols[24], cols[27]])
    df1 = pd.DataFrame(new_rows, columns=['Player','FG', 'FGA', '3P', '3PA', 'REB', 'AST', 'STL', 'BLK', 'PTS'])
    return {"roster": df1, "team_name": team_abbreviations[team_name]}

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
    nu_row.reverse()
    df2 = pd.DataFrame(nu_row, columns=['Date', 'Opp', 'MP', 'PTS', 'REB', 'AST','STL', 'BLK', 'FG', 'FGA', '3P', '3PA'])
    return {"last5opp": df2, "next_opponent": [team, team_name]}