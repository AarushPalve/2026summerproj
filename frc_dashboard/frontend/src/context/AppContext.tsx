import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { checkBackendHealth } from '../services/api';

interface AppContextType {
  backendHealthy: boolean | null;
  darkMode: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
  toggleDarkMode: () => void;
  toggleAutoRefresh: () => void;
  setRefreshInterval: (interval: number) => void;
  checkBackendStatus: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [darkMode, setDarkMode] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);

  const checkBackendStatus = async () => {
    try {
      const healthy = await checkBackendHealth();
      setBackendHealthy(healthy);
    } catch (error) {
      setBackendHealthy(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(prev => !prev);
  };

  // Check backend status on initial load
  useEffect(() => {
    checkBackendStatus();

    // Set up periodic health checks
    const interval = setInterval(checkBackendStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <AppContext.Provider value={{
      backendHealthy,
      darkMode,
      autoRefresh,
      refreshInterval,
      toggleDarkMode,
      toggleAutoRefresh,
      setRefreshInterval,
      checkBackendStatus
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};