#!/usr/bin/env python
"""
Script to send order reminders for orders placed within the last 7 days.
Uses GraphQL to query orders and logs reminders.
"""

import os
import sys
from datetime import timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django environment
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")

import django

django.setup()

from django.utils import timezone

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# GraphQL query to get orders from the last 7 days
QUERY = gql("""
    query GetRecentOrders {
        orders {
            id
            orderDate
            customer {
                email
            }
        }
    }
""")


def get_recent_orders():
    """Query GraphQL for orders and filter those from last 7 days."""
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Execute query
        result = client.execute(QUERY)

        # Calculate date 7 days ago (timezone-aware)
        seven_days_ago = timezone.now() - timedelta(days=7)

        # Filter orders from last 7 days
        recent_orders = []
        for order in result.get("orders", []):
            order_date_str = order.get("orderDate")
            if order_date_str:
                # Parse ISO format datetime (GraphQL returns ISO format)
                from dateutil import parser

                order_date = parser.isoparse(order_date_str)
                # Make timezone-aware if needed
                if timezone.is_naive(order_date):
                    order_date = timezone.make_aware(order_date)
                # Check if order is within last 7 days
                if order_date >= seven_days_ago:
                    recent_orders.append(order)

        return recent_orders
    except Exception as e:
        print(f"Error querying GraphQL: {e}")
        return []


def log_order_reminders(orders):
    """Log order reminders to file."""
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/order_reminders_log.txt"

    with open(log_file, "a") as f:
        for order in orders:
            order_id = order.get("id")
            customer_email = order.get("customer", {}).get("email", "N/A")
            log_message = f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n"
            f.write(log_message)


def main():
    """Main function to process order reminders."""
    orders = get_recent_orders()
    log_order_reminders(orders)
    print("Order reminders processed!")


if __name__ == "__main__":
    main()
