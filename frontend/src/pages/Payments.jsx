import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Container, Typography, Box, Grid,
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress
} from '@mui/material';
import PaymentCalculator from '../components/payments/PaymentCalculator';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function Payments() {
  const { isAdmin, isTreasurer } = useAuth();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const response = await client.get('/payments/coupons');
      setPayments(response.data);
    } catch (error) {
      toast.error('Failed to load payments');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'processed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
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
        Coupon Payments
      </Typography>

      {(isAdmin || isTreasurer) && (
        <Grid container spacing={3} sx={{ mt: 2, mb: 4 }}>
          <Grid item xs={12}>
            <PaymentCalculator onSuccess={fetchPayments} />
          </Grid>
        </Grid>
      )}

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Payment History
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Payment Ref</TableCell>
              <TableCell>Member</TableCell>
              <TableCell>Payment Date</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Gross Amount</TableCell>
              <TableCell align="right">Net Amount</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {payments.map((payment) => (
              <TableRow key={payment.payment_id}>
                <TableCell>{payment.payment_reference}</TableCell>
                <TableCell>
                  {payment.user?.first_name} {payment.user?.last_name}
                </TableCell>
                <TableCell>
                  {new Date(payment.payment_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {payment.payment_type?.replace('_', ' ')}
                </TableCell>
                <TableCell align="right">
                  ${parseFloat(payment.gross_coupon_amount).toLocaleString()}
                </TableCell>
                <TableCell align="right">
                  ${parseFloat(payment.net_payment_amount).toLocaleString()}
                </TableCell>
                <TableCell>
                  <Chip
                    label={payment.payment_status}
                    color={getStatusColor(payment.payment_status)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}
