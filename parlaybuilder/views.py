from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.parsers import JSONParser
from .services import GetStats, GetNextOpponent

@api_view(['GET', 'POST'])
def index(request):
    parsed = JSONParser().parse(request)
    splitted_full_name = parsed["player"].split()
    if len(splitted_full_name) < 2:
        return Response({"error": "Player not in the league."})
    first_name = splitted_full_name[0]
    last_name = splitted_full_name[1]
    response = GetStats(first_name, last_name) 
    return Response(response)
