import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * RedirectHandler component that manages automatic redirects based on authentication state
 */
const RedirectHandler: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Don't redirect while authentication is still loading
    if (isLoading) {
      return;
    }

    // Protected routes that require authentication
    const protectedRoutes = ['/saved-decks', '/profile'];
    const isProtectedRoute = protectedRoutes.some(route => 
      location.pathname.startsWith(route)
    );

    // If user is not authenticated and trying to access a protected route
    if (!isAuthenticated && isProtectedRoute) {
      // Store the intended destination for after login
      sessionStorage.setItem('redirectAfterLogin', location.pathname);
      navigate('/', { replace: true });
    }

    // If user is authenticated and we have a stored redirect path
    if (isAuthenticated) {
      const redirectPath = sessionStorage.getItem('redirectAfterLogin');
      if (redirectPath && redirectPath !== location.pathname) {
        sessionStorage.removeItem('redirectAfterLogin');
        navigate(redirectPath, { replace: true });
      }
    }
  }, [isAuthenticated, isLoading, location.pathname, navigate]);

  return null; // This component doesn't render anything
};

export default RedirectHandler;