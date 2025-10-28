# GraphQL CRM - Example Queries

This file contains example GraphQL queries and mutations you can use to test the API.

## Basic Queries

### Get All Customers
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

### Get All Products
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

### Get All Orders
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

## Filtering Examples

### Filter Customers by Name
```graphql
query {
  customers(name: "John") {
    id
    name
    email
  }
}
```

### Filter Products by Price Range
```graphql
query {
  products(priceMin: 100.0, priceMax: 500.0) {
    id
    name
    price
  }
}
```

### Filter Orders by Customer Name
```graphql
query {
  orders(customerName: "John") {
    id
    totalAmount
    customer {
      name
    }
  }
}
```

## Sorting Examples

### Sort Products by Price (Descending)
```graphql
query {
  products(orderBy: "-price") {
    id
    name
    price
  }
}
```

### Sort Customers by Name (Ascending)
```graphql
query {
  customers(orderBy: "name") {
    id
    name
    email
  }
}
```

### Sort Orders by Date (Newest First)
```graphql
query {
  orders(orderBy: "-orderDate") {
    id
    totalAmount
    orderDate
    customer {
      name
    }
  }
}
```

## Mutation Examples

### Create a New Customer
```graphql
mutation {
  createCustomer(input: {
    name: "Alice Wonder"
    email: "alice@example.com"
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

### Create Multiple Customers (Bulk)
```graphql
mutation {
  bulkCreateCustomers(inputs: [
    {
      name: "Customer One"
      email: "customer1@example.com"
      phone: "+1-555-0001"
    },
    {
      name: "Customer Two"
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

### Create a New Product
```graphql
mutation {
  createProduct(input: {
    name: "Wireless Headphones"
    price: "79.99"
    stock: 25
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

### Create an Order
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
        email
      }
      products {
        name
        price
      }
    }
  }
}
```

### Update a Customer
```graphql
mutation {
  updateCustomer(id: 1, input: {
    name: "John Updated"
    email: "john.updated@example.com"
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

### Update a Product
```graphql
mutation {
  updateProduct(id: 1, input: {
    name: "Updated Product Name"
    price: "129.99"
    stock: 30
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

### Delete a Customer
```graphql
mutation {
  deleteCustomer(id: 1) {
    success
    errors
  }
}
```

### Delete a Product
```graphql
mutation {
  deleteProduct(id: 1) {
    success
    errors
  }
}
```

### Delete an Order
```graphql
mutation {
  deleteOrder(id: 1) {
    success
    errors
  }
}
```

## Complex Queries

### Get Customer with All Orders
```graphql
query {
  customer(id: 1) {
    id
    name
    email
    orders {
      id
      totalAmount
      orderDate
      products {
        name
        price
      }
    }
  }
}
```

### Get Products with Low Stock
```graphql
query {
  products(priceMax: 50.0) {
    id
    name
    price
    stock
  }
}
```

### Get High-Value Orders
```graphql
query {
  orders(totalMin: 500.0) {
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

## Error Handling Examples

### Try to Create Customer with Duplicate Email
```graphql
mutation {
  createCustomer(input: {
    name: "Duplicate Email"
    email: "john.doe@example.com"
    phone: "+1-555-9999"
  }) {
    success
    errors
    customer {
      id
      name
    }
  }
}
```

### Try to Create Order with Non-existent Customer
```graphql
mutation {
  createOrder(input: {
    customerId: 999
    productIds: [1, 2]
  }) {
    success
    errors
    order {
      id
    }
  }
}
```

### Try to Get Non-existent Customer
```graphql
query {
  customer(id: 999) {
    id
    name
    email
  }
}
```

## How to Use

1. Start the Django server: `python manage.py runserver`
2. Open your browser and go to: http://localhost:8000/graphql
3. Copy any of the queries above into the GraphiQL interface
4. Click the "Play" button to execute the query
5. View the results in the right panel

The GraphiQL interface also provides:
- Auto-completion for field names
- Query validation
- Documentation explorer
- Query history
