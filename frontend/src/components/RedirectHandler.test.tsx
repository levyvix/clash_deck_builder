import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RedirectHandler from './RedirectHandler';
import { AuthProvider } from '../contexts/AuthContext';

// Mock the auth service
jest.mock('../services/authService', () => ({
  validateToken: jest.fn(),
  loginWithGoogle: jest.fn(),
  logout: jest.fn(),
  updateUserProfile: jest.fn(),
}));

// Mock navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/test' }),
}));

describe('RedirectHandler', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          {component}
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders without crashing', () => {
    renderWithProviders(<RedirectHandler />);
  });

  it('does not render any visible content', () => {
    const { container } = renderWithProviders(<RedirectHandler />);
    expect(container.firstChild).toBeNull();
  });
});