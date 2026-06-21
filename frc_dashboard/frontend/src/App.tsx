import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import { AppProvider } from './context/AppContext';
import DashboardPage from './pages/DashboardPage';
import TeamsPage from './pages/TeamsPage';
import PredictionsPage from './pages/PredictionsPage';
import UploadPage from './pages/UploadPage';
import SettingsPage from './pages/SettingsPage';
import { checkBackendHealth } from './services/api';

const App: React.FC = () => {
  return (
    <AppProvider>
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <CssBaseline />
        <Navbar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 3,
            bgcolor: 'background.default',
            color: 'text.primary'
          }}
        >
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/teams" element={<TeamsPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Box>
      </Box>
    </AppProvider>
  );
};

export default App;
