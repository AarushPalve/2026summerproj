import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Analytics as AnalyticsIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
  HealthAndSafety as HealthIcon
} from '@mui/icons-material';
import { useAppContext } from '../context/AppContext';

const Navbar: React.FC = () => {
  const { backendHealthy } = useAppContext();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
    { name: 'Teams', path: '/teams', icon: <PeopleIcon /> },
    { name: 'Predictions', path: '/predictions', icon: <AnalyticsIcon /> },
    { name: 'Upload Data', path: '/upload', icon: <UploadIcon /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon /> }
  ];

  const drawerWidth = 240;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: '1px solid rgba(255, 255, 255, 0.12)'
        }
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" component="h1" sx={{ fontWeight: 'bold' }}>
          FRC Dashboard
        </Typography>
        {backendHealthy === true && (
          <Chip
            icon={<HealthIcon style={{ color: '#4caf50' }} />}
            label="Backend Healthy"
            size="small"
            sx={{ mt: 1, bgcolor: 'success.main', color: 'white' }}
          />
        )}
        {backendHealthy === false && (
          <Chip
            icon={<HealthIcon style={{ color: '#f44336' }} />}
            label="Backend Offline"
            size="small"
            sx={{ mt: 1, bgcolor: 'error.main', color: 'white' }}
          />
        )}
      </Box>

      <Divider />

      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.name}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark'
                }
              },
              '&:hover': {
                bgcolor: 'action.hover'
              }
            }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        ))}
      </List>

      <Box sx={{ flexGrow: 1 }} />

      <Divider />

      <Box sx={{ p: 1, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          v1.0.0
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Navbar;
