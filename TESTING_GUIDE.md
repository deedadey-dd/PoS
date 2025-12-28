# API Testing Guide

## Quick Start

### 1. Get Authentication Token

```bash
# Get JWT token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }
```

### 2. Use Token in Requests

```bash
# Set token as environment variable
export TOKEN="your_access_token"

# Or use in curl
curl -X GET http://127.0.0.1:8000/api/inventory/products/ \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Endpoints

### Core Endpoints

#### Create Tenant
```bash
POST /api/auth/tenants/
{
  "name": "Test Company",
  "slug": "test-company",
  "currency": "USD",
  "timezone": "UTC"
}
```

#### Create Location
```bash
POST /api/auth/locations/
{
  "tenant": "tenant-id",
  "name": "Main Shop",
  "code": "SHOP001",
  "location_type": "shop",
  "city": "New York"
}
```

### Inventory Endpoints

#### Create Product
```bash
POST /api/inventory/products/
{
  "tenant": "tenant-id",
  "name": "Product A",
  "sku": "PROD-A-001",
  "unit_of_measure": "pcs",
  "track_batches": true
}
```

#### Create Batch
```bash
POST /api/inventory/batches/
{
  "tenant": "tenant-id",
  "product": "product-id",
  "batch_number": "BATCH-001",
  "production_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "quantity": 100,
  "bulk_price": 1000.00,
  "unit_cost": 10.00,
  "production_location": "location-id"
}
```

#### Check Low Stock
```bash
GET /api/inventory/stock-balances/low_stock/?threshold=10&location_id=shop-id
# Automatically sends notifications
```

### Sales Endpoints

#### Process Sale
```bash
POST /api/sales/sales/process/
{
  "tenant": "tenant-id",
  "shop": "shop-id",
  "items": [
    {
      "product": "product-id",
      "quantity": 2,
      "unit_price": 100.00,
      "discount_amount": 0
    }
  ],
  "payments": [
    {
      "payment_method": "cash",
      "amount": 200.00
    }
  ]
}
```

### Transfer Endpoints

#### Create Transfer
```bash
POST /api/transfers/transfers/
{
  "tenant": "tenant-id",
  "from_location": "store-id",
  "to_location": "shop-id",
  "items": [
    {
      "product": "product-id",
      "quantity_ordered": 10,
      "batch": "batch-id"
    }
  ]
}
```

#### Send Transfer
```bash
POST /api/transfers/transfers/{id}/send/
# Validates stock and moves to in-transit
# Sends notification
```

#### Receive Transfer
```bash
POST /api/transfers/transfers/{id}/receive/
{
  "received_items": {
    "item-id-1": 10,
    "item-id-2": 5
  }
}
# Supports partial receives
```

### Analytics Endpoints

#### Top Products
```bash
GET /api/analytics/top_products/?metric=profit&limit=10&start_date=2024-01-01
```

#### Profit & Loss
```bash
GET /api/analytics/profit_loss/?group_by=shop&start_date=2024-01-01&end_date=2024-12-31
```

#### Inventory Valuation
```bash
GET /api/analytics/inventory_valuation/?location_id=shop-id
```

### Notifications

#### Get Unread Notifications
```bash
GET /api/notifications/notifications/?is_read=false
```

#### Mark as Read
```bash
POST /api/notifications/notifications/{id}/mark_read/
```

#### Unread Count
```bash
GET /api/notifications/notifications/unread_count/
```

## Testing Permissions

### Test Role-Based Access

1. Create user with specific role
2. Assign to location
3. Try accessing endpoints
4. Verify access is granted/denied based on role

### Test Location-Based Access

1. Create user with role at Location A
2. Try accessing data for Location B
3. Verify access is denied

## Testing Validation

### Test Negative Stock

1. Set location `negative_stock_behavior` to 'block'
2. Try selling more than available stock
3. Verify error is returned

### Test Margin Rules

1. Create margin rule with `behavior='block'`
2. Try creating sale with price below margin
3. Verify error is returned

### Test Credit Limits

1. Create customer with credit limit
2. Try sale that exceeds limit
3. Verify error is returned

## Using Swagger UI

1. Navigate to: http://127.0.0.1:8000/api/docs/
2. Click "Authorize" button
3. Enter: `Bearer your_access_token`
4. Test endpoints directly in browser

## Postman Collection

Create a Postman collection with:
- Environment variables for token
- Pre-request scripts to refresh token
- Test scripts for validation

## Common Issues

### 401 Unauthorized
- Token expired - refresh token
- Token not included in header
- User not authenticated

### 403 Forbidden
- User doesn't have required role
- User not assigned to location
- Action not allowed for user's role

### 400 Bad Request
- Validation error
- Missing required fields
- Invalid data format

### 500 Internal Server Error
- Check server logs
- Verify database migrations
- Check for missing dependencies

