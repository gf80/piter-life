from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    path('<slug:slug>/', views.category, name='category'),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/data/", views.get_cart, name="get_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/create_order/", views.create_order, name="create_order"),
]