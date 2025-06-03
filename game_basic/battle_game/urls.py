"""
URL configuration for battle_game project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from login_app.views import UsernameResetView, CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_app/', include(('login_app.urls','login_app'),namespace='login_app')),
    
     path(
        'accounts/password_reset/',
        UsernameResetView.as_view(),
        name='password_reset'
    ),

    # ② パスワード再設定画面（トークン確認＆新パスワード入力）
    path(
        'accounts/reset/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    # ③ 再設定完了ページ（標準の完了テンプレートを上書き可）
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
   
    path('accounts/', include('django.contrib.auth.urls')),
    path("battle_app/",include(("battle_app.urls","battle_app"),namespace="battle_app")),
   
]
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
