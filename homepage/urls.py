from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.home_page, name='index'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('terms-of-use/', views.user_term_page, name='terms-of-use'),
    path('delivery', views.delivery_page, name='delivery')
]