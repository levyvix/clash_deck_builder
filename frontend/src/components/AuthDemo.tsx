import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignInButton from './GoogleSignInButton';

/**
 * Demo component to test Google Sign-In functionality
 * This is a temporary component for testing purposes
 */
const AuthDemo: React.FC = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  const handleSignInSuccess = () => {
    console.log('Sign-in successful!');
  };

  const handleSignInError = (error: string) => {
    console.error('Sign-in error:', error);
  };

  const handleLogout = async () => {
    try {
      await logout();
      console.log('Logout successful!');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Loading...</h2>
        <p>Checking authentication status...</p>
      </div>
    );
  }

  if (isAuthenticated && user) {
    return (
      <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
        <h2>Welcome, {user.name}!</h2>
        <div style={{ marginBottom: '1rem' }}>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Google ID:</strong> {user.googleId}</p>
          <p><strong>Avatar:</strong> {user.avatar}</p>
          <p><strong>Member since:</strong> {new Date(user.createdAt).toLocaleDateString()}</p>
        </div>
        <button 
          onClick={handleLogout}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Sign Out
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
      <h2>Authentication Demo</h2>
      <p>Sign in with your Google account to test the authentication flow.</p>
      <div style={{ marginTop: '2rem' }}>
        <GoogleSignInButton
          onSuccess={handleSignInSuccess}
          onError={handleSignInError}
        />
      </div>
    </div>
  );
};

export default AuthDemo;