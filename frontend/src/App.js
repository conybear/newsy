import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import LoginRegister from './components/LoginRegister';
import WeeklyEdition from './pages/WeeklyEdition';
import Stories from './pages/Stories';
import Friends from './pages/Friends';
import Archive from './pages/Archive';
import DebugPage from './pages/DebugPage';
import { AlertTriangle, X } from 'lucide-react';
import './App.css';

// Network Error Banner Component
const NetworkErrorBanner = ({ error, onClearError }) => {
  if (!error) return null;

  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-yellow-600" />
          <span className="text-sm text-yellow-800">{error}</span>
        </div>
        <button
          onClick={onClearError}
          className="text-yellow-600 hover:text-yellow-800"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

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
  const { isAuthenticated, loading, error, clearError } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return (
    <div>
      <NetworkErrorBanner error={error} onClearError={clearError} />
      {!isAuthenticated ? (
        <LoginRegister />
      ) : (
        <Routes>
          <Route path="/" element={<Navigate to="/edition" replace />} />
          <Route path="/edition" element={<WeeklyEdition />} />
          <Route path="/stories" element={<Stories />} />
          <Route path="/friends" element={<Friends />} />
          <Route path="/archive" element={<Archive />} />
          <Route path="/debug" element={<DebugPage />} />
        </Routes>
      )}
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <div className="App">
            <AppContent />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;