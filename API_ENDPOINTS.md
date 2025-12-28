# API Endpoints Documentation

## Base URL
All API endpoints are prefixed with `/api/`

## Authentication
- **Token Endpoint**: `POST /api/auth/token/`
- **Token Refresh**: `POST /api/auth/token/refresh/`

## Core Endpoints (`/api/auth/`)

### Tenants
- `GET /api/auth/tenants/` - List tenants
- `POST /api/auth/tenants/` - Create tenant
- `GET /api/auth/tenants/{id}/` - Get tenant
- `PUT /api/auth/tenants/{id}/` - Update tenant
- `DELETE /api/auth/tenants/{id}/` - Delete tenant

### Locations
- `GET /api/auth/locations/` - List locations
- `POST /api/auth/locations/` - Create location
- `GET /api/auth/locations/{id}/` - Get location
- `PUT /api/auth/locations/{id}/` - Update location
- `DELETE /api/auth/locations/{id}/` - Delete location

### Users
- `GET /api/auth/users/` - List users
- `POST /api/auth/users/` - Create user
- `GET /api/auth/users/me/` - Get current user
- `GET /api/auth/users/{id}/` - Get user
- `PUT /api/auth/users/{id}/` - Update user
- `DELETE /api/auth/users/{id}/` - Delete user

### Roles
- `GET /api/auth/roles/` - List roles
- `POST /api/auth/roles/` - Create role
- `GET /api/auth/roles/{id}/` - Get role
- `PUT /api/auth/roles/{id}/` - Update role
- `DELETE /api/auth/roles/{id}/` - Delete role

### User Location Roles
- `GET /api/auth/user-location-roles/` - List assignments
- `POST /api/auth/user-location-roles/` - Create assignment
- `GET /api/auth/user-location-roles/by_user/?user_id={id}` - Get by user
- `GET /api/auth/user-location-roles/by_location/?location_id={id}` - Get by location

## Inventory Endpoints (`/api/inventory/`)

### Products
- `GET /api/inventory/products/` - List products
- `POST /api/inventory/products/` - Create product
- `GET /api/inventory/products/{id}/` - Get product
- `GET /api/inventory/products/{id}/stock_balances/` - Get stock balances
- `GET /api/inventory/products/{id}/ledger/` - Get ledger entries

### Batches
- `GET /api/inventory/batches/` - List batches
- `POST /api/inventory/batches/` - Create batch
- `GET /api/inventory/batches/{id}/stock_balances/` - Get stock balances

### Stock Balances
- `GET /api/inventory/stock-balances/` - List stock balances
- `GET /api/inventory/stock-balances/low_stock/?threshold=10` - Get low stock
- `GET /api/inventory/stock-balances/by_location/?location_id={id}` - Get by location

### Inventory Ledger
- `GET /api/inventory/ledger/` - List ledger entries (read-only)

### Expiry Alerts
- `GET /api/inventory/expiry-alerts/` - List alerts
- `GET /api/inventory/expiry-alerts/upcoming/?days=30` - Get upcoming expiries

## Transfers Endpoints (`/api/transfers/`)

### Transfers
- `GET /api/transfers/transfers/` - List transfers
- `POST /api/transfers/transfers/` - Create transfer
- `GET /api/transfers/transfers/{id}/` - Get transfer
- `POST /api/transfers/transfers/{id}/send/` - Send transfer
- `POST /api/transfers/transfers/{id}/receive/` - Receive transfer
- `POST /api/transfers/transfers/{id}/dispute/` - Dispute transfer

### Shop Orders
- `GET /api/transfers/shop-orders/` - List orders
- `POST /api/transfers/shop-orders/` - Create order
- `POST /api/transfers/shop-orders/{id}/submit/` - Submit order
- `POST /api/transfers/shop-orders/{id}/approve/` - Approve order
- `POST /api/transfers/shop-orders/{id}/fulfill/` - Fulfill order
- `POST /api/transfers/shop-orders/{id}/cancel/` - Cancel order

### Return Requests
- `GET /api/transfers/return-requests/` - List returns
- `POST /api/transfers/return-requests/` - Create return
- `POST /api/transfers/return-requests/{id}/approve/` - Approve return
- `POST /api/transfers/return-requests/{id}/dispute/` - Dispute return

## Sales Endpoints (`/api/sales/`)

### Sales
- `GET /api/sales/sales/` - List sales
- `POST /api/sales/sales/` - Create sale
- `GET /api/sales/sales/{id}/` - Get sale
- `POST /api/sales/sales/{id}/refund/` - Process refund

### Shifts
- `GET /api/sales/shifts/` - List shifts
- `POST /api/sales/shifts/` - Create shift
- `POST /api/sales/shifts/{id}/close/` - Close shift

### Customers & Credit
- `GET /api/sales/customers/` - List customers
- `POST /api/sales/customers/` - Create customer
- `GET /api/sales/credit-accounts/` - List credit accounts
- `GET /api/sales/credit-accounts/{id}/transactions/` - Get transactions

## Accounting Endpoints (`/api/accounting/`)

### Cash Up Reports
- `GET /api/accounting/cash-up-reports/` - List reports
- `POST /api/accounting/cash-up-reports/` - Create report
- `POST /api/accounting/cash-up-reports/{id}/submit/` - Submit report
- `POST /api/accounting/cash-up-reports/{id}/approve/` - Approve report

### Remittances
- `GET /api/accounting/remittances/` - List remittances
- `POST /api/accounting/remittances/` - Create remittance
- `POST /api/accounting/remittances/{id}/approve/` - Approve remittance

## Filtering & Search

All list endpoints support:
- **Filtering**: `?field=value&field2=value2`
- **Search**: `?search=term` (searches in search_fields)
- **Ordering**: `?ordering=field` or `?ordering=-field` (descending)
- **Pagination**: `?page=1&page_size=50`

## Response Format

All responses are in JSON format:
```json
{
  "count": 100,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

