import React, { createContext, useState, useContext, useEffect } from 'react';
import client from '../api/client';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      setCurrentUser(JSON.parse(user));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    localStorage.setItem('token', response.data.access_token);

    // Get user info
    const userResponse = await client.get('/auth/me');
    localStorage.setItem('user', JSON.stringify(userResponse.data));
    setCurrentUser(userResponse.data);

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    login,
    logout,
    isAuthenticated: !!currentUser,
    isAdmin: currentUser?.user_role === 'admin',
    isTreasurer: currentUser?.user_role === 'treasurer',
    isMember: currentUser?.user_role === 'member',
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
