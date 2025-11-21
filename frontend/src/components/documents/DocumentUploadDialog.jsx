import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Typography,
  LinearProgress,
  Alert
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import client from '../../api/client';
import toast from 'react-hot-toast';

const DOCUMENT_TYPES = [
  { value: 'ID', label: 'National ID / Passport' },
  { value: 'Proof of Address', label: 'Proof of Address' },
  { value: 'Bank Statement', label: 'Bank Statement' },
  { value: 'Payslip', label: 'Payslip' },
  { value: 'Tax Document', label: 'Tax Document' },
  { value: 'Other', label: 'Other' }
];

export default function DocumentUploadDialog({ open, onClose, onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentType, setDocumentType] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (documentType) formData.append('document_type', documentType);
    if (description) formData.append('description', description);

    try {
      await client.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success('Document uploaded successfully!');
      handleClose();
      if (onSuccess) onSuccess();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to upload document';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setDocumentType('');
    setDescription('');
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Document</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {error && <Alert severity="error">{error}</Alert>}

          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUpload />}
            sx={{ py: 2 }}
          >
            {selectedFile ? selectedFile.name : 'Choose File'}
            <input
              type="file"
              hidden
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            />
          </Button>

          {selectedFile && (
            <Typography variant="body2" color="text.secondary">
              Size: {(selectedFile.size / 1024).toFixed(2)} KB
            </Typography>
          )}

          <TextField
            select
            label="Document Type"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            fullWidth
          >
            {DOCUMENT_TYPES.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Description (Optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
            fullWidth
            placeholder="Add any additional notes about this document..."
          />

          {uploading && <LinearProgress />}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!selectedFile || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
