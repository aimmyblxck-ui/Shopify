
from django.urls import path
from . import views


urlpatterns = [

    path('', views.home_view, name='home'),

    path(
        'products/',
        views.products_view,
        name='products'
    ),

    path(
        'product/<slug:slug>/',
        views.product_detail_view,
        name='product_detail'
    ),

    path(
        'cart/',
        views.cart_detail_view,
        name='cart'
    ),

    path(
        'cart/add/<int:product_id>/',
        views.cart_add_view,
        name='cart_add'
    ),

    path(
        'cart/update/<int:product_id>/',
        views.cart_update_view,
        name='cart_update'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.cart_remove_view,
        name='cart_remove'
    ),

    path(
        'checkout/',
        views.checkout_view,
        name='checkout'
    ),

    path(
        'order-success/<str:order_number>/',
        views.order_success_view,
        name='order_success'
    ),

    path('about/', views.about_view, name='about'),

    path('contact/', views.contact_view, name='contact'),

]
