from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Валидатор для логина
username_validator = RegexValidator(
    regex=r'^[a-zA-Z\-]+$',
    message='Логин должен содержать только латиницу и дефис.',
    code='invalid_username'
)

class User(AbstractUser):
    full_name = models.CharField(verbose_name='ФИО', max_length=255)
    email = models.EmailField(unique=True)
    consent = models.BooleanField("Согласие на обработку ПД", default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'consent']

    # Переопределяем поле username, чтобы убрать стандартный help_text
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        help_text='',  # Убираем стандартный текст
        validators=[username_validator],
        error_messages={
            "unique": "Пользователь с таким логином уже существует.",
        }
    )


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self): # определяет то как будет отобажатся обект?
        return self.name #удет отображатся по имени

class Request(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('done', 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField('Фото помещения', upload_to= 'requests/')
    status = models.CharField('', max_length=30, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_comment = models.TextField('Комментарий админа', blank=True, null=True)
    design_image = models.ImageField('Дизайн', upload_to='designs/', blank=True, null=True)

    def __str__(self):
        return self.title
