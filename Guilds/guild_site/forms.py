from django import forms
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from guild_site.models import SiteUser, Post, Reply, Category, AuthCode


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['body']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'body']


class DeleteForm(forms.Form):
    confirmation = forms.BooleanField(label='ДА, Я ВСЁ ПОДТВЕРЖДАЮ!')


class ConfirmRegistrationForm(forms.Form):
    code = forms.IntegerField(max_value=99_999, min_value=10_000)

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super(ConfirmRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        attempted_code = cleaned_data['code']
        print(f'{self.user_id}||||{attempted_code}|||||{timezone.now()}')
        if not AuthCode.objects.filter(user_id=self.user_id,
                                       code=attempted_code,
                                       expires__gte=timezone.now()).exists():
            raise ValidationError("Неверный код!")

        return cleaned_data


class CustomSignupForm(SignupForm):
    display_username = forms.CharField(max_length=100, label="Имя пользователя, отображаемое на сайте", required=True)
    potential_username = ''

    def clean(self):

        cleaned_data = super().clean()
        self.potential_username = cleaned_data['display_username']

        # checking for username uniqueness
        if SiteUser.objects.filter(username=self.potential_username).exists():
            raise ValidationError('Пользователь с таким ником уже существует.')

        return cleaned_data


class ManageSubscriptionsForm(forms.ModelForm):
    class Meta:
        model = SiteUser
        fields = ['subscription']

