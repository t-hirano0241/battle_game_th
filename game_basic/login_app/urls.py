from django.urls import path
from .views import ProfileUpdateView,SignUpView


app_name='login_app'
urlpatterns=[
    path('profile_form/',ProfileUpdateView.as_view(),name="profile_form"),
     path('signup_create/',SignUpView.as_view(),name="signup_create"),
]
