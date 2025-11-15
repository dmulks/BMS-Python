import React from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  AppBar, Toolbar, Typography, Button, Box,
  IconButton, Menu, MenuItem, Avatar
} from '@mui/material';
import {
  Dashboard, AccountBalance, Payment,
  Assessment, ExitToApp, People
} from '@mui/icons-material';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const { currentUser, logout, isAdmin, isTreasurer } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4 }}>
            Bond Management System
          </Typography>

          <Box sx={{ flexGrow: 1, display: 'flex', gap: 2 }}>
            <Button
              color="inherit"
              startIcon={<Dashboard />}
              component={RouterLink}
              to="/dashboard"
            >
              Dashboard
            </Button>

            <Button
              color="inherit"
              startIcon={<AccountBalance />}
              component={RouterLink}
              to="/bonds"
            >
              Bonds
            </Button>

            <Button
              color="inherit"
              startIcon={<Payment />}
              component={RouterLink}
              to="/payments"
            >
              Payments
            </Button>

            {(isAdmin || isTreasurer) && (
              <>
                <Button
                  color="inherit"
                  startIcon={<Assessment />}
                  component={RouterLink}
                  to="/reports"
                >
                  Reports
                </Button>
                <Button
                  color="inherit"
                  startIcon={<People />}
                  component={RouterLink}
                  to="/users"
                >
                  Users
                </Button>
              </>
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2">
              {currentUser?.first_name} {currentUser?.last_name}
            </Typography>
            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {currentUser?.first_name?.[0]}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleLogout}>
                <ExitToApp sx={{ mr: 1 }} /> Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
        {children}
      </Box>
    </Box>
  );
}
