import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: ({ element }: { element: React.ReactNode }) => <div>{element}</div>,
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => <a href={to}>{children}</a>,
  useNavigate: () => jest.fn(),
  Navigate: () => <div>Navigate</div>,
  useLocation: () => ({ pathname: '/' }),
}));

// Mock the auth service
jest.mock('../services/authService', () => ({
  validateToken: jest.fn().mockResolvedValue(null),
  loginWithGoogle: jest.fn(),
  logout: jest.fn(),
  updateUserProfile: jest.fn(),
}));

// Mock the API service
jest.mock('../services/api', () => ({
  verifyEndpoints: jest.fn().mockResolvedValue(true),
}));

// Mock Google Sign In Button to avoid external dependencies
jest.mock('./GoogleSignInButton', () => {
  return function MockGoogleSignInButton() {
    return <button>Sign in with Google</button>;
  };
});

describe('Navigation Integration', () => {
  beforeEach(() => {
    // Clear any stored session data
    sessionStorage.clear();
    localStorage.clear();
  });

  it('renders navigation with correct structure', async () => {
    render(<App />);
    
    // Check that the main title is present
    expect(screen.getByText('Clash Royale Deck Builder')).toBeInTheDocument();
    
    // Check that Deck Builder link is present
    expect(screen.getByText('Deck Builder')).toBeInTheDocument();
    
    // Check that sign in button is present for unauthenticated users
    expect(screen.getByText('Sign in with Google')).toBeInTheDocument();
  });

  it('shows appropriate navigation for unauthenticated users', async () => {
    render(<App />);
    
    // Should show Deck Builder
    expect(screen.getByText('Deck Builder')).toBeInTheDocument();
    
    // Should NOT show Saved Decks (protected route)
    expect(screen.queryByText('Saved Decks')).not.toBeInTheDocument();
    
    // Should show sign in button
    expect(screen.getByText('Sign in with Google')).toBeInTheDocument();
  });

  it('renders footer with creator attribution', () => {
    render(<App />);
    
    // Check that footer is present
    expect(screen.getByText(/Made with KIRO IDE by Levy Nunes/)).toBeInTheDocument();
  });
});