import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from decimal import Decimal
from crm.models import Customer, Product, Order
from crm.models import Product
from .filters import CustomerFilter, ProductFilter, OrderFilter


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
    # DjangoFilterConnectionField queries for advanced filtering
    all_customers = DjangoFilterConnectionField(
        CustomerType, filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType, filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

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
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.create(
                name=input.name, email=input.email, phone=input.phone
            )
            return CreateCustomer(customer=customer, success=True, errors=[])
        except Exception as e:
            return CreateCustomer(customer=None, success=False, errors=[str(e)])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, inputs):
        customers = []
        errors = []

        try:
            with transaction.atomic():
                for input_data in inputs:
                    customer = Customer.objects.create(
                        name=input_data.name,
                        email=input_data.email,
                        phone=input_data.phone,
                    )
                    customers.append(customer)
            return BulkCreateCustomers(customers=customers, success=True, errors=[])
        except Exception as e:
            return BulkCreateCustomers(customers=[], success=False, errors=[str(e)])


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            product = Product.objects.create(
                name=input.name, price=input.price, stock=input.stock
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
        try:
            with transaction.atomic():
                # Get customer
                try:
                    customer = Customer.objects.get(pk=input.customer_id)
                except Customer.DoesNotExist:
                    return CreateOrder(
                        order=None, success=False, errors=["Customer not found"]
                    )

                # Get products
                products = Product.objects.filter(pk__in=input.product_ids)
                if not products.exists():
                    return CreateOrder(
                        order=None, success=False, errors=["No valid products found"]
                    )

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
