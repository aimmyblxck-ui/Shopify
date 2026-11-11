
from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug']

    prepopulated_fields = {
        'slug': ('name',)
    }

    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'category',
        'price',
        'stock',
        'is_available'
    ]

    list_filter = [
        'category',
        'is_available'
    ]

    list_editable = [
        'price',
        'stock',
        'is_available'
    ]

    prepopulated_fields = {
        'slug': ('name',)
    }

    search_fields = ['name']


class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0
    readonly_fields = [
        'product',
        'quantity',
        'price'
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        'order_number',
        'full_name',
        'total_amount',
        'status',
        'created_at'
    ]

    list_filter = ['status']

    readonly_fields = [
        'order_number',
        'total_amount',
        'created_at'
    ]

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = [
        'order',
        'product',
        'quantity',
        'price'
    ]
