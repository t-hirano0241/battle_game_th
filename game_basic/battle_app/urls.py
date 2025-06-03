from django.urls import path
from . import views
from .views import campaign_play,campaign_recruit,campaign_clear,campaign_recruit_submit,campaign_game_over,campaign_action

app_name="battle_app"

urlpatterns=[
    path('battle_start/',campaign_play,name="battle_start"),
    path('battle_action/',campaign_action,name="battle_action"),
    path('battle_recruit/',campaign_recruit,name="battle_recruit"),
    path('battle_clear/',campaign_clear,name="battle_clear"),
    path('battle_recruit_submit/',campaign_recruit_submit,name="battle_recruit_submit"),
    path('battle_game_over/',campaign_game_over,name="battle_game_over"),

]