import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Invitations from './pages/Invitations';
import Contributors from './pages/Contributors';
import Stories from './pages/Stories';
import Newspaper from './pages/Newspaper';
import Archive from './pages/Archive';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/invitations" element={
            <ProtectedRoute>
              <Layout>
                <Invitations />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/contributors" element={
            <ProtectedRoute>
              <Layout>
                <Contributors />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/stories" element={
            <ProtectedRoute>
              <Layout>
                <Stories />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/newspaper" element={
            <ProtectedRoute>
              <Layout>
                <Newspaper />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/archive" element={
            <ProtectedRoute>
              <Layout>
                <Archive />
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;