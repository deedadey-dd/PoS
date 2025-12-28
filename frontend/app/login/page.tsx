'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import apiClient from '@/lib/api/client';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

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
      
      // Get user roles to determine redirect (same logic as home page)
      try {
        const userResponse = await apiClient.get('/auth/users/me/');
        const user = userResponse.data;
        
        if (user.is_superuser || user.is_staff) {
          try {
            const tenantResponse = await apiClient.get('/auth/tenants/');
            const tenants = tenantResponse.data.results || tenantResponse.data;
            
            if (!tenants || tenants.length === 0) {
              router.push('/setup');
              return;
            }
            
            try {
              const rolesResponse = await apiClient.get(`/auth/user-location-roles/?user_id=${user.id}`);
              const roles = rolesResponse.data.results || rolesResponse.data;
              
              if (roles.length === 0) {
                router.push('/setup');
                return;
              }
              
              const hasShopAttendantRole = roles.some((r: any) => 
                r.role_code === 'shop_attendant' || 
                r.role_name?.toLowerCase().includes('attendant') ||
                r.role_name?.toLowerCase().includes('cashier')
              );
              
              if (hasShopAttendantRole) {
                router.push('/pos');
                return;
              }
            } catch {
              router.push('/setup');
              return;
            }
          } catch {
            router.push('/setup');
            return;
          }
        }
        
        try {
          const rolesResponse = await apiClient.get(`/auth/user-location-roles/?user_id=${user.id}`);
          const roles = rolesResponse.data.results || rolesResponse.data;
          
          if (roles.length > 0) {
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
        
        router.push('/dashboard');
      } catch {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            POS System
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                {...register('username')}
                type="text"
                autoComplete="username"
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                {...register('password')}
                type="password"
                autoComplete="current-password"
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Password"
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
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

