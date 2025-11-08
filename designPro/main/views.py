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
        form = UserLoginForm(request, data=request.POST) # <-- Использует стандартную аутентификацию Django
        if form.is_valid():
            user = form.get_user() # <-- form.get_user() возвращает пользователя или None
            if user: # <-- Проверка, что пользователь существует и пароль верен
                login(request, user)
                if user.is_superuser:
                    return redirect('superadmin')
                else:
                    return redirect('profile')
            else:
                # <-- Сюда попадаем, если логин/пароль неверны
                messages.error(request, 'Неверный логин или пароль.')
        else:
            # <-- Сюда попадаем, если форма не прошла валидацию (например, пустые поля)
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
            # form.errors содержит ошибки, шаблон их отобразит
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')


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

    return render(request, 'main/profile.html', {
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

@admin_required
def superadmin_panel(request):
    # Получаем все заявки
    requests = Request.objects.all().order_by('-created_at')

    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)

    # Категории
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
        category.delete()  # Удаляет и связанные заявки благодаря CASCADE
        messages.success(request, 'Категория и связанные заявки удалены.')
        return redirect('superadmin')

    # Обработка смены статуса заявки
    if 'request_id' in request.POST and 'status_new' in request.POST:
        req_id = request.POST.get('request_id')
        new_status = request.POST.get('status_new')
        comment = request.POST.get('admin_comment', '').strip()
        # --- Вот здесь получаем файл --->
        design_image = request.FILES.get('design_image')  # <-- name="design_image" из формы
        # <--- Вот здесь

        print("DEBUG: request.FILES =", request.FILES)
        print("DEBUG: design_image =", design_image)

        req = get_object_or_404(Request, id=req_id)

        # Проверяем, что статус можно изменить (только из 'new')
        if req.status != 'new':
            messages.error(request, f'Невозможно изменить статус заявки #{req.id}, так как она уже не "Новая".')
            return redirect('superadmin')

        # Проверки на основе нового статуса
        if new_status == 'in_progress':
            if not comment:
                messages.error(request, f'Для заявки #{req.id} статус "Принято в работу" требует комментарий.')
                return redirect('superadmin')
            req.admin_comment = comment
        elif new_status == 'done':
            # --- Вот здесь проверяется файл --->
            if not design_image:  # <-- Если файл не передан
                messages.error(request, f'Для заявки #{req.id} статус "Выполнено" требует изображение дизайна.')
                return redirect('superadmin')
            req.design_image = design_image  # <-- Присваиваем файл модели
            # <--- Вот здесь
        else:
            # Недопустимый статус (на всякий случай)
            messages.error(request, f'Недопустимый статус: {new_status}')
            return redirect('superadmin')

        req.status = new_status
        req.save()
        messages.success(request,
                         f'Статус заявки #{req.id} изменён на "{dict(Request.STATUS_CHOICES).get(new_status)}".')
        return redirect('superadmin')

    is_filter_new = status_filter == 'new'
    is_filter_in_progress = status_filter == 'in_progress'
    is_filter_done = status_filter == 'done'

    return render(request, 'main/superadmin.html', {
        'requests': requests,
        'categories': categories,
        'status_filter': status_filter,
        'is_filter_new': is_filter_new,
        'is_filter_in_progress': is_filter_in_progress,
        'is_filter_done': is_filter_done,
    })

@user_required
def delete_request(request, request_id):
    # Получаем заявку или 404
    req = get_object_or_404(Request, id=request_id)

    # Проверяем, что заявка принадлежит текущему пользователю
    if req.user != request.user:
        # Если заявка не его - ошибка доступа
        raise PermissionDenied

    # Проверяем статус: можно удалять только 'new'
    if req.status != 'new':
        messages.error(request, f'Невозможно удалить заявку "{req.title}", так как её статус уже изменён.')
        return redirect('profile')

    # Если всё в порядке - удаляем
    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('profile')

    return redirect('profile')

from .forms import UserRegistrationForm, UserLoginForm, CreateRequestForm

@user_required
def user_profile(request):
    # --- Форма создания заявки ---
    form = None
    if request.method == 'POST':
        form = CreateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user  # Привязываем к текущему пользователю
            req.save()
            messages.success(request, 'Заявка успешно создана.')
            return redirect('profile')
        else:
            # Если форма не валидна, она останется с ошибками и передастся в шаблон
            pass
    else:
        # При GET-запросе создаём пустую форму
        form = CreateRequestForm()

    # Получаем заявки пользователя
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')

    # Фильтрация по статусу (если передан параметр status)
    status_filter = request.GET.get('status')
    if status_filter:
        user_requests = user_requests.filter(status=status_filter)

    # Пагинация (опционально)
    paginator = Paginator(user_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаём и форму, и заявки в шаблон
    return render(request, 'main/profile.html', {
        'form': form,  # <-- Вот она
        'page_obj': page_obj,
        'status_filter': status_filter
    })