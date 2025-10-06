import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfileSection from './ProfileSection';
import { fetchCards } from '../services/api';
import * as authService from '../services/authService';

// Mock the API and auth service
jest.mock('../services/api');
jest.mock('../services/authService', () => ({
  validateToken: jest.fn(),
  refreshAccessToken: jest.fn(),
  updateUserProfile: jest.fn(),
  logout: jest.fn(),
  loginWithGoogle: jest.fn(),
  getCurrentUser: jest.fn(),
  tokenStorage: {
    getAccessToken: jest.fn(),
    setAccessToken: jest.fn(),
    getRefreshToken: jest.fn(),
    setRefreshToken: jest.fn(),
    clearTokens: jest.fn(),
  }
}));

const mockFetchCards = fetchCards as jest.MockedFunction<typeof fetchCards>;
const mockAuthService = authService as jest.Mocked<typeof authService>;

const mockCards = [
  {
    id: 1,
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/knight.png'
  },
  {
    id: 2,
    name: 'Wizard',
    elixir_cost: 5,
    rarity: 'Rare' as const,
    type: 'Troop' as const,
    image_url: 'https://example.com/wizard.png'
  }
];

const mockUser = {
  id: '1',
  googleId: 'google123',
  email: 'test@example.com',
  name: 'Test User',
  avatar: '1',
  createdAt: '2023-01-01T00:00:00Z',
  updatedAt: '2023-01-01T00:00:00Z'
};

// Mock AuthContext
const mockAuthContext = {
  user: mockUser,
  isLoading: false,
  isAuthenticated: true,
  login: jest.fn(),
  logout: jest.fn(),
  updateProfile: jest.fn(),
  refreshUser: jest.fn(),
};

jest.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => mockAuthContext,
}));

jest.mock('../contexts/OnboardingContext', () => ({
  OnboardingProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useOnboarding: () => ({
    isOnboardingComplete: true,
    currentStep: null,
    completeOnboarding: jest.fn(),
    resetOnboarding: jest.fn(),
  }),
}));

describe('AvatarSelector Integration with ProfileSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock auth service methods
    (mockAuthService.validateToken as jest.Mock).mockResolvedValue(mockUser);
    (mockAuthService.refreshAccessToken as jest.Mock).mockResolvedValue({ token: 'new-token', user: mockUser });
    (mockAuthService.updateUserProfile as jest.Mock).mockResolvedValue({ ...mockUser, avatar: '2' });
    (mockAuthService.logout as jest.Mock).mockResolvedValue(undefined);
    
    // Mock fetchCards
    mockFetchCards.mockResolvedValue(mockCards);
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn().mockReturnValue('mock-token'),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  const renderWithAuth = (component: React.ReactElement) => {
    return render(component);
  };

  it('should open avatar selector when change avatar button is clicked', async () => {
    renderWithAuth(<ProfileSection cards={mockCards} />);
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Click change avatar button
    const changeAvatarButton = screen.getByText('Change Avatar');
    fireEvent.click(changeAvatarButton);

    // Avatar selector should open
    await waitFor(() => {
      expect(screen.getByText('Choose Your Avatar')).toBeInTheDocument();
    });
  });

  it('should display cards in avatar selector', async () => {
    renderWithAuth(<ProfileSection cards={mockCards} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Open avatar selector
    const changeAvatarButton = screen.getByText('Change Avatar');
    fireEvent.click(changeAvatarButton);

    // Wait for avatar selector to load cards
    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
      expect(screen.getByText('Wizard')).toBeInTheDocument();
    });
  });

  it('should close avatar selector when close button is clicked', async () => {
    renderWithAuth(<ProfileSection cards={mockCards} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Open avatar selector
    const changeAvatarButton = screen.getByText('Change Avatar');
    fireEvent.click(changeAvatarButton);

    await waitFor(() => {
      expect(screen.getByText('Choose Your Avatar')).toBeInTheDocument();
    });

    // Close avatar selector
    const closeButton = screen.getByLabelText('Close avatar selector');
    fireEvent.click(closeButton);

    // Avatar selector should be closed
    await waitFor(() => {
      expect(screen.queryByText('Choose Your Avatar')).not.toBeInTheDocument();
    });
  });

  it('should call updateProfile when avatar is selected', async () => {
    renderWithAuth(<ProfileSection cards={mockCards} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Open avatar selector
    const changeAvatarButton = screen.getByText('Change Avatar');
    fireEvent.click(changeAvatarButton);

    await waitFor(() => {
      expect(screen.getByText('Wizard')).toBeInTheDocument();
    });

    // Select wizard card
    const wizardCard = screen.getByText('Wizard').closest('.avatar-selector__card');
    fireEvent.click(wizardCard!);

    // Should call updateUserProfile with new avatar
    await waitFor(() => {
      expect(mockAuthService.updateUserProfile).toHaveBeenCalledWith({ avatar: '2' });
    });
  });

  it('should filter cards by search term in avatar selector', async () => {
    renderWithAuth(<ProfileSection cards={mockCards} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Open avatar selector
    const changeAvatarButton = screen.getByText('Change Avatar');
    fireEvent.click(changeAvatarButton);

    await waitFor(() => {
      expect(screen.getByText('Knight')).toBeInTheDocument();
      expect(screen.getByText('Wizard')).toBeInTheDocument();
    });

    // Search for wizard
    const searchInput = screen.getByPlaceholderText('Search cards...');
    fireEvent.change(searchInput, { target: { value: 'wizard' } });

    // Only wizard should be visible
    expect(screen.getByText('Wizard')).toBeInTheDocument();
    expect(screen.queryByText('Knight')).not.toBeInTheDocument();
  });
});