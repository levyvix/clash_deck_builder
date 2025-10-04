import { API_BASE_URL, GOOGLE_CLIENT_ID } from '../config';
import { AuthResponse, GoogleUserInfo, User } from '../types';

// Custom error class for authentication errors
export class AuthError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public isNetworkError: boolean = false
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

// Token storage keys
const ACCESS_TOKEN_KEY = 'clash_deck_builder_token';
const REFRESH_TOKEN_KEY = 'clash_deck_builder_refresh_token';

// Token storage utilities
export const tokenStorage = {
  getAccessToken: (): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  
  setAccessToken: (token: string): void => {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },
  
  setRefreshToken: (token: string): void => {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  },
  
  clearTokens: (): void => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
};

// Enhanced fetch with authentication
const authFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = tokenStorage.getAccessToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    return response;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new AuthError('Cannot connect to server', undefined, true);
    }
    throw error;
  }
};

// Handle API response and extract error messages
const handleAuthResponse = async (response: Response): Promise<any> => {
  if (!response.ok) {
    let errorMessage = 'An error occurred';
    
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    
    if (response.status === 401) {
      throw new AuthError('Authentication failed', response.status);
    } else if (response.status === 403) {
      throw new AuthError('Access denied', response.status);
    } else if (response.status === 400) {
      throw new AuthError(errorMessage, response.status);
    } else if (response.status >= 500) {
      throw new AuthError('Server error, please try again', response.status);
    } else {
      throw new AuthError(errorMessage, response.status);
    }
  }
  
  return response.json();
};

// Google OAuth login
export const loginWithGoogle = async (idToken: string, userInfo: GoogleUserInfo, migrationData?: any): Promise<AuthResponse> => {
  try {
    console.log('🔐 Authenticating with Google OAuth...');
    
    const response = await authFetch(`${API_BASE_URL}/api/auth/google`, {
      method: 'POST',
      body: JSON.stringify({
        id_token: idToken,
        migration_data: migrationData
      }),
    });
    
    const data = await handleAuthResponse(response);
    
    // Store tokens
    tokenStorage.setAccessToken(data.access_token);
    if (data.refresh_token) {
      tokenStorage.setRefreshToken(data.refresh_token);
    }
    
    console.log('✅ Authentication successful');
    return data;
  } catch (error) {
    console.error('❌ Authentication failed:', error);
    throw error;
  }
};

// Refresh access token
export const refreshAccessToken = async (): Promise<AuthResponse> => {
  try {
    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new AuthError('No refresh token available', 401);
    }
    
    console.log('🔄 Refreshing access token...');
    
    const response = await authFetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: refreshToken
      }),
    });
    
    const data = await handleAuthResponse(response);
    
    // Update stored token
    tokenStorage.setAccessToken(data.access_token);
    // Refresh token stays the same, don't update it
    
    console.log('✅ Token refreshed successfully');
    return data;
  } catch (error) {
    console.error('❌ Token refresh failed:', error);
    // Clear tokens on refresh failure
    tokenStorage.clearTokens();
    throw error;
  }
};

// Logout
export const logout = async (): Promise<void> => {
  try {
    console.log('🚪 Logging out...');
    
    const response = await authFetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      console.warn('Logout request failed, but clearing local tokens anyway');
    }
    
    console.log('✅ Logout successful');
  } catch (error) {
    console.warn('Logout request failed, but clearing local tokens anyway:', error);
  } finally {
    // Always clear tokens regardless of API response
    tokenStorage.clearTokens();
  }
};

// Get current user profile
export const getCurrentUser = async (): Promise<User> => {
  try {
    console.log('👤 Fetching current user profile...');
    
    const response = await authFetch(`${API_BASE_URL}/api/profile`);
    const data = await handleAuthResponse(response);
    
    console.log('✅ User profile fetched successfully');
    // The backend returns the user data directly, not wrapped in a user property
    return data;
  } catch (error) {
    console.error('❌ Failed to fetch user profile:', error);
    throw error;
  }
};

// Update user profile
export const updateUserProfile = async (updates: { name?: string; avatar?: string }): Promise<User> => {
  try {
    console.log('✏️ Updating user profile...', updates);
    
    const response = await authFetch(`${API_BASE_URL}/api/profile`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    
    const data = await handleAuthResponse(response);
    
    console.log('✅ User profile updated successfully');
    // The backend returns the user data directly, not wrapped in a user property
    return data;
  } catch (error) {
    console.error('❌ Failed to update user profile:', error);
    throw error;
  }
};

// Get onboarding status
export const getOnboardingStatus = async (): Promise<any> => {
  try {
    console.log('📋 Fetching onboarding status...');
    
    const response = await authFetch(`${API_BASE_URL}/api/auth/onboarding`);
    const data = await handleAuthResponse(response);
    
    console.log('✅ Onboarding status fetched successfully');
    return data;
  } catch (error) {
    console.error('❌ Failed to fetch onboarding status:', error);
    throw error;
  }
};

// Validate current token and get user info
export const validateToken = async (): Promise<User | null> => {
  const token = tokenStorage.getAccessToken();
  if (!token) {
    return null;
  }
  
  try {
    return await getCurrentUser();
  } catch (error) {
    if (error instanceof AuthError && error.statusCode === 401) {
      // Token is invalid, try to refresh
      try {
        await refreshAccessToken();
        // After refreshing token, try to get user again
        return await getCurrentUser();
      } catch (refreshError) {
        // Refresh failed, user needs to login again
        tokenStorage.clearTokens();
        return null;
      }
    }
    throw error;
  }
};