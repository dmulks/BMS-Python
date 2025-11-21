import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Container, Typography, Button, Box,
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress
} from '@mui/material';
import { Add, Upload, AccountBalance } from '@mui/icons-material';
import BondPurchaseForm from '../components/bonds/BondPurchaseForm';
import ExcelImportDialog from '../components/bonds/ExcelImportDialog';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function Bonds() {
  const navigate = useNavigate();
  const { isAdmin, isTreasurer, currentUser } = useAuth();
  const [bonds, setBonds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);

  useEffect(() => {
    fetchBonds();
  }, []);

  const fetchBonds = async () => {
    try {
      const response = await client.get('/bonds/purchases');
      setBonds(response.data);
    } catch (error) {
      toast.error('Failed to load bonds');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'matured':
        return 'default';
      case 'cancelled':
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Bond Purchases</Typography>
        {(isAdmin || isTreasurer) && (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AccountBalance />}
              onClick={() => navigate('/bonds/1')}
            >
              View Bond Issues
            </Button>
            <Button
              variant="outlined"
              startIcon={<Upload />}
              onClick={() => setImportOpen(true)}
            >
              Import Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setFormOpen(true)}
            >
              New Purchase
            </Button>
          </Box>
        )}
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Transaction Ref</TableCell>
              <TableCell>Member</TableCell>
              <TableCell>Purchase Date</TableCell>
              <TableCell align="right">Bond Shares</TableCell>
              <TableCell align="right">Face Value</TableCell>
              <TableCell align="right">Purchase Price</TableCell>
              <TableCell>Maturity Date</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bonds.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                    No bond purchases found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              bonds.map((bond) => (
                <TableRow key={bond.purchase_id}>
                  <TableCell>{bond.transaction_reference}</TableCell>
                  <TableCell>
                    {bond.user ? `${bond.user.first_name} ${bond.user.last_name}` : `User ID: ${bond.user_id}`}
                  </TableCell>
                <TableCell>
                  {new Date(bond.purchase_date).toLocaleDateString()}
                </TableCell>
                <TableCell align="right">
                  {parseFloat(bond.bond_shares).toLocaleString()}
                </TableCell>
                <TableCell align="right">
                  ${parseFloat(bond.face_value).toLocaleString()}
                </TableCell>
                <TableCell align="right">
                  ${parseFloat(bond.purchase_price).toLocaleString()}
                </TableCell>
                <TableCell>
                  {new Date(bond.maturity_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Chip
                    label={bond.purchase_status}
                    color={getStatusColor(bond.purchase_status)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))
          )}
          </TableBody>
        </Table>
      </TableContainer>

      <BondPurchaseForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={fetchBonds}
      />

      <ExcelImportDialog
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onSuccess={fetchBonds}
      />
    </Container>
  );
}
