"""
Cron jobs for the CRM application.
"""

from django.utils import timezone
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm the CRM application's health.
    Runs every 5 minutes.
    """
    # Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    timestamp = timezone.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append to log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optionally query the GraphQL hello field to verify endpoint is responsive
    try:
        GRAPHQL_URL = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("""
            query {
                hello
            }
        """)

        result = client.execute(query)
        # If we get here, the endpoint is responsive
        return True
    except Exception as e:
        # Log error but don't fail the heartbeat
        error_message = f"{timestamp} GraphQL endpoint check failed: {str(e)}\n"
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(error_message)
        return False


def update_low_stock():
    """
    Update low-stock products (stock < 10) by incrementing stock by 10.
    Runs every 12 hours.
    """
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        GRAPHQL_URL = "http://localhost:8000/graphql"
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Execute the UpdateLowStockProducts mutation
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        mutation_result = result.get("updateLowStockProducts", {})

        # Log the results
        log_file = "/tmp/low_stock_updates_log.txt"
        with open(log_file, "a") as f:
            if mutation_result.get("success"):
                updated_products = mutation_result.get("updatedProducts", [])
                f.write(
                    f"{timestamp} - Update successful. Updated {len(updated_products)} product(s):\n"
                )
                for product in updated_products:
                    product_name = product.get("name", "N/A")
                    new_stock = product.get("stock", "N/A")
                    f.write(
                        f"  {timestamp} - Product: {product_name}, New Stock: {new_stock}\n"
                    )
            else:
                error_msg = mutation_result.get("message", "Unknown error")
                f.write(f"{timestamp} - Update failed: {error_msg}\n")

        return mutation_result.get("success", False)
    except Exception as e:
        # Log error
        log_file = "/tmp/low_stock_updates_log.txt"
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error executing mutation: {str(e)}\n")
        return False
