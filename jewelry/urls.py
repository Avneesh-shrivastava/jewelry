"""
URL configuration for jewelry_ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from zevera.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_page, name="home_page"),
    path('admin/', admin.site.urls),
    path('new-arrivals/', new_arrivals, name="new_arrivals"),
    path('home-page/', home_page, name="home_page"),
    path('products/<int:id>/', products, name="products"),
    path('product-overview/<int:id>/', product_overview, name="product_overview"),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('remove-cart/<int:rm_id>/', remove_cart, name='remove_cart'),
    path('update-cart/<int:cart_id>/', update_cart, name='update_cart'),
    path('api/', include('api.urls')),
    path('logout/', logout_view, name="logout"),
    path('checkout/', checkout, name="checkout"),
    path('checkout/', checkout, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('razorpay-payment/<int:order_id>/',razorpay_payment, name='razorpay_payment'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
