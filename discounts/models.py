# discounts/models.py
from django.db import models
from django.utils.text import slugify
from goods.models import Category


class Discounts(models.Model):
    """Модель акций"""
    DISCOUNT_TYPES = [
        ('bundle', 'Набор/комплект'),
        ('special', 'Специальное предложение'),
    ]
    
    name = models.CharField(
        'Название акции',
        max_length=200
    )
    slug = models.SlugField(
        'URL-идентификатор',
        max_length=200,
        unique=True,
        blank=True
    )
    description = models.TextField(
        'Описание акции',
        blank=True
    )
    
    # Тип акции
    discount_type = models.CharField(
        'Тип акции',
        max_length=20,
        choices=DISCOUNT_TYPES,
        default='special'
    )
    
    # Изображение акции
    image = models.ImageField(
        'Изображение',
        upload_to='discounts/',
        blank=True,
        null=True
    )
    
    # Связь с категорией (необязательно)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='discounts',
        verbose_name='Категория',
        null=True,
        blank=True
    )
    
    # Статус - только is_active, без дат
    is_active = models.BooleanField(
        'Акция активна',
        default=True
    )
    
    # Время создания
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_discount_type_display(self):
        if self.discount_type == 'special':
            return 'Специальное предложение'
        return 'Набор/комплект'