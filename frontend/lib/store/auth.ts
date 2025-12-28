import { create } from 'zustand';
import apiClient from '../api/client';

interface User {
    id: number;
    username: string;
    email: string;
    is_superuser: boolean;
    is_staff: boolean;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,

    login: async (username, password) => {
        set({ isLoading: true });
        try {
            const response = await apiClient.post('/auth/token/', { username, password });
            const { access, refresh } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);

            const userResponse = await apiClient.get('/auth/users/me/');
            set({
                user: userResponse.data,
                isAuthenticated: true,
                isLoading: false
            });
        } catch (error) {
            set({ isLoading: false });
            throw error;
        }
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
    },

    checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            set({ isAuthenticated: false });
            return;
        }

        try {
            const response = await apiClient.get('/auth/users/me/');
            set({
                user: response.data,
                isAuthenticated: true
            });
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            set({ user: null, isAuthenticated: false });
        }
    },
}));
