from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.views.generic import CreateView, FormView, UpdateView
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, UsernameResetForm, ProfileForm
from .models import Profile

#新規登録
User = get_user_model()

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login_app:profile_form')

    def form_valid(self, form):
        user = form.save()
        from django.contrib.auth import login
        login(self.request, user)
        return super().form_valid(form)

#パスワード忘れた時
class UsernameResetView(FormView):
    template_name = 'registration/password_reset_form.html'
    form_class = UsernameResetForm

    def form_valid(self, form):
        # ユーザー名でユーザーを取得し、トークン生成 → リダイレクト
        user = User.objects.get(
            username__iexact=form.cleaned_data['username'],
            is_active=True
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        return HttpResponseRedirect(url)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class    = SetPasswordForm
    success_url   = reverse_lazy('login')

#トップ画面
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from .forms import ProfileForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model               = Profile
    form_class          = ProfileForm
    template_name       = 'login_app/profile_form.html'
    success_url         = reverse_lazy('login_app:profile_form')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """
        GET リクエストでは Profile を作らず、既存があれば返すだけ。
        まだなければ None を返して「新規モード」にする。
        """
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # プロフィールが存在しないなら新規モード(True)、あるなら編集モード(False)
        ctx['is_new_profile'] = (ctx.get('profile') is None)
        return ctx

    def form_valid(self, form):
        """
        POST 時に初めてレコードを作成 or 取得し、
        form.instance にセットしてから保存。
        """
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        form.instance = profile
        return super().form_valid(form)
