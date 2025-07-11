import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import LoginRegister from './components/LoginRegister';
import WeeklyEdition from './pages/WeeklyEdition';
import Stories from './pages/Stories';
import Friends from './pages/Friends';
import Archive from './pages/Archive';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <LoginRegister />;
};

// App content component
const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <LoginRegister />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/edition" replace />} />
      <Route path="/edition" element={<WeeklyEdition />} />
      <Route path="/stories" element={<Stories />} />
      <Route path="/friends" element={<Friends />} />
      <Route path="/archive" element={<Archive />} />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <AppContent />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;