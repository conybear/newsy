import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [error, setError] = useState(null);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      setError(null);
      const response = await axios.get(`${API_BASE}/users/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      // Only logout if it's an auth error, not a network error
      if (error.response?.status === 401 || error.response?.status === 403) {
        logout();
      } else {
        setError('Network error - please check your connection');
        // Keep the user logged in for network errors
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE}/auth/login`, {
        email,
        password
      });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      await fetchCurrentUser();
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed - please try again'
      };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE}/auth/register`, {
        email,
        password,
        full_name: fullName
      });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      await fetchCurrentUser();
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed - please try again'
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setError(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    error,
    clearError,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};