from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL of the app renders 'home'path('products/', product_list_view, name='product-list'),
   ]
