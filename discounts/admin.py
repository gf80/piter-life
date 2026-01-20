# discounts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Discounts


@admin.register(Discounts)
class DiscountsAdmin(admin.ModelAdmin):
    # Поля в списке
    list_display = ['name', 'slug', 'discount_type', 'category', 'is_active', 'created_at', 'image_preview']
    list_filter = ['discount_type', 'is_active', 'category']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'slug', 'image_preview_big']
    
    # Группировка полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'discount_type')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview_big')
        }),
        ('Категория', {
            'fields': ('category',)
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Миниатюра в списке"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'Изображение'
    
    def image_preview_big(self, obj):
        """Большое изображение в форме"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 300px; border-radius: 10px; margin: 10px 0;" />',
                obj.image.url
            )
        return "Изображение не загружено"
    image_preview_big.short_description = 'Предпросмотр'