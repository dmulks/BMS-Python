import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Container, Grid, Card, CardContent, Paper, Divider,
  Typography, Box, CircularProgress, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip
} from '@mui/material';
import {
  AccountBalance, TrendingUp, Payment, Description,
  Person, PieChart, AttachMoney
} from '@mui/icons-material';
import client from '../api/client';

export default function Dashboard() {
  const { currentUser, isMember } = useAuth();
  const [stats, setStats] = useState(null);
  const [memberData, setMemberData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isMember) {
      fetchMemberDashboard();
    } else {
      fetchAdminDashboard();
    }
  }, [isMember, currentUser]);

  const fetchMemberDashboard = async () => {
    try {
      // Fetch member holdings and payments
      const [holdingsRes, paymentsRes] = await Promise.all([
        client.get(`/members/${currentUser.user_id}/holdings`),
        client.get(`/members/${currentUser.user_id}/payments`)
      ]);

      // Calculate totals from holdings
      const holdings = holdingsRes.data || [];
      const totalShares = holdings.reduce((sum, h) => sum + (h.bond_shares || 0), 0);
      const totalFaceValue = holdings.reduce((sum, h) => sum + (h.member_face_value || 0), 0);

      // Process payments for the coupon table
      const payments = paymentsRes.data?.payments || [];

      setMemberData({
        holdings,
        payments,
        totals: {
          totalShares,
          totalFaceValue,
          ...paymentsRes.data?.totals
        }
      });
    } catch (error) {
      console.error('Failed to fetch member dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAdminDashboard = async () => {
    try {
      const response = await client.get('/dashboard');
      setStats(response.data);
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

  // Member Dashboard
  if (isMember) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" gap={2} mb={4}>
          <Person sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" fontWeight="bold">
              Welcome, {currentUser.first_name}!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your Bond Portfolio Overview
            </Typography>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6}>
            <Card elevation={2} sx={{ borderRadius: 2, height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <PieChart sx={{ color: 'primary.main', mr: 1, fontSize: 28 }} />
                  <Typography variant="body1" color="text.secondary" fontWeight="medium">
                    Total Bond Shares
                  </Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="primary.main">
                  {memberData?.totals?.totalShares?.toLocaleString() || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Shares across all bond holdings
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Card elevation={2} sx={{ borderRadius: 2, height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AttachMoney sx={{ color: 'success.main', mr: 1, fontSize: 28 }} />
                  <Typography variant="body1" color="text.secondary" fontWeight="medium">
                    Total Face Value
                  </Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  ${memberData?.totals?.totalFaceValue?.toLocaleString() || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Combined value of all holdings
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Net Coupon Payment Table */}
        <Paper elevation={2} sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Box display="flex" alignItems="center" gap={2}>
              <Payment sx={{ color: 'primary.main' }} />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  Total Net Coupon Payment
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Breakdown of your coupon payments and deductions
                </Typography>
              </Box>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.100' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Bond Name</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>Shares</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>Face Value</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>Semi-Annual Coupon</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', color: 'error.main' }}>Less 15% WHT</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', color: 'error.main' }}>Less 1% BOZ</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', color: 'error.main' }}>Less 2% Coop</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', color: 'success.main' }}>Net Coupon Receiving</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(!memberData?.payments || memberData.payments.length === 0) ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 6 }}>
                      <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                        <Payment sx={{ fontSize: 48, color: 'text.disabled' }} />
                        <Typography color="text.secondary">
                          No coupon payments found
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  <>
                    {memberData.payments.map((payment, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {payment.bond_name || 'N/A'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {payment.event_name || ''}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {payment.bond_shares?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            ${payment.member_face_value?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            ${payment.gross_coupon_from_boz?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="error.main">
                            -${payment.withholding_tax?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="error.main">
                            -${payment.boz_fee?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="error.main">
                            -${payment.coop_fee_on_coupon?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold" color="success.main">
                            ${payment.net_coupon_payment?.toLocaleString() || 0}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                    {/* Totals Row */}
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell colSpan={3}>
                        <Typography variant="body2" fontWeight="bold">
                          TOTAL
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${memberData.totals?.total_gross_coupon?.toLocaleString() || 0}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold" color="error.main">
                          -${memberData.totals?.total_taxes?.toLocaleString() || 0}
                        </Typography>
                      </TableCell>
                      <TableCell align="right" colSpan={2}>
                        <Typography variant="body2" fontWeight="bold" color="error.main">
                          -${memberData.totals?.total_fees?.toLocaleString() || 0}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`$${memberData.totals?.total_net_coupon_payment?.toLocaleString() || 0}`}
                          color="success"
                          sx={{ fontWeight: 'bold', fontSize: '1rem' }}
                        />
                      </TableCell>
                    </TableRow>
                  </>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Bond Holdings Summary */}
        {memberData?.holdings && memberData.holdings.length > 0 && (
          <Paper elevation={2} sx={{ borderRadius: 2, overflow: 'hidden', mt: 4 }}>
            <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Box display="flex" alignItems="center" gap={2}>
                <AccountBalance sx={{ color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Your Bond Holdings
                </Typography>
              </Box>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.100' }}>
                    <TableCell sx={{ fontWeight: 'bold' }}>Bond Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Shares</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Face Value</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>% Share</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Maturity Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {memberData.holdings.map((holding) => (
                    <TableRow key={holding.holding_id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {holding.bond_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={holding.bond_type}
                          size="small"
                          color={holding.bond_type === 'GRZ' ? 'primary' : 'secondary'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        {holding.bond_shares?.toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        ${holding.member_face_value?.toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        {holding.percentage_share?.toFixed(2)}%
                      </TableCell>
                      <TableCell>
                        {holding.maturity_date}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Container>
    );
  }

  // Admin Dashboard (original)
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
                      {event.bond_name} - {event.payment_date}
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
                      {event.payments_generated ? `${event.payments_count} payments generated` : 'Not yet generated'}
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
                      {event.bond_name} - {event.payment_date}
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
