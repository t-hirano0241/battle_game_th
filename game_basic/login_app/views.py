from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.views.generic import CreateView, FormView, UpdateView,ListView,TemplateView
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
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile,TimeAttackRecord
from .forms import ProfileForm
from django.shortcuts import redirect


#新規登録
User = get_user_model()

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login_app:top_wrap')

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
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
class TopView(LoginRequiredMixin, TemplateView):
    template_name = 'login_app/top_wrap.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model               = Profile
    form_class          = ProfileForm               # ← これが必須
    template_name       = 'login_app/profile_form.html'
    success_url         = reverse_lazy('login_app:profile_form')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # 存在すれば取得、なければ作成
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        # created=True のときが「本当の新規作成モード」
        self.is_new_profile = created
        return profile

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # サインアップ時に自動作成された "空" プロフィールも新規扱いにする
        if not getattr(self, 'is_new_profile', False):
            profile = self.object
            if profile.favorite_mon is None and profile.best_record is None:
                ctx['is_new_profile'] = True
            else:
                ctx['is_new_profile'] = False
        else:
            ctx['is_new_profile'] = True

        return ctx

    def form_valid(self, form):
        # フォームからデータを受け取って保存
        profile = form.save(commit=False)

        # もしランク自動計算が必要ならここで
        # level = profile.level
        # profile.rank = Rank.objects.get(min_level__lte=level, max_level__gte=level)

        profile.save()
        return redirect(self.get_success_url())
# #ランキング一覧（レベル）
# class LevelRankingView(ListView):
#     model=Profile
#     template_name='login_app/level_ranking.html'
#     context_object_name="profiles"
#     ordering=['-level']
#     paginate_by= 20
#     def get_queryset(self):
#         return super().get_queryset().select_related('user')

# class WinRankingView(ListView):
#     model=Profile
#     template_name='login_app/win_ranking.html'
#     context_object_name="profiles"
#     ordering=['-win_count']
#     paginate_by= 20
#     def get_queryset(self):
#         return super().get_queryset().select_related('user')

class TimeAttackRankingView(LoginRequiredMixin, ListView):
    model = TimeAttackRecord
    template_name = 'login_app/time_attack_ranking.html'
    context_object_name = 'times'
    paginate_by = 20

    def get_queryset(self):
        # タイムが速い順に並べ、ユーザーも一緒に取得
        return (
            TimeAttackRecord.objects
            .select_related('user')
            .order_by('elapsed_time', 'cleared_at')
        )
