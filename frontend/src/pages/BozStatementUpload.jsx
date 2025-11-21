import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Paper, Typography, Box, Grid, Card, CardContent,
  Button, Alert, CircularProgress, Divider, Chip, List, ListItem,
  ListItemIcon, ListItemText
} from '@mui/material';
import {
  CloudUpload, CheckCircle, Error as ErrorIcon,
  Info, ArrowForward, InsertDriveFile, Code, Warning
} from '@mui/icons-material';
import api from '../api/client';

function BozStatementUpload() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setResult(null);
        setError(null);
      } else {
        setError('Please upload a CSV file');
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setError(null);
      const response = await api.post('/admin/boz-statement-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleClearFile = () => {
    setFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={4}>
        <CloudUpload sx={{ fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight="bold" color="text.primary">
            BOZ Statement Upload
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Import expected payment totals from Bank of Zambia
          </Typography>
        </Box>
      </Box>

      {/* Instructions Panel */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
          border: '1px solid',
          borderColor: 'primary.light'
        }}
      >
        <Box display="flex" alignItems="flex-start" gap={2}>
          <Info sx={{ color: 'primary.main', mt: 0.5 }} />
          <Box flex={1}>
            <Typography variant="h6" fontWeight="bold" color="primary.dark" mb={1}>
              Instructions
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Upload a CSV file from Bank of Zambia containing expected payment totals.
              This will update the expected values for payment events to compare against calculated amounts in the Audit Report.
            </Typography>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: 'white',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'grey.300'
              }}
            >
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Code fontSize="small" color="action" />
                <Typography variant="subtitle2" fontWeight="bold">
                  CSV Format:
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  fontFamily: 'monospace',
                  bgcolor: 'grey.50',
                  p: 1.5,
                  borderRadius: 1,
                  fontSize: '0.8rem',
                  lineHeight: 1.8
                }}
              >
                event_id,expected_total_net_maturity,expected_total_net_coupon<br />
                3,1500000.50,0<br />
                4,0,280000.75
              </Typography>
            </Paper>
          </Box>
        </Box>
      </Paper>

      {/* Upload Section */}
      <Paper elevation={2} sx={{ p: 4, borderRadius: 2, mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          Upload File
        </Typography>

        <form onSubmit={handleUpload}>
          {/* Drag & Drop Zone */}
          <Box
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: '2px dashed',
              borderColor: dragActive ? 'primary.main' : file ? 'success.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: dragActive ? 'rgba(25, 118, 210, 0.08)' : file ? 'rgba(46, 125, 50, 0.08)' : 'grey.100',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'rgba(25, 118, 210, 0.08)'
              }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            {file ? (
              <Box>
                <InsertDriveFile sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
                <Typography variant="h6" color="success.main" fontWeight="medium">
                  {file.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Size: {(file.size / 1024).toFixed(2)} KB
                </Typography>
                <Button
                  size="small"
                  color="error"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClearFile();
                  }}
                  sx={{ mt: 1 }}
                >
                  Remove File
                </Button>
              </Box>
            ) : (
              <Box>
                <CloudUpload sx={{ fontSize: 48, color: dragActive ? 'primary.main' : 'grey.400', mb: 1 }} />
                <Typography variant="h6" color={dragActive ? 'primary.main' : 'text.secondary'}>
                  {dragActive ? 'Drop your file here' : 'Drag & drop your CSV file here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" mt={1}>
                  or click to browse
                </Typography>
                <Chip
                  label="CSV files only"
                  size="small"
                  variant="outlined"
                  sx={{ mt: 2 }}
                />
              </Box>
            )}
          </Box>

          {/* Upload Button */}
          <Box mt={3} display="flex" gap={2}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={!file || uploading}
              startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
              sx={{ px: 4 }}
            >
              {uploading ? 'Processing...' : 'Upload & Process'}
            </Button>
            {file && (
              <Button
                variant="outlined"
                size="large"
                onClick={handleClearFile}
                disabled={uploading}
              >
                Clear
              </Button>
            )}
          </Box>
        </form>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert
          severity="error"
          sx={{ mb: 4, borderRadius: 2 }}
          onClose={() => setError(null)}
        >
          <Typography fontWeight="medium">{error}</Typography>
        </Alert>
      )}

      {/* Results Section */}
      {result && (
        <Paper elevation={2} sx={{ borderRadius: 2, overflow: 'hidden' }}>
          {/* Results Header */}
          <Box
            sx={{
              p: 3,
              background: result.failed_updates === 0
                ? 'linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%)'
                : 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
              borderBottom: '1px solid',
              borderColor: 'divider'
            }}
          >
            <Box display="flex" alignItems="center" gap={2}>
              {result.failed_updates === 0 ? (
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              ) : (
                <Warning sx={{ fontSize: 40, color: 'warning.main' }} />
              )}
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  Upload Complete
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.successful_updates} record(s) processed successfully
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Results Stats */}
          <Box p={3}>
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} sm={6}>
                <Card
                  elevation={0}
                  sx={{
                    bgcolor: 'rgba(46, 125, 50, 0.08)',
                    border: '1px solid',
                    borderColor: 'success.light',
                    borderRadius: 2
                  }}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <CheckCircle color="success" />
                      <Typography variant="body2" color="text.secondary" fontWeight="medium">
                        Successful Updates
                      </Typography>
                    </Box>
                    <Typography variant="h3" fontWeight="bold" color="success.dark">
                      {result.successful_updates}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Card
                  elevation={0}
                  sx={{
                    bgcolor: result.failed_updates > 0 ? 'rgba(211, 47, 47, 0.08)' : 'grey.100',
                    border: '1px solid',
                    borderColor: result.failed_updates > 0 ? 'error.light' : 'grey.300',
                    borderRadius: 2
                  }}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <ErrorIcon color={result.failed_updates > 0 ? 'error' : 'disabled'} />
                      <Typography variant="body2" color="text.secondary" fontWeight="medium">
                        Failed Updates
                      </Typography>
                    </Box>
                    <Typography
                      variant="h3"
                      fontWeight="bold"
                      color={result.failed_updates > 0 ? 'error.dark' : 'text.disabled'}
                    >
                      {result.failed_updates}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Error List */}
            {result.errors && result.errors.length > 0 && (
              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="bold" color="error.main" mb={2}>
                  Errors ({result.errors.length})
                </Typography>
                <Paper
                  elevation={0}
                  sx={{
                    bgcolor: 'rgba(211, 47, 47, 0.08)',
                    border: '1px solid',
                    borderColor: 'error.light',
                    borderRadius: 2,
                    maxHeight: 200,
                    overflow: 'auto'
                  }}
                >
                  <List dense>
                    {result.errors.map((err, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <ErrorIcon fontSize="small" color="error" />
                        </ListItemIcon>
                        <ListItemText
                          primary={err}
                          primaryTypographyProps={{
                            variant: 'body2',
                            fontFamily: 'monospace',
                            color: 'error.dark'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}

            {/* Action Buttons */}
            <Divider sx={{ my: 3 }} />
            <Box display="flex" gap={2} flexWrap="wrap">
              {result.successful_updates > 0 && (
                <Button
                  variant="contained"
                  color="primary"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/admin/audit')}
                >
                  View Audit Report
                </Button>
              )}
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
                onClick={() => {
                  setResult(null);
                  setError(null);
                }}
              >
                Upload Another File
              </Button>
            </Box>
          </Box>
        </Paper>
      )}
    </Container>
  );
}

export default BozStatementUpload;
