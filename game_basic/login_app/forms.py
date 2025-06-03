# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from .models import Profile

#新規登録
class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ラベル
        self.fields['username'].label    = 'ユーザー名'
        self.fields['password1'].label   = 'パスワード'
        self.fields['password2'].label   = 'パスワード（確認）'

        # ヘルプテキスト
        self.fields['username'].help_text  = '必須。10文字以内。英数字と @ / . / + / - / _ のみ。'
        self.fields['password1'].help_text = (
            '英大文字・小文字・数字・記号を含む8文字以上のパスワードを設定してください。'
        )
        self.fields['password2'].help_text = '確認のためもう一度同じパスワードを入力してください。'

        self.fields['password1'].widget.attrs.update({'id': 'password1'})
        self.fields['password2'].widget.attrs.update({'id': 'password2'})



#パスワード忘れた時
User = get_user_model()

class UsernameResetForm(forms.Form):
    """
    ユーザー名だけを入力させるフォーム
    """
    username = forms.CharField(
        label="ユーザー名",
        max_length=User._meta.get_field('username').max_length,
    )

   

    def clean_username(self):
        uname = self.cleaned_data['username']
        if not User.objects.filter(username__iexact=uname, is_active=True).exists():
            raise forms.ValidationError("指定のユーザー名は存在しません。")
        return uname



#マイページ画面
class ProfileForm(forms.ModelForm):
	class Meta:
		model=Profile
		fields=("favorite_mon",)