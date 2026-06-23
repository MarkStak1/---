from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тип события")
    slug = models.SlugField(unique=True, verbose_name="Код типа")

    class Meta:
        verbose_name = 'Тип события'
        verbose_name_plural = 'Типы событий'

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=300, verbose_name="Место проведения")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    preview = models.ImageField(
        upload_to='events/previews/',
        blank=True,
        null=True,
        verbose_name='Фото-превью',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def preview_fallback_slug(self):
        return self.category.slug if self.category_id else 'default'

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Оплачено'
    )

    class Meta:
        unique_together = ('user', 'event')

    @property
    def is_paid(self):
        return self.amount_paid > 0