'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';
import { formatCurrency } from '@/lib/utils';
import { Package, ShoppingCart, DollarSign, TrendingUp } from 'lucide-react';

interface DashboardStats {
  total_products: number;
  total_sales: number;
  total_revenue: number;
  low_stock_items: number;
}

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // This would be a custom endpoint, for now we'll use placeholder
      // In production, create a dashboard stats endpoint in Django
      return {
        total_products: 0,
        total_sales: 0,
        total_revenue: 0,
        low_stock_items: 0,
      };
    },
  });

  const statCards = [
    {
      name: 'Total Products',
      value: stats?.total_products || 0,
      icon: Package,
      color: 'bg-blue-500',
    },
    {
      name: 'Total Sales',
      value: stats?.total_sales || 0,
      icon: ShoppingCart,
      color: 'bg-green-500',
    },
    {
      name: 'Total Revenue',
      value: formatCurrency(stats?.total_revenue || 0),
      icon: DollarSign,
      color: 'bg-purple-500',
    },
    {
      name: 'Low Stock Items',
      value: stats?.low_stock_items || 0,
      icon: TrendingUp,
      color: 'bg-red-500',
    },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      {isLoading ? (
        <div className="animate-pulse">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow p-6 h-32"></div>
            ))}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {statCards.map((stat) => (
            <div
              key={stat.name}
              className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Sales</h2>
          <p className="text-gray-500">Recent sales will appear here</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Low Stock Alerts</h2>
          <p className="text-gray-500">Low stock items will appear here</p>
        </div>
      </div>
    </div>
  );
}

