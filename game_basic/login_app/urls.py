from django.urls import path
from .views import ProfileUpdateView,SignUpView,TopView,TimeAttackRankingView


app_name='login_app'
urlpatterns=[
    path('top_wrap/',TopView.as_view(),name="top_wrap"),
    path('profile_form/',ProfileUpdateView.as_view(),name="profile_form"),
     path('signup_create/',SignUpView.as_view(),name="signup_create"),
     path('time_attack_ranking/',TimeAttackRankingView.as_view(),name="time_attack_ranking"),

]
