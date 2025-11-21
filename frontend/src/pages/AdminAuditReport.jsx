import { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Box, Grid, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Chip, TextField, InputAdornment,
  IconButton, Tooltip, Divider, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Assessment, CheckCircle, Warning, Error as ErrorIcon,
  Search, Download, Refresh, FilterList,
  TrendingUp, TrendingDown, AccountBalance
} from '@mui/icons-material';
import api from '../api/client';

function AdminAuditReport() {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchAuditReport();
  }, []);

  const fetchAuditReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/admin/audit');
      setAuditData(response.data);
    } catch (err) {
      setError('Failed to load audit report. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!auditData) return;

    const csvContent = [
      ['Event', 'Bond', 'Date', 'Calc Maturity', 'Exp Maturity', 'Mat Diff', 'Calc Coupon', 'Exp Coupon', 'Cpn Diff', 'Status'].join(','),
      ...auditData.report.map(event => [
        `"${event.event_name}"`,
        `"${event.bond_name}"`,
        event.payment_date,
        event.calculated_net_maturity,
        event.expected_net_maturity,
        event.maturity_difference,
        event.calculated_net_coupon,
        event.expected_net_coupon,
        event.coupon_difference,
        event.has_discrepancy ? 'DISCREPANCY' : 'OK'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const filteredReport = auditData?.report?.filter(event => {
    const matchesSearch =
      event.event_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.bond_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'discrepancy' && event.has_discrepancy) ||
      (statusFilter === 'matched' && !event.has_discrepancy);

    return matchesSearch && matchesStatus;
  }) || [];

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="60vh" gap={2}>
        <CircularProgress size={48} />
        <Typography color="text.secondary">Loading audit report...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert
          severity="error"
          action={
            <IconButton color="inherit" size="small" onClick={fetchAuditReport}>
              <Refresh />
            </IconButton>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  if (!auditData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">No audit data available</Alert>
      </Container>
    );
  }

  const { summary } = auditData;

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box display="flex" alignItems="center" gap={2}>
          <Assessment sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" fontWeight="bold" color="text.primary">
              Audit Report
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Financial reconciliation and discrepancy analysis
            </Typography>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={fetchAuditReport} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export to CSV">
            <IconButton onClick={handleExport} color="primary">
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Overall Status Banner */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          background: summary.has_overall_discrepancy
            ? 'linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%)'
            : 'linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%)',
          border: '1px solid',
          borderColor: summary.has_overall_discrepancy ? 'error.light' : 'success.light'
        }}
      >
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            {summary.has_overall_discrepancy ? (
              <Warning sx={{ fontSize: 48, color: 'error.main' }} />
            ) : (
              <CheckCircle sx={{ fontSize: 48, color: 'success.main' }} />
            )}
            <Box>
              <Typography variant="h5" fontWeight="bold" color={summary.has_overall_discrepancy ? 'error.main' : 'success.main'}>
                {summary.has_overall_discrepancy ? 'Discrepancies Detected' : 'All Records Matched'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {summary.events_with_discrepancies} of {summary.total_events} events have discrepancies
              </Typography>
            </Box>
          </Box>
          <Chip
            label={summary.has_overall_discrepancy ? 'REQUIRES ATTENTION' : 'VERIFIED'}
            color={summary.has_overall_discrepancy ? 'error' : 'success'}
            variant="filled"
            sx={{ fontWeight: 'bold', px: 2, py: 2.5 }}
          />
        </Box>
      </Paper>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        {/* Total Events Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ height: '100%', borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccountBalance sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  Total Events
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color="text.primary">
                {summary.total_events}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Payment events audited
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Events with Discrepancies */}
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ height: '100%', borderRadius: 2, borderLeft: '4px solid', borderColor: summary.events_with_discrepancies > 0 ? 'error.main' : 'success.main' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ErrorIcon sx={{ color: summary.events_with_discrepancies > 0 ? 'error.main' : 'success.main', mr: 1 }} />
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  Discrepancies
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color={summary.events_with_discrepancies > 0 ? 'error.main' : 'success.main'}>
                {summary.events_with_discrepancies}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Events requiring review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Maturity Difference */}
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ height: '100%', borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                {summary.total_maturity_difference >= 0 ? (
                  <TrendingUp sx={{ color: 'info.main', mr: 1 }} />
                ) : (
                  <TrendingDown sx={{ color: 'warning.main', mr: 1 }} />
                )}
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  Maturity Variance
                </Typography>
              </Box>
              <Typography
                variant="h4"
                fontWeight="bold"
                color={Math.abs(summary.total_maturity_difference) > 0.01 ? 'error.main' : 'success.main'}
              >
                ${summary.total_maturity_difference.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Calculated vs Expected
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Coupon Difference */}
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ height: '100%', borderRadius: 2 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                {summary.total_coupon_difference >= 0 ? (
                  <TrendingUp sx={{ color: 'info.main', mr: 1 }} />
                ) : (
                  <TrendingDown sx={{ color: 'warning.main', mr: 1 }} />
                )}
                <Typography variant="body2" color="text.secondary" fontWeight="medium">
                  Coupon Variance
                </Typography>
              </Box>
              <Typography
                variant="h4"
                fontWeight="bold"
                color={Math.abs(summary.total_coupon_difference) > 0.01 ? 'error.main' : 'success.main'}
              >
                ${summary.total_coupon_difference.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Calculated vs Expected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Breakdown */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" fontWeight="bold" mb={2} display="flex" alignItems="center">
              <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
              Maturity Reconciliation
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography color="text.secondary">Calculated Net Maturity</Typography>
                <Typography fontWeight="bold" fontSize="1.1rem">
                  ${summary.total_calculated_net_maturity.toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography color="text.secondary">Expected Net Maturity</Typography>
                <Typography fontWeight="bold" fontSize="1.1rem">
                  ${summary.total_expected_net_maturity.toLocaleString()}
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography fontWeight="medium">Difference</Typography>
                <Chip
                  label={`$${summary.total_maturity_difference.toLocaleString()}`}
                  color={Math.abs(summary.total_maturity_difference) > 0.01 ? 'error' : 'success'}
                  variant="filled"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" fontWeight="bold" mb={2} display="flex" alignItems="center">
              <AccountBalance sx={{ mr: 1, color: 'secondary.main' }} />
              Coupon Reconciliation
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography color="text.secondary">Calculated Net Coupon</Typography>
                <Typography fontWeight="bold" fontSize="1.1rem">
                  ${summary.total_calculated_net_coupon.toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography color="text.secondary">Expected Net Coupon</Typography>
                <Typography fontWeight="bold" fontSize="1.1rem">
                  ${summary.total_expected_net_coupon.toLocaleString()}
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography fontWeight="medium">Difference</Typography>
                <Chip
                  label={`$${summary.total_coupon_difference.toLocaleString()}`}
                  color={Math.abs(summary.total_coupon_difference) > 0.01 ? 'error' : 'success'}
                  variant="filled"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Event Details Table */}
      <Paper elevation={2} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        {/* Table Header with Filters */}
        <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
            <Typography variant="h6" fontWeight="bold">
              Event-Level Details
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <TextField
                size="small"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search color="action" />
                      </InputAdornment>
                    ),
                  },
                }}
                sx={{ minWidth: 220 }}
              />
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                  startAdornment={<FilterList sx={{ mr: 1, color: 'action.active' }} />}
                >
                  <MenuItem value="all">All Events</MenuItem>
                  <MenuItem value="discrepancy">Discrepancies</MenuItem>
                  <MenuItem value="matched">Matched</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Showing {filteredReport.length} of {auditData.report.length} events
          </Typography>
        </Box>

        {/* Table */}
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Event</TableCell>
                <TableCell sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Bond</TableCell>
                <TableCell sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Date</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Calc Maturity</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Exp Maturity</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Mat Diff</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Calc Coupon</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Exp Coupon</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Cpn Diff</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredReport.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center" sx={{ py: 6 }}>
                    <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                      <Assessment sx={{ fontSize: 48, color: 'text.disabled' }} />
                      <Typography color="text.secondary">
                        {searchTerm || statusFilter !== 'all'
                          ? 'No events match your filters'
                          : 'No events to audit'}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredReport.map((event) => (
                  <TableRow
                    key={event.event_id}
                    sx={{
                      bgcolor: event.has_discrepancy ? 'rgba(211, 47, 47, 0.08)' : 'inherit',
                      '&:hover': { bgcolor: event.has_discrepancy ? 'rgba(211, 47, 47, 0.12)' : 'grey.100' }
                    }}
                  >
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {event.event_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {event.event_type}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{event.bond_name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                        {event.payment_date}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${event.calculated_net_maturity.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${event.expected_net_maturity.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        color={Math.abs(event.maturity_difference) > 0.01 ? 'error.main' : 'success.main'}
                      >
                        ${event.maturity_difference.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${event.calculated_net_coupon.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${event.expected_net_coupon.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        color={Math.abs(event.coupon_difference) > 0.01 ? 'error.main' : 'success.main'}
                      >
                        ${event.coupon_difference.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={event.has_discrepancy ? 'DIFF' : 'OK'}
                        color={event.has_discrepancy ? 'error' : 'success'}
                        size="small"
                        variant="filled"
                        sx={{ fontWeight: 'bold', minWidth: 60 }}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}

export default AdminAuditReport;
