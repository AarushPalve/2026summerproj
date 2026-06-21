import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Divider,
  TextField,
  Button,
  Alert,
  Snackbar,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { checkBackendHealth, checkMLHealth } from '../services/api';
import { Refresh as RefreshIcon } from '@mui/icons-material';

const SettingsPage: React.FC = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [backendStatus, setBackendStatus] = useState<'healthy' | 'unhealthy' | 'checking'>('checking');
  const [mlStatus, setMlStatus] = useState<'healthy' | 'degraded' | 'checking'>('checking');
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check system status
    const checkSystemStatus = async () => {
      try {
        // Check backend
        const backendHealthy = await checkBackendHealth();
        setBackendStatus(backendHealthy ? 'healthy' : 'unhealthy');

        // Check ML
        const mlHealth = await checkMLHealth();
        setMlStatus(mlHealth.status === 'healthy' ? 'healthy' : 'degraded');

      } catch (err) {
        setBackendStatus('unhealthy');
        setMlStatus('degraded');
      }
    };

    checkSystemStatus();
  }, []);

  const handleSaveSettings = () => {
    // In a real app, this would save to localStorage or backend
    setShowSuccess(true);
    setError(null);
  };

  const handleResetSettings = () => {
    setDarkMode(true);
    setAutoRefresh(true);
    setRefreshInterval(30);
    setApiBaseUrl('');
  };

  const getStatusColor = (status: 'healthy' | 'unhealthy' | 'degraded' | 'checking') => {
    switch (status) {
      case 'healthy': return 'success.main';
      case 'unhealthy': return 'error.main';
      case 'degraded': return 'warning.main';
      default: return 'info.main';
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      {/* System Status */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Backend Service
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    bgcolor: getStatusColor(backendStatus),
                    animation: backendStatus === 'checking' ? 'pulse 1.5s infinite' : 'none'
                  }} />
                  <Typography variant="body1">
                    {backendStatus === 'checking' ? 'Checking...' :
                     backendStatus === 'healthy' ? 'Healthy' : 'Unhealthy'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  ML Pipeline
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    bgcolor: getStatusColor(mlStatus),
                    animation: mlStatus === 'checking' ? 'pulse 1.5s infinite' : 'none'
                  }} />
                  <Typography variant="body1">
                    {mlStatus === 'checking' ? 'Checking...' :
                     mlStatus === 'healthy' ? 'Healthy' : mlStatus === 'degraded' ? 'Degraded' : 'Unhealthy'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* General Settings */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          General Settings
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
                color="primary"
              />
            }
            label="Dark Mode"
          />

          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="Auto-refresh Data"
          />

          {autoRefresh && (
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Refresh Interval (sec)</InputLabel>
              <Select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                label="Refresh Interval (sec)"
              >
                <MenuItem value={15}>15 seconds</MenuItem>
                <MenuItem value={30}>30 seconds</MenuItem>
                <MenuItem value={60}>1 minute</MenuItem>
                <MenuItem value={300}>5 minutes</MenuItem>
              </Select>
            </FormControl>
          )}
        </Box>
      </Paper>

      {/* API Settings */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          API Settings
        </Typography>

        <TextField
          label="API Base URL"
          value={apiBaseUrl}
          onChange={(e) => setApiBaseUrl(e.target.value)}
          fullWidth
          placeholder="Leave empty for default"
          helperText="e.g., http://localhost:8000/api/v1"
          variant="outlined"
          sx={{ mb: 2 }}
        />

        <Button
          variant="outlined"
          onClick={() => setApiBaseUrl('')}
          disabled={!apiBaseUrl}
        >
          Reset to Default
        </Button>
      </Paper>

      {/* Data Sync Settings */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Sync Settings
        </Typography>

        <Typography variant="body2" paragraph>
          Configure how the dashboard synchronizes data with the backend.
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControlLabel
            control={<Switch color="primary" />}
            label="Enable Hotspot Sync (30-second intervals)"
            disabled
          />

          <FormControlLabel
            control={<Switch color="primary" />}
            label="Sync on Startup"
            disabled
          />

          <FormControlLabel
            control={<Switch color="primary" />}
            label="Background Sync"
            disabled
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          disabled
        >
          Force Sync Now
        </Button>
      </Paper>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>

        <Button
          variant="outlined"
          onClick={handleResetSettings}
          size="large"
        >
          Reset to Defaults
        </Button>
      </Box>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={3000}
        onClose={() => setShowSuccess(false)}
      >
        <Alert severity="success" onClose={() => setShowSuccess(false)}>
          Settings saved successfully!
        </Alert>
      </Snackbar>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Information Section */}
      <Paper elevation={3} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          About
        </Typography>
        <Typography variant="body2" paragraph>
          FRC Strategic Dashboard v1.0.0
        </Typography>
        <Typography variant="body2" paragraph>
          A comprehensive analytics platform for FIRST Robotics Competition teams.
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Typography variant="body2" paragraph>
          <strong>Features:</strong>
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="Real-time match predictions using ML models" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="EPA, OPR, and cOPR calculations" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="Team comparison and analysis tools" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="30-second hotspot sync for competition environments" />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

        <Typography variant="body2" paragraph>
          <strong>Support:</strong> For issues or questions, please refer to the documentation or
          open a GitHub issue.
        </Typography>
      </Paper>
    </Box>
  );
};

export default SettingsPage;