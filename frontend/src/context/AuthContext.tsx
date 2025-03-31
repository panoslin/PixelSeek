'use client';

import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

// API URL would be defined in an environment variable in production
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface User {
  id: string;
  username: string;
  email: string;
  auth_provider?: string;
  subscription_tier?: string;
  profile_image?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  login: (tokens: { access: string; refresh: string }) => Promise<void>;
  logout: () => void;
  getAccessToken: () => string | null;
  refreshTokens: () => Promise<string | null>;
}

// Default context values
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  getAccessToken: () => null,
  refreshTokens: async () => null,
});

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();

  // Refresh access token using refresh token
  const refreshTokens = async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      return null;
    }
    
    try {
      const response = await fetch(`${API_URL}/users/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh: refreshToken })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        
        // Update token expiration time
        const expiresAt = new Date();
        expiresAt.setHours(expiresAt.getHours() + 1);
        localStorage.setItem('token_expires', expiresAt.toISOString());
        
        return data.access;
      }
      
      // If refresh fails, remove tokens and return null
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_expires');
      return null;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return null;
    }
  };

  // Logout user and clear tokens
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires');
    localStorage.removeItem('remember_me');
    setIsAuthenticated(false);
    setUser(null);
    router.push('/auth/login');
  };

  // Login user with provided tokens
  const login = async (tokens: { access: string; refresh: string }): Promise<void> => {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    
    // Set token expiration (typically 1 hour)
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 1);
    localStorage.setItem('token_expires', expiresAt.toISOString());
    
    setIsAuthenticated(true);
    
    try {
      // Fetch user profile after login
      const userResponse = await fetch(`${API_URL}/users/me/`, {
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
      } else {
        throw new Error('Failed to fetch user data');
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  // Get current access token
  const getAccessToken = (): string | null => {
    const token = localStorage.getItem('access_token');
    const tokenExpiry = localStorage.getItem('token_expires');
    
    if (!token || !tokenExpiry) {
      return null;
    }
    
    // Check if token is expired
    const now = new Date();
    const expiry = new Date(tokenExpiry);
    
    if (now >= expiry) {
      // Token is expired, will need to be refreshed
      return null;
    }
    
    return token;
  };

  // Check authentication state on initial load
  useEffect(() => {
    const initAuth = async () => {
      try {
        let token = getAccessToken();
        
        // If token is expired or missing, try to refresh
        if (!token) {
          token = await refreshTokens();
          
          // If refresh fails, logout
          if (!token) {
            logout();
            setLoading(false);
            return;
          }
        }
        
        // Fetch user profile with valid token
        const userResponse = await fetch(`${API_URL}/users/me/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Invalid token or user not found
          logout();
        }
      } catch (error) {
        console.error('Authentication initialization error:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);

  return (
    <AuthContext.Provider 
      value={{
        isAuthenticated,
        user,
        loading,
        login,
        logout,
        getAccessToken,
        refreshTokens
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export default AuthContext; 