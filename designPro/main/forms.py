from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    consent = forms.BooleanField(label='Согласие на обработку ПД', required=False)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email']

    def clean_full_name (self):
        name = self.cleaned_data['full_name']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', name):
            raise ValidationError('ФИО должно содержать только русские буквы, робелы и дефисы')
        return name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-z\-]+$', username):
            raise ValidationError('Логин должен содержать только английские буквы и дефис')
        return username

    def clean_password2 (self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Пороли не совпадают')
        return p2

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
