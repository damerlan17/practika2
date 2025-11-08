from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm, UserLoginForm, CreateRequestForm
from .models import Request, Category
from .decorators import user_required, admin_required


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
                return redirect('superadmin')  # или '/superadmin/'
            else:
                return redirect('profile')     # <-- Вот сюда должен попасть обычный пользователь
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


@user_required
def user_profile(request):
    # получаем заявы текущего пользоваткля
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')

    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        user_requests = user_requests.filter(status=status_filter)

    # аггинация
    paginator = Paginator(user_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/user_profile.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })


@admin_required
def superadmin_panel(request):
    # олучаем все заявки
    requests = Request.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)

    categories = Category.objects.all()

    # Обработка добавления категории
    if request.method == 'POST' and 'add_category' in request.POST:
        cat_name = request.POST.get('category_name')
        if cat_name:
            Category.objects.create(name=cat_name)
            messages.success(request, 'Категория добавлена.')
        return redirect('superadmin')

    # Обработка удаления категории
    if 'delete_category' in request.POST:
        cat_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=cat_id)
        category.delete()
        messages.success(request, 'Категория и связанные заявки удалены.')
        return redirect('superadmin')

    return render(request, 'main/superadmin.html', {
        'requests': requests,
        'categories': categories,
        'status_filter': status_filter
    })


def user_logout(request):
    logout(request)
    return redirect('home')
