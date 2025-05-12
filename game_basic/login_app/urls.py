from django.urls import path
from .views import ProfileUpdateView,SignUpView,LevelRankingView,WinRankingView,UserdetailView


app_name='login_app'
urlpatterns=[
    path('profile_form/',ProfileUpdateView.as_view(),name="profile_form"),
     path('signup_create/',SignUpView.as_view(),name="signup_create"),
     path('ranking_level/',LevelRankingView.as_view(),name="ranking_level"),
     path('ranking_win/',WinRankingView.as_view(),name='ranking_win'),
     path('user_detail/<int:pk>/',UserdetailView.as_view(),name="user_detail"),
]
