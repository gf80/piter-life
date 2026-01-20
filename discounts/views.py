from django.shortcuts import render
from .models import Discounts
from goods.models import Category

def discounts_page(request):
    """Обработчик для главной страницы"""
    categories = Category.objects.all()
    discounts = Discounts.objects.filter(is_active=True)
    
    # Данные, которые мы передадим в шаблон
    context = {
        'categories': categories,
        'discounts': discounts,
    }
    
    # Возвращаем ответ с шаблоном
    return render(request, 'discounts/index.html', context)