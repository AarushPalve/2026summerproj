import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import App from './App';

// Create a custom theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3'
    },
    secondary: {
      main: '#ff4081'
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e'
    }
  },
  typography: {
    fontFamily: 'Roboto, sans-serif'
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8
        }
      }
    }
  }
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
);
