# main/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from .models import Request  # Добавлен импорт модели Request

def home(request):
    # Выбираем до 4 последних выполненных заявок
    completed_requests = Request.objects.filter(status='done').order_by('-created_at')[:4]
    # Считаем количество заявок в статусе "Принято в работу"
    in_progress_count = Request.objects.filter(status='in_progress').count()

    return render(request, 'main/home.html', {
        'completed_requests': completed_requests,
        'in_progress_count': in_progress_count
    })

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('/superadmin/')
            else:
                return redirect('/profile/')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = UserLoginForm()
    return render(request, 'main/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Регистрация прошла успешно. Вы можете войти.')
            return redirect('login')
        else:
            # Если форма не прошла валидацию, снова отображаем её с ошибками
            pass  # form уже содержит ошибки, просто передаём её в шаблон
    else:
        form = UserRegistrationForm()

    return render(request, 'main/register.html', {'form': form})