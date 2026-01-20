import calendar
import json
from django.contrib.admin import AdminSite
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order, OrderItem
from goods.models import Goods

from django.utils.timezone import now
from datetime import datetime, timedelta, timezone

from django.db.models import Count, Sum, Avg


class CustomAdminSite(AdminSite):
    site_header = "Admin Panel"
    site_title = "Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        print("CUSTOM INDEX WORKS")
        total_revenue = total_revenue = sum([
            order.total_price for order in Order.objects.filter(is_done=True).all()
        ])

        all_orders = Order.objects.count()

        total_goods = Goods.objects.count()

        new_orders = Order.objects.filter(is_done=True).count()
        
        # Получаем стандартный контекст
        context = {
            **self.each_context(request),
            "app_list": self.get_app_list(request),
            "total_revenue": total_revenue,
            "all_orders": all_orders,
            "total_goods": total_goods,
            "new_orders": new_orders,
        }
        
        return render(request, "admin/custom_index.html", context)


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("orders/", self.admin_view(self.orders_page), name="orders"),
            path("orders/data/", self.admin_view(self.orders_data), name="orders_data"),
            path("orders/toggle/", self.admin_view(self.toggle_order), name="toggle_order"),
            path("orders/<int:order_id>/", self.admin_view(self.order_detail_view), name="order_detail"),
            path("reports/", self.admin_view(self.reports_view), name="reports"),

        ]
        return custom_urls + urls

    def reports_view(self, request):
        # Получаем параметр месяца
        month_param = request.GET.get('month', None)
        
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                start_date = datetime(year, month, 1)
                end_date = datetime(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1)
            except:
                # Если ошибка - текущий месяц
                today = datetime.now()
                start_date = today.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1)
        else:
            # По умолчанию текущий месяц
            today = datetime.now()
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
        
        # Форматируем месяц для отображения
        month_display = start_date.strftime("%B %Y").replace(
            "January", "Январь").replace("February", "Февраль").replace(
            "March", "Март").replace("April", "Апрель").replace(
            "May", "Май").replace("June", "Июнь").replace(
            "July", "Июль").replace("August", "Август").replace(
            "September", "Сентябрь").replace("October", "Октябрь").replace(
            "November", "Ноябрь").replace("December", "Декабрь")
        
        # Основные данные
        orders = Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
        
        total_orders = orders.count()
        completed_orders = orders.filter(is_done=True).count()
        
        # Выручка
        total_revenue = total_revenue = sum([
            order.total_price for order in Order.objects.filter(is_done=True).all()
        ])

        # Средние значения
        avg_check = 0
        if completed_orders > 0:
            avg_check = total_revenue / completed_orders
        
        # Статистика по дням (упрощённая)
        daily_stats = []
        current_date = start_date
        while current_date < end_date:
            day_end = current_date + timedelta(days=1)
            day_orders = orders.filter(created_at__gte=current_date, created_at__lt=day_end)
            day_completed = day_orders.filter(is_done=True)
            
            daily_stats.append({
                'date': current_date,
                'total_orders': day_orders.count(),
                'completed_orders': day_completed.count(),

            })
            
            current_date = day_end
        
        # Дополнительная статистика
        delivery_count = orders.filter(delivery_type='delivery').count()
        pickup_count = orders.filter(delivery_type='pickup').count()
        
        # Среднедневная выручка
        days_in_month = (end_date - start_date).days
        daily_avg = total_revenue / days_in_month if days_in_month > 0 else 0
        
        context = {
            **self.each_context(request),
            'month': month_display,
            'today': datetime.now(),
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'avg_check': avg_check,
            'daily_avg': daily_avg,
            'daily_stats': daily_stats,
            'delivery_count': delivery_count,
            'pickup_count': pickup_count,
            'peak_hour': "12:00-14:00",  # Можно вычислить реальные данные
            'cancelled_orders': 0,  # Если есть поле отмены
        }
        
        return render(request, 'admin/reports.html', context)

    def orders_page(self, request):
        context = {
            **self.each_context(request),
        }
        return render(request, "admin/orders.html", context)
    
    def order_detail_view(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            id=order_id
        )

        context = dict(
            self.each_context(request),
            order=order,
            title=f"Заказ №{order.id}",
        )
        return render(request, "admin/order_detail.html", context)

    # 📡 Получение данных (AJAX)
    def orders_data(self, request):
        orders = Order.objects.order_by("-created_at")
        data = [
            {
                "id": o.id,
                "phone_number": o.phone_number,
                "address": o.address or "",
                "delivery_type": o.get_delivery_type_display(),
                "total_quantity": o.total_quantity,
                "total_price": str(o.total_price),
                "is_done": o.is_done,
                "created": o.created_at.strftime("%d.%m.%Y %H:%M"),
            }
            for o in orders
        ]
        return JsonResponse({"orders": data})


    def toggle_order(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Invalid method"}, status=400)

        try:
            order_id = None
            is_done = None
            
            # Проверяем Content-Type
            content_type = request.content_type
            
            if 'application/json' in content_type:
                # JSON запрос
                payload = json.loads(request.body)
                order_id = payload.get("id")
                is_done = payload.get("is_done")
            else:
                # Form-data запрос
                order_id = request.POST.get("id")
                is_done_str = request.POST.get("is_done", "false").lower()
                is_done = is_done_str == "true"
            
            if not order_id:
                return JsonResponse({"error": "Order ID is required"}, status=400)
            
            order = get_object_or_404(Order, id=order_id)
            order.is_done = is_done
            order.save()

            return redirect('admin:order_detail', order_id=order_id)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


    def order_items_data(self, request, order_id):
        order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=order_id)
        items = [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": str(item.price),
                "total": str(item.total_price)
            }
            for item in order.items.all()
        ]
        return JsonResponse({"items": items})