# Schema Generation Fixes

## Issues Fixed

### 1. AnalyticsViewSet Serializer Warning ✅
**Issue**: `unable to guess serializer` for AnalyticsViewSet

**Fix**: Added `serializer_class = None` since analytics endpoints return custom data structures, not model instances.

### 2. StockBalanceSerializer Property Warning ✅
**Issue**: `unable to resolve type hint for function "available_quantity"`

**Fix**: Added explicit `available_quantity` field to serializer with proper type:
```python
available_quantity = serializers.DecimalField(max_digits=15, decimal_places=3, read_only=True)
```

### 3. NotificationViewSet Queryset Warning ✅
**Issue**: `Failed to obtain model through view's queryset` due to AnonymousUser

**Fix**: Added `swagger_fake_view` check in `get_queryset()`:
```python
if getattr(self, 'swagger_fake_view', False):
    return Notification.objects.none()
```

### 4. CreditAccountSerializer Property Warning ✅
**Issue**: `unable to resolve type hint for function "available_credit"`

**Fix**: Added explicit `available_credit` field to serializer:
```python
available_credit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
```

### 5. NotificationViewSet Path Parameter Warning ✅
**Issue**: `could not derive type of path parameter "id"`

**Fix**: The swagger_fake_view fix also resolves this by providing a proper queryset for schema generation.

## Result

All schema generation warnings should now be resolved. The Swagger/OpenAPI documentation will generate cleanly without warnings.

## Testing

1. Access Swagger UI: `http://127.0.0.1:8000/api/docs/`
2. Check that all endpoints appear correctly
3. Verify no warnings in server logs when accessing `/api/schema/`

