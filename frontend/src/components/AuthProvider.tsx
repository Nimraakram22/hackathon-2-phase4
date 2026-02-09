import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  user_id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Load token from localStorage on mount
    const savedToken = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
      email,
      password,
    });

    const { access_token, user_id, email: userEmail } = response.data;
    const userData = { user_id, email: userEmail };

    setToken(access_token);
    setUser(userData);

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const register = async (email: string, password: string) => {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, {
      email,
      password,
    });

    const { access_token, user_id, email: userEmail } = response.data;
    const userData = { user_id, email: userEmail };

    setToken(access_token);
    setUser(userData);

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        register,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
