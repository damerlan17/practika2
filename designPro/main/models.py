from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(verbose_name='ФИО', max_length=255)
    email = models.EmailField(unique=True)
    consent = models.BooleanField("Согласие на отработку ПД", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'consent']


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
