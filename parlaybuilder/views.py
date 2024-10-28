from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .services import GetStats, GetAllTeams, GetMvpList, GetTeamPlayers, GetNextOpponent, GetTodaysGames

@api_view(['GET', 'POST'])
def index(request):
    if request.method == "GET":
        all_teams = GetAllTeams()
        mvp_list = GetMvpList()
        todays_games = GetTodaysGames()
        return Response({ "mvp_list": mvp_list, "all_teams": all_teams, "todays_games": todays_games})
    else:
        parsed = JSONParser().parse(request)
        splitted_full_name = parsed["player"].split()
        if len(splitted_full_name) < 2:
            return Response({"error": "Player not in the league."})
        first_name = splitted_full_name[0]
        last_name = splitted_full_name[1]
        response = GetStats(first_name, last_name) 
        return Response(response)
@api_view(['GET'])
def get_all_teams(request):
    all_teams = GetAllTeams()
    return Response({"teams": all_teams})

@api_view(['GET'])
def get_team(request, team):
    players = GetTeamPlayers(team)
    return Response({"roster": players["roster"]})

@api_view(['GET'])
def get_mvp_list(request):
    mvp_list = GetMvpList()
    return Response({ "mvp_list": mvp_list})

@api_view(['POST'])
def get_opponent_stats(request):
    parsed = JSONParser().parse(request)
    opponent_stats = GetNextOpponent(parsed["first"], parsed["last"], parsed["team"])
    return Response({"opp_stats": opponent_stats})



