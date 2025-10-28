from django.contrib import admin
from .models import Customer, Product, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email"]
    ordering = ["-created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock"]
    list_filter = ["price"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "total_amount", "order_date"]
    list_filter = ["order_date", "customer"]
    search_fields = ["customer__name", "customer__email"]
    ordering = ["-order_date"]
    filter_horizontal = ["products"]
