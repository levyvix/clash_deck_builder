import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import GoogleSignInButton from './GoogleSignInButton';
import { AuthProvider } from '../contexts/AuthContext';
import * as authService from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Mock Google Identity Services
const mockGoogleAccounts = {
  id: {
    initialize: jest.fn(),
    renderButton: jest.fn(),
    prompt: jest.fn(),
  },
};

// Helper to render GoogleSignInButton with all required providers
const renderGoogleSignInButton = (props = {}) => {
  return render(
    <GoogleOAuthProvider clientId="test-client-id.apps.googleusercontent.com">
      <AuthProvider>
        <GoogleSignInButton {...props} />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

describe('GoogleSignInButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock window.google
    Object.defineProperty(window, 'google', {
      value: {
        accounts: mockGoogleAccounts,
      },
      writable: true,
    });
    
    // Mock environment variable
    process.env.REACT_APP_GOOGLE_CLIENT_ID = 'test-client-id.apps.googleusercontent.com';
    
    // Mock validateToken to return null (not authenticated)
    mockedAuthService.validateToken.mockResolvedValue(null);
  });

  afterEach(() => {
    delete (window as any).google;
    delete process.env.REACT_APP_GOOGLE_CLIENT_ID;
  });

  it('should render GoogleSignInButton component', async () => {
    renderGoogleSignInButton();
    
    // Component should render without crashing - look for the button container
    await waitFor(() => {
      const container = document.querySelector('.google-signin-button');
      expect(container).toBeInTheDocument();
    });
  });

  it('should show loading state when auth context is loading', () => {
    // Mock auth context to be in loading state
    mockedAuthService.validateToken.mockImplementation(() => new Promise(() => {}));
    
    renderGoogleSignInButton();
    
    expect(screen.getByText('Signing in...')).toBeInTheDocument();
  });

  it('should render button container when not loading', async () => {
    renderGoogleSignInButton();
    
    // Wait for auth context to resolve and button to appear
    await waitFor(() => {
      const container = document.querySelector('.google-signin-button');
      expect(container).toBeInTheDocument();
    });
  });
});