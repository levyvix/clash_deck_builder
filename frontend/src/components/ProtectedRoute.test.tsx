import React from 'react';
import { render, screen } from '@testing-library/react';
import ProtectedRoute from './ProtectedRoute';
import { AuthProvider } from '../contexts/AuthContext';
import * as authService from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Mock child component
const TestChild: React.FC = () => <div>Protected Content</div>;

// Helper to render ProtectedRoute with AuthProvider
const renderProtectedRoute = (children: React.ReactNode, fallback?: React.ReactNode) => {
  return render(
    <AuthProvider>
      <ProtectedRoute fallback={fallback}>
        {children}
      </ProtectedRoute>
    </AuthProvider>
  );
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should show loading state while checking authentication', () => {
    // Mock validateToken to never resolve (simulating loading)
    mockedAuthService.validateToken.mockImplementation(() => new Promise(() => {}));
    
    renderProtectedRoute(<TestChild />);
    
    expect(screen.getByText('Checking authentication...')).toBeInTheDocument();
  });

  it('should show default sign-in prompt when not authenticated', async () => {
    mockedAuthService.validateToken.mockResolvedValue(null);
    
    renderProtectedRoute(<TestChild />);
    
    await screen.findByText('Sign In Required');
    expect(screen.getByText('Please sign in with your Google account to access this feature.')).toBeInTheDocument();
  });

  it('should show custom fallback when not authenticated', async () => {
    mockedAuthService.validateToken.mockResolvedValue(null);
    
    const customFallback = <div>Custom Sign In Message</div>;
    renderProtectedRoute(<TestChild />, customFallback);
    
    await screen.findByText('Custom Sign In Message');
    expect(screen.queryByText('Sign In Required')).not.toBeInTheDocument();
  });

  it('should render children when authenticated', async () => {
    const mockUser = {
      id: '1',
      googleId: 'google123',
      email: 'test@example.com',
      name: 'Test User',
      avatar: 'knight',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    };
    
    mockedAuthService.validateToken.mockResolvedValue(mockUser);
    
    renderProtectedRoute(<TestChild />);
    
    await screen.findByText('Protected Content');
    expect(screen.queryByText('Sign In Required')).not.toBeInTheDocument();
  });
});