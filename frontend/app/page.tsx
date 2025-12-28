'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Home() {
  const router = useRouter();
  const { login, isLoading, isAuthenticated, checkAuth } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [companyName, setCompanyName] = useState<string>('POS System');

  // Fetch tenant name if available
  const { data: tenantData } = useQuery({
    queryKey: ['tenant-info'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/auth/tenants/');
        const tenants = response.data.results || response.data;
        if (tenants && tenants.length > 0) {
          return tenants[0];
        }
        return null;
      } catch {
        return null;
      }
    },
    enabled: !isAuthenticated,
  });

  useEffect(() => {
    if (tenantData?.name) {
      setCompanyName(tenantData.name);
    }
  }, [tenantData]);

  useEffect(() => {
    checkAuth().then(() => {
      if (isAuthenticated) {
        // Redirect will be handled by login function
      }
    });
  }, [isAuthenticated, checkAuth]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      setError(null);
      await login(data.username, data.password);
      
      // Ensure token is in localStorage before making requests
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication failed. Please try again.');
        return;
      }
      
      // Small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Get user roles to determine redirect
      try {
        const userResponse = await apiClient.get('/auth/users/me/');
        const user = userResponse.data;
        
        console.log('User data:', user); // Debug log
        
        // Check if user is superuser/admin
        if (user.is_superuser || user.is_staff) {
          console.log('User is admin/superuser'); // Debug log
          
          // Check if tenant is set up
          try {
            // Verify token is still available
            const currentToken = localStorage.getItem('access_token');
            console.log('Token available:', !!currentToken); // Debug log
            console.log('Token value:', currentToken ? currentToken.substring(0, 20) + '...' : 'none'); // Debug log
            
            const tenantResponse = await apiClient.get('/auth/tenants/', {
              headers: {
                Authorization: `Bearer ${currentToken}`,
              },
            });
            const tenants = tenantResponse.data.results || tenantResponse.data;
            
            console.log('Tenants:', tenants); // Debug log
            
            // Check if no tenants exist or empty array
            // Handle both array and object responses
            const tenantList = Array.isArray(tenants) ? tenants : (tenants?.results || []);
            if (!tenantList || tenantList.length === 0) {
              console.log('No tenants found, redirecting to setup'); // Debug log
              router.push('/setup');
              return;
            }
            
            // Check if user has any location-role assignments
            try {
              const rolesResponse = await apiClient.get(`/auth/user-location-roles/?user_id=${user.id}`);
              const roles = rolesResponse.data.results || rolesResponse.data;
              
              console.log('User roles:', roles); // Debug log
              
              // Handle both array and object responses
              const roleList = Array.isArray(roles) ? roles : (roles?.results || []);
              if (!roleList || roleList.length === 0) {
                console.log('No roles found, redirecting to setup'); // Debug log
                router.push('/setup');
                return;
              }
              
              // Check for shop attendant role
              const hasShopAttendantRole = roles.some((r: any) => 
                r.role_code === 'shop_attendant' || 
                r.role_name?.toLowerCase().includes('attendant') ||
                r.role_name?.toLowerCase().includes('cashier')
              );
              
              if (hasShopAttendantRole) {
                console.log('User has shop attendant role, redirecting to POS'); // Debug log
                router.push('/pos');
                return;
              }
            } catch (rolesError) {
              console.error('Error fetching roles:', rolesError); // Debug log
              // If can't get roles, go to setup
              router.push('/setup');
              return;
            }
            } catch (tenantError: any) {
            console.error('Error fetching tenants:', tenantError); // Debug log
            console.error('Error status:', tenantError.response?.status); // Debug log
            console.error('Error data:', tenantError.response?.data); // Debug log
            
            // If 401 or 403, or if no tenants exist, go to setup
            if (tenantError.response?.status === 401 || tenantError.response?.status === 403) {
              console.log('Unauthorized/Forbidden - redirecting to setup'); // Debug log
              router.push('/setup');
              return;
            }
            
            // For other errors, also go to setup (assume no tenant exists)
            router.push('/setup');
            return;
          }
        }
        
        // For non-superusers, check their roles
        try {
          const rolesResponse = await apiClient.get(`/auth/user-location-roles/?user_id=${user.id}`);
          const roles = rolesResponse.data.results || rolesResponse.data;
          
          if (roles && roles.length > 0) {
            const hasShopAttendantRole = roles.some((r: any) => 
              r.role_code === 'shop_attendant' || 
              r.role_name?.toLowerCase().includes('attendant') ||
              r.role_name?.toLowerCase().includes('cashier')
            );
            
            if (hasShopAttendantRole) {
              router.push('/pos');
              return;
            }
          }
        } catch {
          // Continue to default
        }
        
        // Default to dashboard
        console.log('Default redirect to dashboard'); // Debug log
        router.push('/dashboard');
      } catch (userError) {
        console.error('Error fetching user:', userError); // Debug log
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    }
  };

  if (isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
            Welcome to
          </h1>
          <h2 className="text-5xl font-bold text-primary-600 mb-8">
            {companyName}
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Sign in to access your account
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-800">{error}</div>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  {...register('username')}
                  type="text"
                  autoComplete="username"
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your username"
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
                )}
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  {...register('password')}
                  type="password"
                  autoComplete="current-password"
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                  placeholder="Enter your password"
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
