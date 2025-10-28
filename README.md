# Django GraphQL CRM

A comprehensive Customer Relationship Management (CRM) system built with Django and GraphQL using graphene-django.

## Features

- **GraphQL API** with full CRUD operations
- **Customer Management** - Create, read, update, delete customers
- **Product Management** - Manage product catalog with pricing and stock
- **Order Management** - Handle customer orders with multiple products
- **Advanced Filtering** - Filter customers, products, and orders by various criteria
- **Sorting** - Sort results by any field
- **Bulk Operations** - Bulk create customers
- **Error Handling** - Comprehensive error handling with detailed messages
- **Data Validation** - Input validation for all mutations

## Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py             # URL configuration
│   ├── wsgi.py
│   └── schema.py           # Main GraphQL schema
├── crm/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Django models
│   ├── schema.py           # GraphQL types and mutations
│   ├── filters.py          # Django filters for GraphQL
│   └── migrations/
├── seed_db.py              # Database seeding script
├── test_graphql.py         # Comprehensive test suite
└── requirements.txt
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx-backend-graphql_crm
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Seed the database**
   ```bash
   python seed_db.py
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access GraphiQL interface**
   Open your browser and go to: http://localhost:8000/graphql

## GraphQL API Usage

### Queries

#### Get All Customers
```graphql
query {
  customers {
    id
    name
    email
    phone
    createdAt
  }
}
```

#### Get All Products
```graphql
query {
  products {
    id
    name
    price
    stock
  }
}
```

#### Get All Orders with Relationships
```graphql
query {
  orders {
    id
    totalAmount
    orderDate
    customer {
      name
      email
    }
    products {
      name
      price
    }
  }
}
```

#### Filter Customers by Name
```graphql
query {
  customers(name: "John") {
    id
    name
    email
  }
}
```

#### Sort Products by Price (Descending)
```graphql
query {
  products(orderBy: "-price") {
    id
    name
    price
  }
}
```

#### Filter Products by Price Range
```graphql
query {
  products(priceMin: 100.0, priceMax: 500.0) {
    id
    name
    price
  }
}
```

### Mutations

#### Create Customer
```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john@example.com"
    phone: "+1-555-0123"
  }) {
    success
    errors
    customer {
      id
      name
      email
    }
  }
}
```

#### Bulk Create Customers
```graphql
mutation {
  bulkCreateCustomers(inputs: [
    {
      name: "Customer 1"
      email: "customer1@example.com"
      phone: "+1-555-0001"
    },
    {
      name: "Customer 2"
      email: "customer2@example.com"
      phone: "+1-555-0002"
    }
  ]) {
    success
    errors
    customers {
      id
      name
      email
    }
  }
}
```

#### Create Product
```graphql
mutation {
  createProduct(input: {
    name: "New Product"
    price: "99.99"
    stock: 50
  }) {
    success
    errors
    product {
      id
      name
      price
      stock
    }
  }
}
```

#### Create Order
```graphql
mutation {
  createOrder(input: {
    customerId: 1
    productIds: [1, 2, 3]
  }) {
    success
    errors
    order {
      id
      totalAmount
      customer {
        name
      }
      products {
        name
        price
      }
    }
  }
}
```

#### Update Customer
```graphql
mutation {
  updateCustomer(id: 1, input: {
    name: "Updated Name"
    email: "updated@example.com"
    phone: "+1-555-9999"
  }) {
    success
    errors
    customer {
      id
      name
      email
    }
  }
}
```

#### Delete Customer
```graphql
mutation {
  deleteCustomer(id: 1) {
    success
    errors
  }
}
```

## Models

### Customer
- `id` - Primary key
- `name` - Customer name (CharField, max 100 chars)
- `email` - Email address (EmailField, unique)
- `phone` - Phone number (CharField, max 20 chars, optional)
- `created_at` - Creation timestamp (DateTimeField, auto-created)

### Product
- `id` - Primary key
- `name` - Product name (CharField, max 100 chars)
- `price` - Product price (DecimalField, 10 digits, 2 decimal places)
- `stock` - Stock quantity (PositiveIntegerField, default 0)

### Order
- `id` - Primary key
- `customer` - Foreign key to Customer
- `products` - Many-to-many relationship with Product
- `total_amount` - Total order amount (DecimalField, 10 digits, 2 decimal places)
- `order_date` - Order timestamp (DateTimeField, auto-created)

## Testing

Run the comprehensive test suite:

```bash
python test_graphql.py
```

This will test:
- All GraphQL queries
- All mutations
- Error handling scenarios
- Filtering and sorting functionality

## API Features

### Filtering
- **Customers**: Filter by name, email
- **Products**: Filter by name, price range
- **Orders**: Filter by customer name, total amount range

### Sorting
- Sort any query result by any field
- Use `-` prefix for descending order
- Example: `orderBy: "-price"` for price descending

### Error Handling
- Comprehensive error messages for all operations
- Validation errors for invalid input
- Database constraint errors (e.g., duplicate emails)
- Not found errors for invalid IDs

### Bulk Operations
- Bulk create customers with transaction support
- Atomic operations ensure data consistency

## Development

### Adding New Fields
1. Update the Django model in `crm/models.py`
2. Create and run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Update GraphQL types in `crm/schema.py`
4. Update filters in `crm/filters.py` if needed

### Adding New Mutations
1. Define input type in `crm/schema.py`
2. Create mutation class with proper error handling
3. Add mutation to the Mutation class
4. Update tests in `test_graphql.py`

## Dependencies

- Django 5.2.7
- graphene-django 3.2.3
- django-filter 25.2
- graphql-core 3.2.6

## License

This project is part of the ALX Backend Specialization curriculum.
