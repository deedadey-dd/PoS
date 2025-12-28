from .models import Tenant


class TenantMiddleware:
    """Middleware to set current tenant in request"""
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract tenant from subdomain, header, or user
        tenant = None
        
        # Try to get from subdomain
        host = request.get_host().split(':')[0]
        if host:
            try:
                tenant = Tenant.objects.get(domain=host, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Try to get from header
        if not tenant:
            tenant_header = request.headers.get('X-Tenant-ID')
            if tenant_header:
                try:
                    tenant = Tenant.objects.get(id=tenant_header, is_active=True)
                except (Tenant.DoesNotExist, ValueError):
                    pass
        
        # Try to get from authenticated user
        if not tenant and request.user.is_authenticated:
            tenant = request.user.tenant
        
        request.tenant = tenant
        response = self.get_response(request)
        return response
