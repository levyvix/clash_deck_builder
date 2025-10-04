import React, { useState } from 'react';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import { GoogleUserInfo } from '../types';
import '../styles/GoogleSignInButton.css';

interface GoogleSignInButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  migrationData?: any;
}

const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  onSuccess,
  onError,
  disabled = false,
  migrationData
}) => {
  const { login, isLoading } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  // Handle successful Google authentication
  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    try {
      setAuthError(null);
      
      if (!credentialResponse.credential) {
        throw new Error('No credential received from Google');
      }

      // Decode the JWT token to get user info
      const payload = JSON.parse(atob(credentialResponse.credential.split('.')[1]));
      
      const userInfo: GoogleUserInfo = {
        sub: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
      };

      // Use the credential as the auth code for backend verification
      await login(credentialResponse.credential, userInfo, migrationData);
      
      onSuccess?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      setAuthError(errorMessage);
      onError?.(errorMessage);
      console.error('Google Sign-In error:', error);
    }
  };

  // Handle Google authentication error
  const handleGoogleError = () => {
    const errorMsg = 'Google Sign-In failed';
    setAuthError(errorMsg);
    onError?.(errorMsg);
  };

  // Handle retry button click
  const handleRetry = () => {
    setAuthError(null);
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="google-signin-button google-signin-button--loading">
        <div className="google-signin-button__spinner"></div>
        <span>Signing in...</span>
      </div>
    );
  }

  // Show error state
  if (authError) {
    return (
      <div className="google-signin-button google-signin-button--error">
        <div className="google-signin-button__error-content">
          <span className="google-signin-button__error-icon">⚠️</span>
          <div className="google-signin-button__error-text">
            <p className="google-signin-button__error-message">{authError}</p>
            <button 
              className="google-signin-button__retry-btn md-button md-button--text"
              onClick={handleRetry}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`google-signin-button ${disabled ? 'google-signin-button--disabled' : ''}`}>
      {disabled ? (
        <div className="google-signin-button__disabled-placeholder">
          <span>Sign in with Google</span>
        </div>
      ) : (
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          theme="outline"
          size="large"
          text="signin_with"
          shape="rectangular"
          logo_alignment="left"
          width="280"
        />
      )}
    </div>
  );
};

export default GoogleSignInButton;