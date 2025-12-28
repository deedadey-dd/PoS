'use client';

import { Bell } from 'lucide-react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store/auth';

export function Header() {
  const { user } = useAuthStore();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            {user?.tenant_name || 'POS System'}
          </h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <Link
            href="/notifications"
            className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
          >
            <Bell className="h-6 w-6" />
            <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
          </Link>
          
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.username}</p>
              <p className="text-xs text-gray-500">{user?.first_name} {user?.last_name}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

