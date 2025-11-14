import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Container, Typography, Box, Grid, Card, CardContent,
  Button, TextField, CircularProgress
} from '@mui/material';
import { Download, Assessment } from '@mui/icons-material';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function Reports() {
  const { isAdmin, isTreasurer } = useAuth();
  const [loading, setLoading] = useState(false);
  const [monthlyMonth, setMonthlyMonth] = useState('');
  const [paymentDates, setPaymentDates] = useState({
    start_date: '',
    end_date: ''
  });

  const handleExportMonthly = async () => {
    if (!monthlyMonth) {
      toast.error('Please select a month');
      return;
    }

    setLoading(true);
    try {
      const response = await client.get(`/exports/monthly-summary/${monthlyMonth}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `monthly_summary_${monthlyMonth}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Monthly summary exported successfully');
    } catch (error) {
      toast.error('Failed to export monthly summary');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPayments = async () => {
    if (!paymentDates.start_date || !paymentDates.end_date) {
      toast.error('Please select both start and end dates');
      return;
    }

    setLoading(true);
    try {
      const response = await client.get('/exports/payment-register', {
        params: paymentDates,
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payment_register_${paymentDates.start_date}_${paymentDates.end_date}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Payment register exported successfully');
    } catch (error) {
      toast.error('Failed to export payment register');
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin && !isTreasurer) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4">Access Denied</Typography>
        <Typography>You do not have permission to view reports.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Reports & Exports
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Assessment color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Monthly Summary Report</Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Export monthly summary with member balances to Excel
              </Typography>

              <TextField
                fullWidth
                type="month"
                label="Select Month"
                value={monthlyMonth}
                onChange={(e) => setMonthlyMonth(e.target.value + '-01')}
                InputLabelProps={{ shrink: true }}
                sx={{ mb: 2 }}
              />

              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <Download />}
                onClick={handleExportMonthly}
                disabled={loading || !monthlyMonth}
              >
                Export Monthly Summary
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Assessment color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">Payment Register</Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Export payment register for a specific date range
              </Typography>

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Start Date"
                    value={paymentDates.start_date}
                    onChange={(e) => setPaymentDates({ ...paymentDates, start_date: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="End Date"
                    value={paymentDates.end_date}
                    onChange={(e) => setPaymentDates({ ...paymentDates, end_date: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>

              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <Download />}
                onClick={handleExportPayments}
                disabled={loading || !paymentDates.start_date || !paymentDates.end_date}
              >
                Export Payment Register
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
