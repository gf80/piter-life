from django.contrib import admin
from .admin_site import CustomAdminSite
from goods.models import Goods, Category, SubCategory
from orders.models import Order, OrderItem
from discounts.models import Discounts
from django.utils.html import format_html

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin


custom_admin_site = CustomAdminSite(name="custom_admin")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'goods_count', 'created_at', 'image_preview']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def goods_count(self, obj):
        return obj.goods.count()
    goods_count.short_description = 'Кол-во товаров'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Предпросмотр'


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'goods_count']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def goods_count(self, obj):
        return obj.goods.count()
    goods_count.short_description = 'Кол-во товаров'


class GoodsAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'subcategory', 'price', 'old_price',
        'discount_percent_display', 'is_available', 'is_featured', 'image_preview'
    ]
    list_filter = ['category', 'subcategory', 'is_available', 'is_featured', 'is_new', 'created_at']
    search_fields = ['name', 'describe']
    list_editable = ['price', 'old_price', 'is_available', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'describe', 'image', 'image_preview')
        }),
        ('Категории', {
            'fields': ('category', 'subcategory')
        }),
        ('Цены', {
            'fields': ('price', 'old_price')
        }),
        ('Характеристики', {
            'fields': ('weight', 'calories')
        }),
        ('Статусы', {
            'fields': ('is_available', 'is_featured', 'is_new')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Предпросмотр'

    def discount_percent_display(self, obj):
        if obj.has_discount:
            return f"{obj.discount_percent}%"
        return "-"
    discount_percent_display.short_description = 'Скидка'


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

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'total_price')
    fields = ('product', 'quantity', 'price', 'total_price')

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = "Сумма"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'phone_number',
        'delivery_type',
        'total_quantity',
        'total_price',
        'is_done',
        'created_at',
    )
    list_filter = ('delivery_type', 'is_done', 'created_at')
    search_fields = ('phone_number',)
    list_editable = ('is_done',)
    readonly_fields = (
        'created_at',
        'total_quantity',
        'total_price',
    )

    inlines = [OrderItemInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('phone_number', 'delivery_type', 'address')
        }),
        ('Статус', {
            'fields': ('is_done',)
        }),
        ('Итоги', {
            'fields': ('total_quantity', 'total_price'),
            'classes': ('collapse',)
        }),
        ('Служебное', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def total_quantity(self, obj):
        return obj.total_quantity

    total_quantity.short_description = "Кол-во товаров"

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = "Сумма заказа"


custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(SubCategory, SubCategoryAdmin)
custom_admin_site.register(Goods, GoodsAdmin)
custom_admin_site.register(Discounts, DiscountsAdmin)
custom_admin_site.register(Order, OrderAdmin)

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)