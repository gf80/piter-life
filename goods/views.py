import json
import random
from django.shortcuts import render, get_object_or_404
from goods.models import Category, Goods

from django.db.models import Count

from django.http import JsonResponse

from collections import defaultdict

from orders.models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt


def category(request, slug):
    """Товары по категории с группировкой по подкатегориям"""
    categories = Category.objects.annotate(
        goods_count=Count('goods')
    ).filter(goods_count__gt=0)

    category = get_object_or_404(Category, slug=slug)
    
    # Сортируем подкатегории по полю order или name
    subcategories = category.subcategories.annotate(
        goods_count=Count('goods')
    ).filter(goods_count__gt=0).order_by('name')  # или 'order' если есть такое поле
    
    # Получаем все товары категории
    all_goods = Goods.objects.filter(category=category, is_available=True)

    to_order = all_goods.order_by('?')[:4]
    
    # Группируем товары по подкатегориям
    goods_by_subcategory = defaultdict(list)
    goods_without_subcategory = []
    
    for good in all_goods:
        if good.subcategory:
            goods_by_subcategory[good.subcategory].append(good)
        else:
            goods_without_subcategory.append(good)
    
    # Сортируем товары внутри каждой подкатегории
    for subcat in goods_by_subcategory:
        goods_by_subcategory[subcat].sort(key=lambda x: x.name)  # или x.price, x.created_at
    
    # Сортируем и товары без подкатегории
    goods_without_subcategory.sort(key=lambda x: x.name)
    
    # Создаем отсортированный словарь в порядке subcategories
    sorted_goods_by_subcategory = {}
    for subcat in subcategories:
        if subcat in goods_by_subcategory:
            sorted_goods_by_subcategory[subcat] = goods_by_subcategory[subcat]
    
    context = {
        'categories': categories,
        'active_category': category,
        'category': category,
        'subcategories': subcategories,
        'goods_by_subcategory': sorted_goods_by_subcategory,
        'goods_without_subcategory': goods_without_subcategory,
        'title': f'Категория: {category.name}',
        'to_order': to_order
    }
    return render(request, 'goods/index.html', context)

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        product_id = int(request.POST.get("product_id"))
        product = Goods.objects.filter(id=product_id)

        cart = request.session.get("cart", {})

        if product_id in cart:
            cart[product_id]["quantity"] += 1
        else:
            cart[product_id] = {
                "name": product.name,
                "price": product.price,
                "quantity": 1,
                "image": product.image
            }

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({"success": True, "cart_count": len(cart)})
    return JsonResponse({"error": "Invalid method"}, status=400)


def get_cart(request):
    cart = request.session.get("cart", {})
    return JsonResponse({"cart": cart})


@csrf_exempt
def update_cart(request):
    """Обновить количество товара в корзине"""
    if request.method == "POST":
        try:
            # Получаем данные из JSON
            data = json.loads(request.body)
            product_id = str(data.get("product_id"))
            quantity = int(data.get("quantity", 1))
            
            if quantity < 1:
                return JsonResponse({
                    "success": False,
                    "error": "Количество должно быть больше 0"
                })
            
            cart = request.session.get("cart", {})

            print(cart)
            
            if product_id in cart:
                # Обновляем существующий товар
                cart[product_id]["quantity"] = quantity
                request.session["cart"] = cart
                request.session.modified = True
                
                # Пересчитываем итоги
                total = sum(item["price"] * item["quantity"] for item in cart.values())
                total_items = sum(item["quantity"] for item in cart.values())
                
                return JsonResponse({
                    "success": True,
                    "cart": cart,
                    "total": total,
                    "cart_count": total_items,
                    "message": "Корзина обновлена"
                })
            else:
                # Если товара нет в корзине, добавляем его
                try:
                    # Используем get() для получения одного объекта
                    product = Goods.objects.get(id=product_id)
                    
                    cart[product_id] = {
                        "name": product.name,
                        "price": float(product.price),
                        "quantity": quantity,
                        "image": str(product.image) if product.image else ""
                    }
                    
                    request.session["cart"] = cart
                    request.session.modified = True
                    
                    # Пересчитываем итоги
                    total = sum(item["price"] * item["quantity"] for item in cart.values())
                    total_items = sum(item["quantity"] for item in cart.values())
                    
                    return JsonResponse({
                        "success": True,
                        "cart": cart,
                        "total": total,
                        "cart_count": total_items,
                        "message": "Товар добавлен в корзину"
                    })
                    
                except Goods.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "error": f"Товар с ID {product_id} не найден"
                    })
                
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
    
    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def remove_from_cart(request):
    """Удалить товар из корзины"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = str(data.get("product_id"))
            
            cart = request.session.get("cart", {})
            
            if product_id in cart:
                # Удаляем товар
                del cart[product_id]
                request.session["cart"] = cart
                request.session.modified = True
                
                return JsonResponse({
                    "success": True,
                    "cart": cart,
                    "message": "Товар удален из корзины"
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Товар не найден в корзине"
                })
                
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
    
    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def clear_cart(request):
    """Очистить всю корзину"""
    if request.method == "POST":
        try:
            request.session["cart"] = {}
            request.session.modified = True
            
            return JsonResponse({
                "success": True,
                "message": "Корзина очищена"
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
    
    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def create_order(request):
    """Создать заказ из корзины"""
    if request.method == "POST":
        try:
            # Получаем данные заказа
            data = json.loads(request.body)
            
            print(data)

            # Проверяем корзину
            cart = request.session.get("cart", {})
            if not cart:
                return JsonResponse({
                    "success": False,
                    "error": "Корзина пуста"
                })
            
            # Получаем данные клиента
            phone = data.get("phone", "").strip()
            delivery_type = data.get("delivery_type", "pickup")
            address = data.get("address", "").strip()
            
            # Валидация телефона
            if not phone:
                return JsonResponse({
                    "success": False,
                    "error": "Укажите телефон"
                })
            
            # Если выбрана доставка, проверяем адрес
            if delivery_type == "delivery" and not address:
                return JsonResponse({
                    "success": False,
                    "error": "Укажите адрес доставки"
                })
            
            # Рассчитываем итоговую сумму
            total_amount = sum(item["price"] * item["quantity"] for item in cart.values())
            
            # Добавляем стоимость доставки если нужно
            # if delivery_type == "delivery":
            #     delivery_cost = 300  # или другая логика расчета
            #     total_amount += delivery_cost
            
            # Создаем заказ в базе данных
            # Если есть авторизованный пользователь, привязываем к нему
            
            order = Order.objects.create(
                phone_number=phone,
                delivery_type=delivery_type,
                address=address if delivery_type == "delivery" else "",
            )
            
            # Добавляем товары в заказ
            for product_id, item in cart.items():
                try:
                    # Пытаемся найти товар в базе
                    product = Goods.objects.get(id=product_id)
                except Goods.DoesNotExist:
                    # Если товара нет в базе, создаем запись с данными из корзины
                    product = None
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item["price"],
                    quantity=item["quantity"]
                )
            
            # Очищаем корзину после создания заказа
            request.session["cart"] = {}
            request.session.modified = True
            
            return JsonResponse({
                "success": True,
                "order_id": order.id,
                "order_number": order.id,  # если есть поле order_number
                "total_amount": total_amount,
                "message": "Заказ успешно создан"
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
    
    return JsonResponse({"error": "Invalid method"}, status=400)
