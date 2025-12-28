# Project Structure

```
PoS/
├── pos_system/              # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Main settings file
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration
│
├── core/                    # Core multi-tenancy app
│   ├── models.py            # Tenant, Location, User, Role models
│   ├── admin.py             # Admin interfaces
│   ├── middleware.py        # Tenant middleware
│   └── urls.py              # Core URLs
│
├── inventory/               # Inventory management
│   ├── models.py            # Product, Batch, InventoryLedger, StockBalance
│   ├── admin.py             # Admin interfaces
│   ├── signals.py           # Signals for stock balance updates
│   └── urls.py              # Inventory URLs
│
├── transfers/               # Transfer and order management
│   ├── models.py            # Transfer, ShopOrder, ReturnRequest, Dispute
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Transfer URLs
│
├── sales/                   # POS and sales
│   ├── models.py            # Sale, Payment, Refund, Pricing, Credit
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Sales URLs
│
├── accounting/              # Accounting and remittance
│   ├── models.py            # CashUpReport, Remittance
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Accounting URLs
│
├── notifications/           # Notification system
│   ├── models.py            # Notification, NotificationLog, Template
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Notification URLs
│
├── analytics/               # Analytics and reporting
│   ├── models.py            # AnalyticsCache
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Analytics URLs
│
├── config/                  # Configuration management
│   ├── models.py            # SystemConfiguration, WorkflowConfiguration
│   ├── admin.py             # Admin interfaces
│   └── urls.py              # Config URLs
│
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore file
├── README.md                # Project README
└── setup_guide.md           # Setup instructions
```

## Model Relationships

### Core Models
- `Tenant` → `Location` (one-to-many)
- `Tenant` → `User` (one-to-many)
- `Tenant` → `Role` (one-to-many)
- `User` → `Location` → `Role` (many-to-many via `UserLocationRole`)

### Inventory Models
- `Tenant` → `Product` (one-to-many)
- `Product` → `Batch` (one-to-many)
- `Location` → `Product` → `Batch` → `InventoryLedger` (transactions)
- `Location` → `Product` → `Batch` → `StockBalance` (current state)

### Transfer Models
- `Tenant` → `Transfer` (one-to-many)
- `Location` → `Transfer` (from/to relationships)
- `Transfer` → `TransferItem` (one-to-many)
- `Tenant` → `ShopOrder` (one-to-many)
- `ShopOrder` → `ShopOrderItem` (one-to-many)
- `Tenant` → `ReturnRequest` (one-to-many)
- `ReturnRequest` → `ReturnItem` (one-to-many)
- `Transfer`/`ReturnRequest` → `Dispute` (optional)

### Sales Models
- `Tenant` → `Sale` (one-to-many)
- `Location` → `Sale` (shop)
- `User` → `Sale` (attendant)
- `Sale` → `SaleItem` (one-to-many)
- `Sale` → `Payment` (one-to-many)
- `Sale` → `Refund` (one-to-many)
- `Location` → `ShopProductCost` (one-to-many)
- `Location` → `PriceRule` (one-to-many)
- `Location` → `MarginRule` (one-to-many)
- `Tenant` → `Customer` (one-to-many)
- `Customer` → `CreditAccount` (one-to-one)
- `CreditAccount` → `CreditTransaction` (one-to-many)

### Accounting Models
- `Tenant` → `CashUpReport` (one-to-many)
- `Location` → `CashUpReport` (shop)
- `CashUpReport` → `Remittance` (one-to-many, optional)

## Key Design Patterns

1. **Multi-Tenancy**: All models include a `tenant` foreign key for data isolation
2. **State Machines**: Workflows use `django-fsm` for state management
3. **Append-Only Ledger**: Inventory changes recorded immutably in `InventoryLedger`
4. **Materialized Views**: `StockBalance` is updated from `InventoryLedger` via signals
5. **Audit Trail**: All critical operations can be logged using django-auditlog
6. **Configuration-Driven**: System behavior controlled via `SystemConfiguration` and `WorkflowConfiguration`

