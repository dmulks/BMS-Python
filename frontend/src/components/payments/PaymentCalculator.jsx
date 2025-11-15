import React, { useState } from 'react';
import {
  Card, CardContent, TextField, Button,
  Grid, Typography, Box, CircularProgress,
  Table, TableBody, TableCell, TableHead, TableRow
} from '@mui/material';
import toast from 'react-hot-toast';
import client from '../../api/client';

export default function PaymentCalculator({ onSuccess }) {
  const [dates, setDates] = useState({
    period_start_date: '',
    period_end_date: ''
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await client.post(
        `/payments/calculate-coupons?period_start=${dates.period_start_date}&period_end=${dates.period_end_date}`
      );
      setResults(response.data);
      toast.success('Calculations completed');
    } catch (error) {
      console.error('Calculation error:', error);
      toast.error(error.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    setLoading(true);
    try {
      const response = await client.post(
        `/payments/calculate-coupons?period_start=${dates.period_start_date}&period_end=${dates.period_end_date}&create_payments=true`
      );
      toast.success(`${response.data.count || 0} payments processed`);
      setResults(null);
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Processing error:', error);
      toast.error(error.response?.data?.detail || 'Processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Coupon Payment Calculator
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="date"
              label="Period Start Date"
              value={dates.period_start_date}
              onChange={(e) => setDates({ ...dates, period_start_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              helperText="Select the start date for coupon calculation period"
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="date"
              label="Period End Date"
              value={dates.period_end_date}
              onChange={(e) => setDates({ ...dates, period_end_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              helperText="Select the end date for coupon calculation period"
              required
            />
          </Grid>
        </Grid>

        {!dates.period_start_date || !dates.period_end_date ? (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'info.lighter', borderRadius: 1 }}>
            <Typography variant="body2" color="info.dark">
              Please select both Period Start Date and Period End Date to enable the Calculate button
            </Typography>
          </Box>
        ) : null}

        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            onClick={handleCalculate}
            disabled={loading || !dates.period_start_date || !dates.period_end_date}
            sx={{ mr: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Calculate'}
          </Button>
          {results && (
            <Button
              variant="contained"
              color="success"
              onClick={handleProcess}
              disabled={loading}
            >
              Process Payments
            </Button>
          )}
        </Box>

        {results && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Calculation Results
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography>Total Payments: {results.calculations_count}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography>Total Amount: ${results.total_net_amount?.toLocaleString()}</Typography>
              </Grid>
            </Grid>

            <Table sx={{ mt: 2 }} size="small">
              <TableHead>
                <TableRow>
                  <TableCell>User ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Gross</TableCell>
                  <TableCell align="right">Net</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.calculations?.slice(0, 10).map((calc, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{calc.user_id}</TableCell>
                    <TableCell>{calc.payment_type}</TableCell>
                    <TableCell align="right">${calc.gross_coupon?.toFixed(2)}</TableCell>
                    <TableCell align="right">${calc.net_payment?.toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
