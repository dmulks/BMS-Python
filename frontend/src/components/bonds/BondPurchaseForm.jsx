import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, MenuItem, Grid, Typography
} from '@mui/material';
import toast from 'react-hot-toast';
import client from '../../api/client';

const schema = yup.object({
  user_id: yup.number().required('Member is required'),
  bond_type_id: yup.number().required('Bond type is required'),
  purchase_date: yup.date().required('Purchase date is required'),
  bond_shares: yup.number().min(1, 'Must be greater than 0').required('Bond shares required'),
  discount_rate: yup.number().min(0).max(1).required('Discount rate required'),
});

export default function BondPurchaseForm({ open, onClose, onSuccess }) {
  const [members, setMembers] = useState([]);
  const [bondTypes, setBondTypes] = useState([]);
  const [loading, setLoading] = useState(false);

  const { control, handleSubmit, formState: { errors }, reset } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      discount_rate: 0.10
    }
  });

  useEffect(() => {
    if (open) {
      fetchData();
    }
  }, [open]);

  const fetchData = async () => {
    try {
      const [membersRes, typesRes] = await Promise.all([
        client.get('/auth/users'),
        client.get('/bonds/types')
      ]);
      setMembers(membersRes.data);
      setBondTypes(typesRes.data);
    } catch (error) {
      toast.error('Failed to load form data');
    }
  };

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await client.post('/bonds/purchases', data);
      toast.success('Bond purchase recorded successfully');
      reset();
      onSuccess();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create purchase');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>New Bond Purchase</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Controller
                name="user_id"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    fullWidth
                    label="Member"
                    error={!!errors.user_id}
                    helperText={errors.user_id?.message}
                    InputLabelProps={{ shrink: true }}
                    SelectProps={{
                      displayEmpty: true,
                      renderValue: (selected) => {
                        if (!selected) return <em style={{ color: '#999' }}>Select a member</em>;
                        const member = members.find(m => m.user_id === selected);
                        return member ? `${member.first_name} ${member.last_name} - ${member.email}` : '';
                      }
                    }}
                  >
                    {members.map((member) => (
                      <MenuItem key={member.user_id} value={member.user_id}>
                        {member.first_name} {member.last_name} - {member.email}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="bond_type_id"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    fullWidth
                    label="Bond Type"
                    error={!!errors.bond_type_id}
                    helperText={errors.bond_type_id?.message}
                    InputLabelProps={{ shrink: true }}
                    SelectProps={{
                      displayEmpty: true,
                      renderValue: (selected) => {
                        if (!selected) return <em style={{ color: '#999' }}>Select bond type</em>;
                        const bondType = bondTypes.find(bt => bt.bond_type_id === selected);
                        return bondType ? bondType.bond_name : '';
                      }
                    }}
                  >
                    {bondTypes.map((type) => (
                      <MenuItem key={type.bond_type_id} value={type.bond_type_id}>
                        {type.bond_name}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="purchase_date"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    type="date"
                    fullWidth
                    label="Purchase Date"
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.purchase_date}
                    helperText={errors.purchase_date?.message}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="bond_shares"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    type="number"
                    fullWidth
                    label="Bond Shares"
                    error={!!errors.bond_shares}
                    helperText={errors.bond_shares?.message}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="discount_rate"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    type="number"
                    inputProps={{ step: 0.01, min: 0, max: 1 }}
                    fullWidth
                    label="Discount Rate"
                    placeholder="0.10"
                    error={!!errors.discount_rate}
                    helperText={errors.discount_rate?.message || "Enter as decimal (e.g., 0.10 = 10%)"}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="caption" color="text.secondary">
                Face Value and other calculations will be computed automatically
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create Purchase'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
