import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';

/**
 * Hook that provides authentication-aware API utilities
 * Automatically handles token refresh and logout on auth failures
 */
export const useAuthenticatedApi = () => {
  const { isAuthenticated, logout, refreshUser } = useAuth();

  // Handle API errors that might indicate authentication issues
  const handleApiError = async (error: any) => {
    if (error?.statusCode === 401) {
      // Token expired or invalid, try to refresh user data
      try {
        await refreshUser();
      } catch (refreshError) {
        // Refresh failed, logout user
        await logout();
      }
    }
  };

  return {
    isAuthenticated,
    handleApiError,
  };
};