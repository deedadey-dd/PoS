# Modular Multi-Store POS, Inventory, and Accounting Platform

A highly configurable, multi-tenant point-of-sale and inventory management platform for organizations that produce goods in-house, distribute through central stores/warehouses, and sell via multiple shops.

## Features

### Core Modules

- **Multi-Tenancy**: Complete tenant isolation with configurable terminology
- **Production & Batch Management**: Track production batches with costing
- **Inventory & Ledger System**: Append-only ledger for audit trail
- **Transfers & Fulfillment**: Production → Stores → Shop transfers with state machines
- **Shop POS**: Complete POS system with sales, returns, credit sales
- **Pricing & Costing**: Flexible pricing rules with margin management
- **Returns & Disputes**: Comprehensive return workflow
- **Accounting & Cash Remittance**: Cash-up reports and remittance tracking
- **Credit Accounts**: Accounts receivable management
- **Analytics & Reporting**: Performance and financial analytics
- **Notifications**: In-app, email, and SMS notifications
- **Audit Logs**: Complete audit trail for compliance

## Architecture

### Django Apps

- `core`: Multi-tenancy, users, locations, roles
- `inventory`: Products, batches, inventory ledger, stock balances
- `transfers`: Transfers, shop orders, returns, disputes
- `sales`: POS sales, payments, refunds, pricing, credit accounts
- `accounting`: Cash-up reports, remittances
- `notifications`: Notification system and templates
- `analytics`: Analytics caching and reporting
- `config`: System and workflow configurations

### State Machines

The system uses `django-fsm` for workflow management:

- **Batch Transfer**: Draft → Sent → Received/Partially Received → Closed
- **Shop Order**: Draft → Submitted → Approved → Fulfilled → Closed
- **Return Request**: Requested → Approved/Partially Approved → Closed
- **Sale**: Completed → Refunded/Partially Refunded/Voided
- **Refund**: Initiated → Approved → Completed
- **Cash Remittance**: Submitted → Approved → Closed
- **Credit Account**: Active → Over Limit/Delinquent/Suspended

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (recommended) or SQLite (for development)
- Redis (for Celery)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd PoS
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Edit `.env` file with your configuration.

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Multi-Tenancy

The system supports multiple tenants with:
- Configurable terminology (Production, Store, Shop labels)
- Tenant-specific locations
- Role-based access control per location
- Tenant isolation via middleware

### Inventory Management

- **Append-only ledger**: All inventory changes are recorded immutably
- **Batch tracking**: Support for batch/expiry tracking
- **Stock balances**: Materialized view of current stock levels
- **Quantities tracked**: On-hand, Reserved, In-transit, Damaged

### Pricing & Costing

- Shop-specific product costs
- Price rules with priorities
- Margin rules with warnings/blocks
- Decoupled from batch costs

### Offline Mode

- Sales, receipts, and receiving work offline
- Sync on reconnection with conflict resolution
- Configurable per tenant

## API Documentation

Once the server is running, API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/`

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Code Style

The project follows PEP 8 style guidelines.

## License

[Your License Here]
