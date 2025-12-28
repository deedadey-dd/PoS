'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Truck,
  DollarSign,
  Bell,
  BarChart3,
  Settings,
  Users,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth';
import { useRouter } from 'next/navigation';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Inventory', href: '/inventory', icon: Package },
  { name: 'POS', href: '/pos', icon: ShoppingCart },
  { name: 'Transfers', href: '/transfers', icon: Truck },
  { name: 'Accounting', href: '/accounting', icon: DollarSign },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="flex flex-col w-64 bg-gray-900 text-white">
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-800">
        <h1 className="text-xl font-bold">POS System</h1>
      </div>
      
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center px-4 py-2 mb-2">
          <div className="flex-1">
            <p className="text-sm font-medium text-white">{user?.username}</p>
            <p className="text-xs text-gray-400">{user?.tenant_name || 'No Tenant'}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center w-full px-4 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </button>
      </div>
    </div>
  );
}

