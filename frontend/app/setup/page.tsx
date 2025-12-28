'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Building2, Users, MapPin, Save } from 'lucide-react';

const tenantSchema = z.object({
  name: z.string().min(1, 'Company name is required'),
  slug: z.string().min(1, 'Slug is required').regex(/^[a-z0-9-]+$/, 'Slug must be lowercase alphanumeric with hyphens'),
  currency: z.string().length(3, 'Currency must be 3 characters'),
  timezone: z.string().min(1, 'Timezone is required'),
});

const userSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
});

type TenantForm = z.infer<typeof tenantSchema>;
type UserForm = z.infer<typeof userSchema>;

export default function SetupPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'tenant' | 'users'>('tenant');
  const [createdTenantId, setCreatedTenantId] = useState<string | null>(null);

  // Check if tenant exists
  const { data: existingTenant } = useQuery({
    queryKey: ['tenant'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/auth/tenants/');
        const tenants = response.data.results || response.data;
        return tenants && tenants.length > 0 ? tenants[0] : null;
      } catch {
        return null;
      }
    },
  });

  const tenantForm = useForm<TenantForm>({
    resolver: zodResolver(tenantSchema),
    defaultValues: {
      currency: 'USD',
      timezone: 'UTC',
    },
  });

  const userForm = useForm<UserForm>({
    resolver: zodResolver(userSchema),
  });

  // Create tenant mutation
  const createTenantMutation = useMutation({
    mutationFn: async (data: TenantForm) => {
      const response = await apiClient.post('/auth/tenants/', data);
      return response.data;
    },
    onSuccess: (data) => {
      setCreatedTenantId(data.id);
      queryClient.invalidateQueries({ queryKey: ['tenant'] });
      setActiveTab('users');
    },
  });

  // Create user mutation
  const createUserMutation = useMutation({
    mutationFn: async (data: UserForm & { tenant: string }) => {
      const response = await apiClient.post('/auth/users/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      userForm.reset();
      alert('User created successfully!');
    },
  });

  const onTenantSubmit = (data: TenantForm) => {
    createTenantMutation.mutate(data);
  };

  const onUserSubmit = (data: UserForm) => {
    const tenantId = createdTenantId || existingTenant?.id;
    if (!tenantId) {
      alert('Please create a tenant first');
      return;
    }
    createUserMutation.mutate({ ...data, tenant: tenantId });
  };

  if (existingTenant && !createdTenantId) {
    setCreatedTenantId(existingTenant.id);
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Initial Setup</h1>
        <p className="text-gray-600">Configure your organization and add users</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('tenant')}
            className={`${
              activeTab === 'tenant'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
          >
            <Building2 className="h-5 w-5 mr-2" />
            Organization
          </button>
          <button
            onClick={() => setActiveTab('users')}
            disabled={!createdTenantId && !existingTenant}
            className={`${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Users className="h-5 w-5 mr-2" />
            Add Users
          </button>
        </nav>
      </div>

      {/* Tenant Setup */}
      {activeTab === 'tenant' && (
        <div className="bg-white rounded-lg shadow p-6">
          {existingTenant ? (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800">
                <strong>Organization already set up:</strong> {existingTenant.name}
              </p>
            </div>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Create Organization</h2>
              <form onSubmit={tenantForm.handleSubmit(onTenantSubmit)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name *
                  </label>
                  <input
                    {...tenantForm.register('name')}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Your Company Name"
                  />
                  {tenantForm.formState.errors.name && (
                    <p className="mt-1 text-sm text-red-600">
                      {tenantForm.formState.errors.name.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Slug * (lowercase, no spaces)
                  </label>
                  <input
                    {...tenantForm.register('slug')}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="company-name"
                  />
                  {tenantForm.formState.errors.slug && (
                    <p className="mt-1 text-sm text-red-600">
                      {tenantForm.formState.errors.slug.message}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Currency *
                    </label>
                    <select
                      {...tenantForm.register('currency')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="KES">KES</option>
                      <option value="NGN">NGN</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Timezone *
                    </label>
                    <input
                      {...tenantForm.register('timezone')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="UTC"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={createTenantMutation.isPending}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Save className="h-5 w-5 mr-2" />
                  {createTenantMutation.isPending ? 'Creating...' : 'Create Organization'}
                </button>
              </form>
            </>
          )}
        </div>
      )}

      {/* Users Setup */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Users</h2>
          <form onSubmit={userForm.handleSubmit(onUserSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <input
                  {...userForm.register('first_name')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {userForm.formState.errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">
                    {userForm.formState.errors.first_name.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <input
                  {...userForm.register('last_name')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {userForm.formState.errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">
                    {userForm.formState.errors.last_name.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username *
              </label>
              <input
                {...userForm.register('username')}
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              {userForm.formState.errors.username && (
                <p className="mt-1 text-sm text-red-600">
                  {userForm.formState.errors.username.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                {...userForm.register('email')}
                type="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              {userForm.formState.errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {userForm.formState.errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password *
              </label>
              <input
                {...userForm.register('password')}
                type="password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              {userForm.formState.errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {userForm.formState.errors.password.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={createUserMutation.isPending || (!createdTenantId && !existingTenant)}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createUserMutation.isPending ? 'Creating...' : 'Create User'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

