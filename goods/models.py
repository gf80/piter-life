from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """Модель категорий товаров"""
    name = models.CharField(
        'Название категории', 
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        'URL-идентификатор',
        max_length=200,
        unique=True,
        blank=True
    )
    image = models.ImageField(
        'Изображение товара',
        upload_to='category/images',
        null=True,
        blank=True
    )
    description = models.TextField(
        'Описание категории',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class SubCategory(models.Model):
    """Модель подкатегорий товаров"""
    name = models.CharField(
        'Название подкатегории',
        max_length=200
    )
    slug = models.SlugField(
        'URL-идентификатор',
        max_length=200,
        unique=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Категория'
    )
    
    description = models.TextField(
        'Описание подкатегории',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['name']
        unique_together = ['name', 'category']  # уникальная пара имя+категория
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}", allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('subcategory_detail', kwargs={'slug': self.slug})


class Goods(models.Model):
    """Модель товаров"""
    name = models.CharField(
        'Название товара',
        max_length=200
    )
    slug = models.SlugField(
        'URL-идентификатор',
        max_length=200,
        unique=True,
        blank=True
    )
    describe = models.TextField(
        'Описание товара',
        blank=True,
        null=True
    )
    
    # Связи с категориями
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Категория'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        related_name='goods',
        verbose_name='Подкатегория',
        null=True,
        blank=True
    )
    
    # Цены
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    old_price = models.DecimalField(
        'Старая цена',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Изображение
    image = models.ImageField(
        'Изображение товара',
        upload_to='goods/images',
        null=True,
        blank=True
    )
    
    # Дополнительные поля
    is_available = models.BooleanField(
        'Доступен',
        default=True
    )
    is_featured = models.BooleanField(
        'Рекомендуемый',
        default=False
    )
    is_new = models.BooleanField(
        'Новинка',
        default=False
    )
    weight = models.DecimalField(
        'Вес (гр)',
        max_digits=6,
        decimal_places=0,
        null=True,
        blank=True
    )
    calories = models.PositiveIntegerField(
        'Калории',
        null=True,
        blank=True
    )
    
    # Время
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'subcategory']),
            models.Index(fields=['price']),
            models.Index(fields=['is_available', 'is_featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('goods_detail', kwargs={'slug': self.slug})
    
    @property
    def has_discount(self):
        """Есть ли скидка на товар"""
        return self.old_price is not None and self.old_price > self.price
    
    @property
    def discount_percent(self):
        """Процент скидки"""
        if self.has_discount:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0
    
    @property
    def thumbnail_url(self):
        """URL миниатюры изображения"""
        if self.image:
            return self.image.url
        return '/static/images/default-goods.jpg'

