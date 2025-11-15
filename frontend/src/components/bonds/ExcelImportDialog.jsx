import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Box, TextField, Typography, LinearProgress,
  Alert, List, ListItem, ListItemText, Chip
} from '@mui/material';
import { CloudUpload, CheckCircle, Error } from '@mui/icons-material';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function ExcelImportDialog({ open, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [purchaseDate, setPurchaseDate] = useState('');
  const [bondType, setBondType] = useState('2-Year Bond');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      toast.error('Please select an Excel file');
      return;
    }

    setUploading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Build query params
      const params = new URLSearchParams();
      if (purchaseDate) {
        params.append('purchase_date', purchaseDate);
      }
      params.append('bond_type_name', bondType);

      const response = await client.post(
        `/bonds/import-excel?${params.toString()}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
      toast.success('Import completed successfully!');

      // Refresh the bonds list after successful import
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Import failed:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to import Excel file';
      toast.error(errorMsg);
      setResult({
        success: false,
        message: errorMsg,
        statistics: { errors: [errorMsg] }
      });
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setPurchaseDate('');
    setBondType('2-Year Bond');
    setResult(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Import Bond Purchases from Excel</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {/* File Upload */}
          <Box sx={{ mb: 3 }}>
            <input
              accept=".xlsx,.xls"
              style={{ display: 'none' }}
              id="excel-file-upload"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="excel-file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUpload />}
                fullWidth
              >
                {file ? file.name : 'Select Excel File'}
              </Button>
            </label>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Supported formats: .xlsx, .xls
            </Typography>
          </Box>

          {/* Purchase Date */}
          <TextField
            fullWidth
            label="Purchase Date"
            type="date"
            value={purchaseDate}
            onChange={(e) => setPurchaseDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            helperText="Leave empty to use today's date"
            sx={{ mb: 2 }}
          />

          {/* Bond Type */}
          <TextField
            fullWidth
            label="Bond Type"
            value={bondType}
            onChange={(e) => setBondType(e.target.value)}
            select
            SelectProps={{ native: true }}
            sx={{ mb: 2 }}
          >
            <option value="2-Year Bond">2-Year Bond</option>
            <option value="5-Year Bond">5-Year Bond</option>
            <option value="15-Year Bond">15-Year Bond</option>
          </TextField>

          {/* Upload Progress */}
          {uploading && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Processing Excel file...
              </Typography>
            </Box>
          )}

          {/* Import Result */}
          {result && (
            <Box sx={{ mt: 3 }}>
              {result.success ? (
                <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2 }}>
                  {result.message}
                </Alert>
              ) : (
                <Alert severity="error" icon={<Error />} sx={{ mb: 2 }}>
                  {result.message}
                </Alert>
              )}

              {/* Statistics */}
              {result.statistics && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Import Summary
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    <Chip
                      label={`Users Created: ${result.statistics.users_created || 0}`}
                      color="success"
                      size="small"
                    />
                    <Chip
                      label={`Users Updated: ${result.statistics.users_updated || 0}`}
                      color="info"
                      size="small"
                    />
                    <Chip
                      label={`Bonds Created: ${result.statistics.bonds_created || 0}`}
                      color="primary"
                      size="small"
                    />
                    {result.statistics.errors?.length > 0 && (
                      <Chip
                        label={`Errors: ${result.statistics.errors.length}`}
                        color="error"
                        size="small"
                      />
                    )}
                  </Box>

                  {/* Error List */}
                  {result.statistics.errors?.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" color="error" gutterBottom>
                        Errors Encountered
                      </Typography>
                      <List dense sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'background.paper' }}>
                        {result.statistics.errors.map((error, index) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={error}
                              primaryTypographyProps={{ variant: 'body2', color: 'error' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Box>
              )}
            </Box>
          )}

          {/* Instructions */}
          {!result && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                <strong>Excel File Requirements:</strong>
              </Typography>
              <Typography variant="body2" component="div">
                • First row should be headers (row 2 contains data)
                <br />
                • Required columns: No, First Name, Last Name, Email, Bond Shares, FACE Value , Discount Value Paid on Maturity
                <br />
                • Default password for new users: <strong>change123</strong>
              </Typography>
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          {result ? 'Close' : 'Cancel'}
        </Button>
        {!result && (
          <Button
            onClick={handleImport}
            variant="contained"
            disabled={!file || uploading}
          >
            Import
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
