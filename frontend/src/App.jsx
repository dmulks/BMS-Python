import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Bonds from './pages/Bonds';
import Payments from './pages/Payments';
import Reports from './pages/Reports';
import Users from './pages/Users';
import BondDetail from './pages/BondDetail';
import BondPaymentPreview from './pages/BondPaymentPreview';
import MemberPaymentsReport from './pages/MemberPaymentsReport';
import AdminAuditReport from './pages/AdminAuditReport';
import BozStatementUpload from './pages/BozStatementUpload';
import Layout from './components/common/Layout';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1a237e',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Layout>{children}</Layout> : <Navigate to="/login" />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bonds"
              element={
                <ProtectedRoute>
                  <Bonds />
                </ProtectedRoute>
              }
            />
            <Route
              path="/payments"
              element={
                <ProtectedRoute>
                  <Payments />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <Reports />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <Users />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bonds/:bondId"
              element={
                <ProtectedRoute>
                  <BondDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bonds/:bondId/events/:eventId/preview"
              element={
                <ProtectedRoute>
                  <BondPaymentPreview />
                </ProtectedRoute>
              }
            />
            <Route
              path="/members/:memberId/payments"
              element={
                <ProtectedRoute>
                  <MemberPaymentsReport />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/audit"
              element={
                <ProtectedRoute>
                  <AdminAuditReport />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/boz-upload"
              element={
                <ProtectedRoute>
                  <BozStatementUpload />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
