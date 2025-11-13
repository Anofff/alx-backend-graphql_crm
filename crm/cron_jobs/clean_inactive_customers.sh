#!/bin/bash
# Script to clean up inactive customers with no orders since a year ago

# Get the absolute path to the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Execute Django shell command to delete inactive customers
python "$PROJECT_DIR/manage.py" shell << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
import django
django.setup()

from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, Q
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders OR whose most recent order is older than a year
customers_to_delete = Customer.objects.annotate(
    last_order_date=Max('orders__order_date')
).filter(
    Q(last_order_date__lt=one_year_ago) | Q(last_order_date__isnull=True)
)

# Count before deletion
count = customers_to_delete.count()

# Delete customers
customers_to_delete.delete()

# Log the result
log_message = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - Deleted {count} inactive customer(s)\n"
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(log_message)

print(f"Deleted {count} inactive customer(s)")
EOF

