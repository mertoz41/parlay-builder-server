from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get_team/<str:team>/", views.get_team, name="get_team"),
    path("get_opponent_stats/", views.get_opponent_stats, name="get_opponent_stats"),
    path("get_all_teams", views.get_all_teams, name="get_all_teams"),
    path("get_mvp_list", views.get_mvp_list, name="get_mvp_list")
]