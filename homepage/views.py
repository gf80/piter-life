from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from goods.models import Category, SubCategory, Goods
from discounts.models import Discounts
from django.db.models import Count

def home_page(request):
    """Обработчик для главной страницы"""
    categories = Category.objects.annotate(
        goods_count=Count('goods')
    ).filter(goods_count__gt=0)
    
    discounts = Discounts.objects.filter(is_active=True)
    
    # Данные, которые мы передадим в шаблон
    context = {
        'categories': categories,
        'discounts': discounts,
    }
    
    # Возвращаем ответ с шаблоном
    return render(request, 'homepage/index.html', context)

def privacy_page(request):
    """Обработчик для политики конфиденциальности"""
    categories = Category.objects.all()
    
    # Данные, которые мы передадим в шаблон
    context = {
        'categories': categories,
    }
    
    # Возвращаем ответ с шаблоном
    return render(request, 'homepage/privacy.html', context)

def user_term_page(request):
    """Обработчик для политики конфиденциальности"""
    categories = Category.objects.all()
    
    # Данные, которые мы передадим в шаблон
    context = {
        'categories': categories,
    }
    
    # Возвращаем ответ с шаблоном
    return render(request, 'homepage/user-term.html', context)

def delivery_page(request):
    """Обработчик для политики конфиденциальности"""
    categories = Category.objects.all()
    
    # Данные, которые мы передадим в шаблон
    context = {
        'categories': categories,
    }
    
    # Возвращаем ответ с шаблоном
    return render(request, 'homepage/delivery.html', context)

