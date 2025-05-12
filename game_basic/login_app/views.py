from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.views.generic import CreateView, FormView, UpdateView,ListView,DetailView
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, UsernameResetForm, ProfileForm
from .models import Profile,Rank

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

from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Rank
from .forms  import ProfileForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model         = Profile
    form_class    = ProfileForm
    template_name = 'login_app/profile_form.html'
    success_url   = reverse_lazy('login_app:profile_form')
    context_object_name = 'profile'

    # --- ① 編集対象取得（既存がなければ None で「作成モード」へ） ---
    def get_object(self, queryset=None):
        return Profile.objects.filter(user=self.request.user).first()

    # --- ② テンプレート用フラグ ---
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_user'] = self.request.user
        ctx['is_new_profile'] = (self.object is None)
        return ctx

    # --- ③ 保存ロジック ---
    def form_valid(self, form):
        # 既存 or 新規インスタンスを確保
        profile = self.object or Profile(user=self.request.user)

        # フォームの値を一括反映
        for field in ('level', 'win_count', 'loss_count', 'favorite_mon'):
            setattr(profile, field, form.cleaned_data[field])

        # レベル → Rank 自動割り当て
        level = profile.level
        profile.rank = Rank.objects.get(min_level__lte=level,
                                        max_level__gte=level)

        # 保存
        profile.save()
        self.object = profile   # UpdateView が後続で使うのでセット

        return super().form_valid(form)
#ランキング一覧（レベル）
class LevelRankingView(ListView):
    model=Profile
    template_name='login_app/level_ranking.html'
    context_object_name="profiles"
    ordering=['-level']
    paginate_by= 20
    def get_queryset(self):
        return super().get_queryset().select_related('user')

class WinRankingView(ListView):
    model=Profile
    template_name='login_app/win_ranking.html'
    context_object_name="profiles"
    ordering=['-win_count']
    paginate_by= 20
    def get_queryset(self):
        return super().get_queryset().select_related('user')

class UserdetailView(DetailView):
    model=Profile
    template_name="login_app/user_detail.html"
    context_object_name="profile"
