import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
import re
from crm.models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


class OrderedDjangoFilterConnectionField(DjangoFilterConnectionField):
    """Custom connection field that supports order_by parameter"""

    def __init__(self, *args, **kwargs):
        # Store order_by argument definition but don't pass to parent
        self._order_by_arg = kwargs.pop("order_by", graphene.String())
        super().__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filterset_kwargs,
        *args,
        **kwargs,
    ):
        # Extract order_by before calling parent
        order_by = kwargs.pop("order_by", None)

        # Modify filterset_kwargs to apply ordering after filtering
        original_filterset_kwargs = filterset_kwargs.copy() if filterset_kwargs else {}

        # Create a custom filterset that applies ordering
        if order_by and filterset_class:
            # Capture order_by in closure
            order_by_value = order_by

            class OrderedFilterSet(filterset_class):
                @property
                def qs(self):
                    qs = super().qs
                    if order_by_value:
                        qs = qs.order_by(order_by_value)
                    return qs

            filterset_class = OrderedFilterSet

        # Call parent with modified filterset
        return super().connection_resolver(
            resolver,
            connection,
            default_manager,
            max_limit,
            enforce_first_or_last,
            filterset_class,
            original_filterset_kwargs,
            *args,
            **kwargs,
        )


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        interfaces = (graphene.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (graphene.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (graphene.Node,)


class Query(graphene.ObjectType):
    # DjangoFilterConnectionField queries for advanced filtering with order_by support
    all_customers = OrderedDjangoFilterConnectionField(
        CustomerType, filterset_class=CustomerFilter, order_by=graphene.String()
    )
    all_products = OrderedDjangoFilterConnectionField(
        ProductType, filterset_class=ProductFilter, order_by=graphene.String()
    )
    all_orders = OrderedDjangoFilterConnectionField(
        OrderType, filterset_class=OrderFilter, order_by=graphene.String()
    )

    def resolve_all_customers(self, info, **kwargs):
        # Return base queryset - ordering will be applied by the custom field
        return Customer.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()

    def resolve_all_orders(self, info, **kwargs):
        return (
            Order.objects.select_related("customer").prefetch_related("products").all()
        )

    # Simple list queries with filtering and sorting
    customers = graphene.List(
        CustomerType,
        order_by=graphene.String(),
        name=graphene.String(),
        email=graphene.String(),
    )
    products = graphene.List(
        ProductType,
        order_by=graphene.String(),
        name=graphene.String(),
        price_min=graphene.Float(),
        price_max=graphene.Float(),
    )
    orders = graphene.List(
        OrderType,
        order_by=graphene.String(),
        customer_name=graphene.String(),
        total_min=graphene.Float(),
        total_max=graphene.Float(),
    )

    # Single item queries
    customer = graphene.Field(CustomerType, id=graphene.Int())
    product = graphene.Field(ProductType, id=graphene.Int())
    order = graphene.Field(OrderType, id=graphene.Int())

    def resolve_customers(root, info, order_by=None, name=None, email=None):
        queryset = Customer.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def resolve_products(
        root, info, order_by=None, name=None, price_min=None, price_max=None
    ):
        queryset = Product.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def resolve_orders(
        root, info, order_by=None, customer_name=None, total_min=None, total_max=None
    ):
        queryset = Order.objects.select_related("customer").prefetch_related("products")

        if customer_name:
            queryset = queryset.filter(customer__name__icontains=customer_name)
        if total_min is not None:
            queryset = queryset.filter(total_amount__gte=total_min)
        if total_max is not None:
            queryset = queryset.filter(total_amount__lte=total_max)
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def resolve_customer(root, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(root, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(root, info, id):
        try:
            return (
                Order.objects.select_related("customer")
                .prefetch_related("products")
                .get(pk=id)
            )
        except Order.DoesNotExist:
            return None


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.Int(required=True)
    product_ids = graphene.List(graphene.Int, required=True)


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def validate_phone(self, phone):
        """Validate phone format: +1234567890 or 123-456-7890"""
        if not phone:
            return True
        # Pattern: + followed by digits, or digits with dashes
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return bool(re.match(pattern, phone))

    def mutate(self, info, input):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
            return CreateCustomer(
                customer=None,
                message="Failed to create customer",
                success=False,
                errors=errors,
            )

        # Validate phone format
        if input.phone and not self.validate_phone(input.phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890")
            return CreateCustomer(
                customer=None,
                message="Failed to create customer",
                success=False,
                errors=errors,
            )

        try:
            customer = Customer.objects.create(
                name=input.name, email=input.email, phone=input.phone or ""
            )
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True,
                errors=[],
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message="Failed to create customer",
                success=False,
                errors=[str(e)],
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def validate_phone(self, phone):
        """Validate phone format: +1234567890 or 123-456-7890"""
        if not phone:
            return True
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return bool(re.match(pattern, phone))

    def mutate(self, info, input):
        customers = []
        errors = []

        # Process each customer individually to support partial success
        for idx, input_data in enumerate(input):
            customer_errors = []

            # Validate email uniqueness
            if Customer.objects.filter(email=input_data.email).exists():
                customer_errors.append(
                    f"Row {idx + 1}: Email '{input_data.email}' already exists"
                )

            # Validate phone format
            if input_data.phone and not self.validate_phone(input_data.phone):
                customer_errors.append(
                    f"Row {idx + 1}: Invalid phone format. Use +1234567890 or 123-456-7890"
                )

            # If no validation errors, try to create the customer
            if not customer_errors:
                try:
                    customer = Customer.objects.create(
                        name=input_data.name,
                        email=input_data.email,
                        phone=input_data.phone or "",
                    )
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            else:
                errors.extend(customer_errors)

        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate price is positive
        if input.price <= 0:
            errors.append("Price must be positive")
            return CreateProduct(product=None, success=False, errors=errors)

        # Validate stock is non-negative
        stock_value = input.stock if input.stock is not None else 0
        if stock_value < 0:
            errors.append("Stock must be non-negative")
            return CreateProduct(product=None, success=False, errors=errors)

        try:
            product = Product.objects.create(
                name=input.name, price=input.price, stock=stock_value
            )
            return CreateProduct(product=product, success=True, errors=[])
        except Exception as e:
            return CreateProduct(product=None, success=False, errors=[str(e)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []

        # Validate at least one product is provided
        if not input.product_ids or len(input.product_ids) == 0:
            errors.append("At least one product must be selected")
            return CreateOrder(order=None, success=False, errors=errors)

        try:
            with transaction.atomic():
                # Get customer
                try:
                    customer = Customer.objects.get(pk=input.customer_id)
                except Customer.DoesNotExist:
                    errors.append(f"Invalid customer ID: {input.customer_id}")
                    return CreateOrder(order=None, success=False, errors=errors)

                # Get products
                products = Product.objects.filter(pk__in=input.product_ids)
                found_product_ids = set(products.values_list("id", flat=True))
                requested_product_ids = set(input.product_ids)

                # Check if all requested products exist
                missing_ids = requested_product_ids - found_product_ids
                if missing_ids:
                    errors.append(
                        f"Invalid product ID(s): {', '.join(map(str, missing_ids))}"
                    )
                    return CreateOrder(order=None, success=False, errors=errors)

                if not products.exists():
                    errors.append("No valid products found")
                    return CreateOrder(order=None, success=False, errors=errors)

                # Calculate total amount
                total_amount = sum(product.price for product in products)

                # Create order
                order = Order.objects.create(
                    customer=customer, total_amount=total_amount
                )
                order.products.set(products)

                return CreateOrder(order=order, success=True, errors=[])
        except Exception as e:
            return CreateOrder(order=None, success=False, errors=[str(e)])


class UpdateCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, input):
        try:
            customer = Customer.objects.get(pk=id)
            customer.name = input.name
            customer.email = input.email
            customer.phone = input.phone
            customer.save()
            return UpdateCustomer(customer=customer, success=True, errors=[])
        except Customer.DoesNotExist:
            return UpdateCustomer(
                customer=None, success=False, errors=["Customer not found"]
            )
        except Exception as e:
            return UpdateCustomer(customer=None, success=False, errors=[str(e)])


class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, input):
        try:
            product = Product.objects.get(pk=id)
            product.name = input.name
            product.price = input.price
            product.stock = input.stock
            product.save()
            return UpdateProduct(product=product, success=True, errors=[])
        except Product.DoesNotExist:
            return UpdateProduct(
                product=None, success=False, errors=["Product not found"]
            )
        except Exception as e:
            return UpdateProduct(product=None, success=False, errors=[str(e)])


class DeleteCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        try:
            customer = Customer.objects.get(pk=id)
            customer.delete()
            return DeleteCustomer(success=True, errors=[])
        except Customer.DoesNotExist:
            return DeleteCustomer(success=False, errors=["Customer not found"])
        except Exception as e:
            return DeleteCustomer(success=False, errors=[str(e)])


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True, errors=[])
        except Product.DoesNotExist:
            return DeleteProduct(success=False, errors=["Product not found"])
        except Exception as e:
            return DeleteProduct(success=False, errors=[str(e)])


class DeleteOrder(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        try:
            order = Order.objects.get(pk=id)
            order.delete()
            return DeleteOrder(success=True, errors=[])
        except Order.DoesNotExist:
            return DeleteOrder(success=False, errors=["Order not found"])
        except Exception as e:
            return DeleteOrder(success=False, errors=[str(e)])


class UpdateLowStockProducts(graphene.Mutation):
    """Mutation to update low-stock products (stock < 10) by incrementing stock by 10."""

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        try:
            with transaction.atomic():
                # Find products with stock < 10
                low_stock_products = Product.objects.filter(stock__lt=10)

                # Increment stock by 10 for each product
                updated_products_list = []
                for product in low_stock_products:
                    product.stock += 10
                    product.save()
                    updated_products_list.append(product)

                message = (
                    f"Updated {len(updated_products_list)} product(s) with low stock."
                )
                return UpdateLowStockProducts(
                    success=True,
                    message=message,
                    updated_products=updated_products_list,
                )
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low stock products: {str(e)}",
                updated_products=[],
            )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_customer = UpdateCustomer.Field()
    update_product = UpdateProduct.Field()
    delete_customer = DeleteCustomer.Field()
    delete_product = DeleteProduct.Field()
    delete_order = DeleteOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
