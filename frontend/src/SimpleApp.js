import React from 'react';
import { AuthProvider, useAuth } from './auth/SimpleAuth';
import SimpleLoginForm from './components/SimpleLoginForm';
import SimpleDashboard from './components/SimpleDashboard';

function AppContent() {
  const { user } = useAuth();

  if (user) {
    return <SimpleDashboard />;
  }

  return <SimpleLoginForm />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;