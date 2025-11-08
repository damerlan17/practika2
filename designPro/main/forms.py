from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import User,Request

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)
    consent = forms.BooleanField(label="Согласие на обработку персональных данных", required=True)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email']
        labels = {
            'full_name': 'ФИО',
            'username': 'Логин',
            'email': 'Email',
        }

    def clean_full_name(self):
        name = self.cleaned_data['full_name']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', name):
            raise ValidationError("ФИО должно содержать только кириллицу, пробелы и дефисы.")
        return name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise ValidationError("Логин должен содержать только латиницу и дефис.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        # Django автоматически валидирует формат email при сохранении
        # Но можно добавить свою валидацию, если нужно
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return p2

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
class CreateRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CreateRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Проверка размера (2MB = 2 * 1024 * 1024 байт)
            max_size_mb = 2
            if image.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f'Размер файла не должен превышать {max_size_mb} МБ.')
            # Проверка расширения файла (jpg, jpeg, png, bmp)
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            ext = image.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise ValidationError('Формат файла не поддерживается. Разрешены: jpg, jpeg, png, bmp.')
        return image