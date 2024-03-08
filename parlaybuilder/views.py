from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.parsers import JSONParser
from .services import GetSeasonStats, GetNextOpponent

@api_view(['GET', 'POST'])
def index(request):
    parsed = JSONParser().parse(request)
    splitted_full_name = parsed["player"].split()
    first_name = splitted_full_name[0]
    last_name = splitted_full_name[1]
    stats = GetSeasonStats(first_name, last_name) 
    opp5 = GetNextOpponent(first_name, last_name, "PHO")
    return Response({"last5": stats["last5"], "season_stats": stats["stats"], "img": stats["pic"], "last5opp": opp5["opp"], "next_opponent": [stats["next_team_abr"], opp5["team_name"]]})
