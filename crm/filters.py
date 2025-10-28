import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    phone = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFilter()
    created_at__gte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at__lte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "created_at"]


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    price = django_filters.NumberFilter()
    price__gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock = django_filters.NumberFilter()
    stock__gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock__lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    customer__name = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    customer__email = django_filters.CharFilter(
        field_name="customer__email", lookup_expr="icontains"
    )
    total_amount = django_filters.NumberFilter()
    total_amount__gte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    total_amount__lte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )
    order_date = django_filters.DateTimeFilter()
    order_date__gte = django_filters.DateTimeFilter(
        field_name="order_date", lookup_expr="gte"
    )
    order_date__lte = django_filters.DateTimeFilter(
        field_name="order_date", lookup_expr="lte"
    )

    class Meta:
        model = Order
        fields = ["customer__name", "customer__email", "total_amount", "order_date"]
