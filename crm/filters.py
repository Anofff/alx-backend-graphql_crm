import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    name__icontains = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )
    email = django_filters.CharFilter(lookup_expr="icontains")
    phone = django_filters.CharFilter(lookup_expr="icontains")
    created_at = django_filters.DateTimeFilter()
    created_at__gte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    createdAtGte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at__lte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    createdAtLte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    # Custom filter for phone pattern (starts with +1)
    phone_pattern = django_filters.CharFilter(method="filter_phone_pattern")

    def filter_phone_pattern(self, queryset, name, value):
        """Filter customers with phone numbers starting with a specific pattern"""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset

    class Meta:
        model = Customer
        fields = ["name", "email", "phone", "created_at"]


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    price = django_filters.NumberFilter()
    price__gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    priceGte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    priceLte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock = django_filters.NumberFilter()
    stock__gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stockGte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock__lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    stockLte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    # Filter for low stock (stock < 10)
    low_stock = django_filters.BooleanFilter(method="filter_low_stock")

    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (stock < 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    customer__name = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    customer_name = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    customer__email = django_filters.CharFilter(
        field_name="customer__email", lookup_expr="icontains"
    )
    # Filter by product name
    product__name = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains"
    )
    product_name = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains"
    )
    # Filter by product ID
    product_id = django_filters.NumberFilter(field_name="products__id")
    total_amount = django_filters.NumberFilter()
    total_amount__gte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    totalAmountGte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    total_amount__lte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )
    totalAmountLte = django_filters.NumberFilter(
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
