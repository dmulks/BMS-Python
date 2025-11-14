import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Container, Grid, Card, CardContent,
  Typography, Box, CircularProgress
} from '@mui/material';
import {
  AccountBalance, TrendingUp,
  Payment, Description
} from '@mui/icons-material';
import client from '../api/client';

export default function Dashboard() {
  const { currentUser, isMember } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      if (isMember) {
        const response = await client.get(`/bonds/portfolio/${currentUser.user_id}`);
        setStats(response.data);
      } else {
        // Fetch admin/treasurer stats
        const [bondsRes, paymentsRes] = await Promise.all([
          client.get('/bonds/purchases'),
          client.get('/payments/coupons')
        ]);
        setStats({
          total_bonds: bondsRes.data.length,
          total_payments: paymentsRes.data.length
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {currentUser.first_name}!
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccountBalance color="primary" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="h6">
                  Total Investment
                </Typography>
              </Box>
              <Typography variant="h4">
                ${stats?.total_investment?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="h6">
                  Current Value
                </Typography>
              </Box>
              <Typography variant="h4">
                ${stats?.total_face_value?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Payment color="info" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="h6">
                  Total Returns
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                ${stats?.total_payments_received?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Description color="warning" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="h6">
                  Active Bonds
                </Typography>
              </Box>
              <Typography variant="h4">
                {stats?.active_bonds_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
