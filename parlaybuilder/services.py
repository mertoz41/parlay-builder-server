import requests
from bs4 import BeautifulSoup
import pandas as pd

def GetStats(first_name, last_name):
    season_stats = GetSeasonStats(first_name, last_name)
    last_five_stats = StatMuseData(f"https://www.statmuse.com/nba/ask/{first_name}-{last_name}-stats-last-5-games")
    season_stats["last5"] = last_five_stats
    return season_stats

def GetAllTeams():
    response = requests.get("https://www.nba.com/teams")
    soup = BeautifulSoup(response.content,  'html.parser')
    teams = soup.find_all("div", {"class": "TeamFigure_tf__jA5HW"})
    cleaned_teams = []
    for team in teams:
        new_team = {"name": team.find(['a']).text.strip(), "img": team.find(['img'])["src"]}
        cleaned_teams.append(new_team)
    return cleaned_teams

def GetMvpList():
    dfs = pd.read_html('https://www.basketball-reference.com/friv/mvp.html')
    df = dfs[0][0:5]
    df = df[["Rk", "Player", "Team","W", "L", "FG", "FGA", "3P", "3PA", "TRB", "AST", "STL", "BLK", "PTS"]]
    df.rename(columns={'FG': "FGM", "3P": "3PM", "Rk": "Rank", "TRB": "REB"}, inplace=True)
    return df


def GetTodaysGames():
    response = requests.get('https://www.foxsports.com/nba/schedule')
    soup = BeautifulSoup(response.content, 'html.parser')
    target_divs = soup.find_all('div', class_="table-segment")
    todays_games = target_divs[0]
    rows = todays_games.find_all("tr")
    rows.pop(0)
    nu_row = []
    for row in rows: 
        cols = row.find_all(['td', 'th'])
        imgs = [ele.img for ele in cols]
        cols = [ele.text.strip() for ele in cols]
        nu_row.append([cols[0], imgs[0]['src'], cols[2], imgs[2]['src'], cols[3]])

    return nu_row

    
    
def GetSeasonStats(first_name, last_name):
    # some players index number is different due to previous players
    index = ""
    full_name = first_name + " " + last_name
    if full_name == "jaylen brown" or full_name == "anthony davis" or full_name == "tobias harris" or full_name == "keegan murray":
        index = "2"
    elif full_name == 'jalen williams':
        index = "6"
    else:
        index = "1"
    
    response = requests.get(f'https://www.basketball-reference.com/players/{last_name[0]}/{last_name[:5]}{first_name[:2]}0{index}.html')
    soup = BeautifulSoup(response.content, 'html.parser')
    all_stats = soup.find(class_="p1")
    if all_stats == None:
        return {"error": "Player not found."}
    separate = all_stats.find_all("p")
    if not separate[3].getText():
        return {"error": "Player not in the league."}
    else:
        points_this_season = separate[3].get_text()
        rebounds_this_season = separate[5].get_text()
        assists_this_season = separate[7].get_text()
        picdiv = soup.find(class_="media-item")
        pic = picdiv.find_all("img")
        season_stats = {"pts": points_this_season, "assist": assists_this_season, "reb": rebounds_this_season}
        return {"img": pic[0]["src"], "season_stats": season_stats}

def GetTeamPlayers(team):
    
    fixed_teams = {"BKN": "BRK", "CHA": "CHO", "PHX": "PHO"}
    searched_team =''
    if team in fixed_teams: 
        searched_team = fixed_teams[team]
    else :
        searched_team = team

    dfs = pd.read_html(f'https://www.basketball-reference.com/teams/{searched_team}/2025.html')
    df = dfs[1][0:9]
    df = df[["Player", "FG", "FGA", "3P", "3PA", "TRB", "AST", "STL", "BLK", "PTS"]]
    df.rename(columns={'FG': "FGM", "3P": "3PM", "TRB": "REB"}, inplace=True)
    return {"roster": df}

def GetNextOpponent(first_name, last_name, team):
    stats = StatMuseData(f'https://www.statmuse.com/nba/ask?q={first_name}+{last_name}+last+5+games+vs+{team}')
    return stats

def StatMuseData(url):
    dfs = pd.read_html(url)
    df = dfs[0][0:5]
    df = df.drop(df.columns[[0,1,5]], axis=1)
    df = df[["DATE", "OPP", "MIN", "FGM", "FGA", "3PM", "3PA", "STL", "BLK", "AST", "PTS", "REB"]]
    df.rename(columns={'DATE': "Date"}, inplace=True)
    types = {}
    for col in df.columns:
        print(col)
        if df[col].dtype == "float64":
            types[col] = "int"
        else:
            types[col] = df[col].dtype

    df = df.astype(types)
    return df