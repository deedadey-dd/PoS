'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';

export default function SetupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, checkAuth, isLoading } = useAuthStore();

  useEffect(() => {
    checkAuth().then(() => {
      if (!isAuthenticated && !isLoading) {
        router.push('/');
      }
    });
  }, [isAuthenticated, isLoading, checkAuth, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8">
        {children}
      </div>
    </div>
  );
}

