# Setup Guide

## Initial Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and update with your settings:
```bash
cp .env.example .env
```

### 4. Database Setup

For SQLite (development):
```bash
python manage.py migrate
```

For PostgreSQL (production):
1. Create a PostgreSQL database
2. Update `.env` with database credentials
3. Run migrations:
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Create Initial Tenant and Roles

After creating a superuser, log into the admin and:
1. Create a Tenant
2. Create Locations (Production, Store, Shop)
3. Create Roles (Production Manager, Store Manager, Shop Manager, etc.)
4. Assign users to locations with roles

### 7. Run Development Server
```bash
python manage.py runserver
```

## Database Schema

The system uses the following main tables:

### Core
- `tenants` - Multi-tenant organizations
- `locations` - Production, Stores, Shops
- `users` - Custom user model with tenant support
- `roles` - Role definitions
- `user_location_roles` - User-location-role associations

### Inventory
- `products` - Product catalog
- `batches` - Production batches
- `inventory_ledger` - Append-only inventory transactions
- `stock_balances` - Current stock levels (materialized view)

### Transfers
- `transfers` - Transfers between locations
- `shop_orders` - Shop orders to stores
- `return_requests` - Return requests

### Sales
- `sales` - Sales transactions
- `payments` - Payment records
- `refunds` - Refund transactions
- `credit_accounts` - Customer credit accounts

### Accounting
- `cash_up_reports` - Cash reconciliation reports
- `remittances` - Cash remittances

## API Structure

The API follows RESTful conventions:

- `/api/auth/` - Authentication endpoints
- `/api/inventory/` - Inventory management
- `/api/transfers/` - Transfer and order management
- `/api/sales/` - POS and sales operations
- `/api/accounting/` - Accounting and remittance
- `/api/notifications/` - Notifications
- `/api/analytics/` - Analytics and reporting
- `/api/config/` - Configuration management

## State Machine Workflows

### Transfer Workflow
1. Create transfer (Draft)
2. Add items
3. Send transfer (Sent)
4. Receive at destination (Received/Partially Received)
5. Close transfer

### Shop Order Workflow
1. Create order (Draft)
2. Submit for approval (Submitted)
3. Approve (Approved)
4. Fulfill (Fulfilled)
5. Close

### Sale Workflow
1. Create sale with items
2. Add payments
3. Complete sale
4. Process refunds if needed

## Testing

Run tests:
```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Update `SECRET_KEY` with a secure key
3. Configure proper database (PostgreSQL recommended)
4. Set up static files serving
5. Configure Redis for Celery
6. Set up proper email/SMS providers
7. Configure proper CORS origins
8. Use a production WSGI server (gunicorn, uwsgi)
9. Set up reverse proxy (nginx)

## Troubleshooting

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Database Reset (Development Only)
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

