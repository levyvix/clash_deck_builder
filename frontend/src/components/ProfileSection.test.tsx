import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProfileSection from './ProfileSection';
import { AuthProvider } from '../contexts/AuthContext';
import { OnboardingProvider } from '../contexts/OnboardingContext';
import { User, Card } from '../types/index';

// Mock the auth service
jest.mock('../services/authService', () => ({
  updateUserProfile: jest.fn(),
  logout: jest.fn(),
}));

// Mock user data
const mockUser: User = {
  id: '1',
  googleId: 'google123',
  email: 'test@example.com',
  name: 'Test User',
  avatar: '1',
  createdAt: '2023-01-01T00:00:00Z',
  updatedAt: '2023-01-01T00:00:00Z',
};

// Mock cards data
const mockCards: Card[] = [
  {
    id: 1,
    name: 'Knight',
    elixir_cost: 3,
    rarity: 'Common',
    type: 'Troop',
    image_url: 'https://example.com/knight.png',
  },
  {
    id: 2,
    name: 'Fireball',
    elixir_cost: 4,
    rarity: 'Rare',
    type: 'Spell',
    image_url: 'https://example.com/fireball.png',
  },
];

// Mock AuthContext
let mockAuthContext = {
  user: mockUser,
  isLoading: false,
  isAuthenticated: true,
  login: jest.fn(),
  logout: jest.fn(),
  updateProfile: jest.fn(),
  refreshUser: jest.fn(),
};

const mockUseAuth = jest.fn(() => mockAuthContext);

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
    refreshOnboardingStatus: jest.fn(),
  }),
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <OnboardingProvider>
      {component}
    </OnboardingProvider>
  );
};

describe('ProfileSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders user information correctly', () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    expect(screen.getByText('Profile Settings')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('Change Avatar')).toBeInTheDocument();
    expect(screen.getByText('Log Out')).toBeInTheDocument();
  });

  it('displays avatar image when user has a valid avatar', () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const avatarImage = screen.getByAltText('Knight');
    expect(avatarImage).toBeInTheDocument();
    expect(avatarImage).toHaveAttribute('src', 'https://example.com/knight.png');
  });

  it('displays placeholder when user has no valid avatar', () => {
    const userWithoutAvatar = { ...mockUser, avatar: '999' };
    const contextWithoutAvatar = { ...mockAuthContext, user: userWithoutAvatar };
    
    mockUseAuth.mockReturnValueOnce(contextWithoutAvatar);
    
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    expect(screen.getByText('👤')).toBeInTheDocument();
  });

  it('allows editing display name', async () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('validates name input correctly', async () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    const nameInput = screen.getByDisplayValue('Test User');
    
    // Test empty name
    fireEvent.change(nameInput, { target: { value: '' } });
    fireEvent.click(screen.getByText('Save'));
    
    await waitFor(() => {
      expect(screen.getByText('Name cannot be empty')).toBeInTheDocument();
    });
    
    // Test invalid characters
    fireEvent.change(nameInput, { target: { value: 'Test@User!' } });
    fireEvent.click(screen.getByText('Save'));
    
    await waitFor(() => {
      expect(screen.getByText('Name can only contain letters, numbers, and spaces')).toBeInTheDocument();
    });
    
    // Test too long name
    fireEvent.change(nameInput, { target: { value: 'a'.repeat(51) } });
    fireEvent.click(screen.getByText('Save'));
    
    await waitFor(() => {
      expect(screen.getByText('Name must be 50 characters or less')).toBeInTheDocument();
    });
  });

  it('calls updateProfile when saving valid name', async () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    const nameInput = screen.getByDisplayValue('Test User');
    fireEvent.change(nameInput, { target: { value: 'New Name' } });
    fireEvent.click(screen.getByText('Save'));
    
    await waitFor(() => {
      expect(mockAuthContext.updateProfile).toHaveBeenCalledWith({ name: 'New Name' });
    });
  });

  it('cancels name editing when cancel button is clicked', () => {
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    const nameInput = screen.getByDisplayValue('Test User');
    fireEvent.change(nameInput, { target: { value: 'Changed Name' } });
    
    fireEvent.click(screen.getByText('Cancel'));
    
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.queryByDisplayValue('Changed Name')).not.toBeInTheDocument();
  });

  it('shows confirmation dialog and calls logout when logout button is clicked', async () => {
    // Mock window.confirm
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
    
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const logoutButton = screen.getByText('Log Out');
    fireEvent.click(logoutButton);
    
    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to log out?');
    await waitFor(() => {
      expect(mockAuthContext.logout).toHaveBeenCalled();
    });
    
    confirmSpy.mockRestore();
  });

  it('does not logout when confirmation is cancelled', () => {
    // Mock window.confirm to return false
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);
    
    renderWithProviders(<ProfileSection cards={mockCards} />);
    
    const logoutButton = screen.getByText('Log Out');
    fireEvent.click(logoutButton);
    
    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to log out?');
    expect(mockAuthContext.logout).not.toHaveBeenCalled();
    
    confirmSpy.mockRestore();
  });

  it('renders error state when no user is available', () => {
    const contextWithoutUser = {
      ...mockAuthContext,
      user: {
        id: '',
        googleId: '',
        email: '',
        name: '',
        avatar: '',
        createdAt: '',
        updatedAt: ''
      } as User,
      isAuthenticated: false
    };

    mockUseAuth.mockReturnValueOnce(contextWithoutUser);

    renderWithProviders(<ProfileSection cards={mockCards} />);

    expect(screen.getByText('No user information available. Please sign in again.')).toBeInTheDocument();
  });
});