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
      // Use new dashboard endpoint (baseURL already includes /api/v1)
      const response = await client.get('/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Fallback to old endpoints if new one fails
      try {
        if (isMember) {
          const response = await client.get(`/bonds/portfolio/${currentUser.user_id}`);
          setStats(response.data);
        } else {
          const [bondsRes, paymentsRes] = await Promise.all([
            client.get('/bonds/purchases'),
            client.get('/payments/coupons')
          ]);
          setStats({
            total_bonds: bondsRes.data.length,
            total_payments: paymentsRes.data.length
          });
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
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

      {/* Bond Purchases System KPIs */}
      <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
        Bond Purchases Overview
      </Typography>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Description color="primary" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Total Purchases
                </Typography>
              </Box>
              <Typography variant="h4">
                {stats?.kpis?.total_bond_purchases || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Total Bond Shares
                </Typography>
              </Box>
              <Typography variant="h4">
                {stats?.kpis?.total_purchase_bond_shares?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Payment color="info" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Total Face Value
                </Typography>
              </Box>
              <Typography variant="h4">
                ${stats?.kpis?.total_purchase_face_value?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccountBalance color="warning" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Active Purchases
                </Typography>
              </Box>
              <Typography variant="h4">
                {stats?.kpis?.active_purchases || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bond Issues System KPIs */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Bond Issues Overview
      </Typography>
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccountBalance color="primary" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Bond Issues
                </Typography>
              </Box>
              <Typography variant="h4">
                {stats?.kpis?.total_bond_issues || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Issues Face Value
                </Typography>
              </Box>
              <Typography variant="h4">
                ${stats?.kpis?.total_face_value?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Payment color="info" sx={{ mr: 1 }} />
                <Typography color="text.secondary" variant="body2">
                  Total Members
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {stats?.kpis?.total_members || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upcoming Events */}
      {stats?.upcoming_events && stats.upcoming_events.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Upcoming Payment Events
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {stats.upcoming_events.map((event) => (
              <Grid item xs={12} md={6} key={event.event_id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary">
                      {event.event_name}
                    </Typography>
                    <Typography color="text.secondary" variant="body2">
                      {event.bond_name} • {event.payment_date}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Type: {event.event_type}
                    </Typography>
                    {event.boz_award_amount > 0 && (
                      <Typography variant="body2">
                        BOZ Award: ${event.boz_award_amount.toLocaleString()}
                      </Typography>
                    )}
                    <Typography variant="body2" color={event.payments_generated ? 'success.main' : 'warning.main'}>
                      {event.payments_generated ? `✓ ${event.payments_count} payments generated` : '⚠ Not yet generated'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Recent Events */}
      {stats?.recent_events && stats.recent_events.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Recent Payments
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {stats.recent_events.map((event) => (
              <Grid item xs={12} md={6} key={event.event_id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.primary">
                      {event.event_name}
                    </Typography>
                    <Typography color="text.secondary" variant="body2">
                      {event.bond_name} • {event.payment_date}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Payments: {event.payments_count}
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      ${event.total_paid.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
}
