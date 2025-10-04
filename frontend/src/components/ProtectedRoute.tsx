import React, { ReactNode, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignInButton from './GoogleSignInButton';
import '../styles/ProtectedRoute.css';

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * ProtectedRoute component that renders children only if user is authenticated.
 * Shows a loading state while authentication is being checked.
 * Shows fallback component (or default sign-in message) if user is not authenticated.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  fallback 
}) => {
  const { isAuthenticated, isLoading } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="protected-route__loading">
        <div className="protected-route__loading-content">
          <div className="protected-route__spinner"></div>
          <p>Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Handle authentication success
  const handleAuthSuccess = () => {
    setAuthError(null);
    // Authentication state will be updated by AuthContext
  };

  // Handle authentication error
  const handleAuthError = (error: string) => {
    setAuthError(error);
  };

  // Show fallback or default sign-in message if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="protected-route__unauthenticated">
        {fallback || (
          <div className="protected-route__signin-prompt">
            <h2>Sign In Required</h2>
            <p>Please sign in with your Google account to access this feature.</p>
            <p className="protected-route__feature-info">
              This feature requires authentication to save and manage your personal data.
            </p>
            
            <div className="protected-route__signin-actions">
              <GoogleSignInButton
                onSuccess={handleAuthSuccess}
                onError={handleAuthError}
              />
              
              {authError && (
                <div className="protected-route__error">
                  <p className="protected-route__error-message">
                    {authError}
                  </p>
                </div>
              )}
            </div>
            
            <div className="protected-route__help">
              <p>
                <strong>Why sign in?</strong>
              </p>
              <ul>
                <li>Save your decks across devices</li>
                <li>Customize your profile with Clash Royale avatars</li>
                <li>Access your personal deck collection</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Render children if authenticated
  return <>{children}</>;
};

export default ProtectedRoute;