# from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from bs4 import BeautifulSoup
import pandas as pd
import requests
from rest_framework.parsers import JSONParser


@api_view(['GET', 'POST'])
def index(request):
    parsed = JSONParser().parse(request)
    splitted_full_name = parsed["player"].split()
    first_name = splitted_full_name[0]
    last_name = splitted_full_name[1]
    response = requests.get(f'https://www.basketball-reference.com/players/{last_name[0]}/{last_name[:5]}{first_name[:2]}01.html')
    soup = BeautifulSoup(response.content, 'html.parser')

    # SEASON STATS
    all_stats = soup.find(class_="p1")
    separate = all_stats.find_all("p")
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


    # LAST 5 VS NEXT OPPONENT

    footer = soup.find('div', id="tfooter_last5")
    next = footer.find_all("a")
    team = next[0].get_text()
    team_abbreviations = {
        "ATL": "hawks",
        "BOS": "celtics",
        "BRK": "nets",
        "CHA": "hornets",
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
        "PHX": "suns",
        "POR": "blazers",
        "SA": "spurs",
        "SAC": "kings",
        "TOR": "raptors",
        "UTH": "jazz",
        "WSH": "wizards"
    }
    team_name = team_abbreviations[f'{team}']
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
    return Response({"last5": df1, "season_stats": season_stats, "img": pic[0]["src"], "last5opp":df2})


def csrf(request):
    return JsonResponse({'csrfToken' : get_token(request)})