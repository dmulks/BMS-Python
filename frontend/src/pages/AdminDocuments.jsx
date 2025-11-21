import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Container,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  CircularProgress,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Download,
  Search,
  Description
} from '@mui/icons-material';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function AdminDocuments() {
  const { isAdmin } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (isAdmin) {
      fetchDocuments();
    }
  }, [isAdmin]);

  useEffect(() => {
    // Filter documents based on search term
    if (searchTerm) {
      const filtered = documents.filter(doc =>
        doc.document_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.user_first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.user_last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.user_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (doc.document_type && doc.document_type.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredDocuments(filtered);
    } else {
      setFilteredDocuments(documents);
    }
  }, [searchTerm, documents]);

  const fetchDocuments = async () => {
    try {
      const response = await client.get('/documents/all');
      setDocuments(response.data);
      setFilteredDocuments(response.data);
    } catch (error) {
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (documentId, documentName) => {
    try {
      const response = await client.get(`/documents/download/${documentId}`, {
        responseType: 'blob'
      });

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', documentName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Document downloaded successfully');
    } catch (error) {
      toast.error('Failed to download document');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const getFileIcon = (mimeType) => {
    if (!mimeType) return <Description />;
    if (mimeType.includes('pdf')) return <Description color="error" />;
    if (mimeType.includes('image')) return <Description color="primary" />;
    if (mimeType.includes('word')) return <Description color="info" />;
    return <Description />;
  };

  if (!isAdmin) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h5" color="error">
          Access Denied - Admin Only
        </Typography>
      </Container>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          All Member Documents
        </Typography>
        <Typography variant="body2" color="text.secondary">
          View and download documents submitted by all members
        </Typography>
      </Box>

      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Search by member name, email, document name, or type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Member</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Document Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Uploaded</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredDocuments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                    {searchTerm ? 'No documents match your search' : 'No documents uploaded yet'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredDocuments.map((doc) => (
                <TableRow key={doc.document_id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {doc.user_first_name} {doc.user_last_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {doc.user_email}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getFileIcon(doc.mime_type)}
                      {doc.document_name}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {doc.document_type ? (
                      <Chip label={doc.document_type} size="small" />
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        maxWidth: 200,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                      title={doc.description}
                    >
                      {doc.description || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>{formatFileSize(doc.file_size)}</TableCell>
                  <TableCell>
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleDownload(doc.document_id, doc.document_name)}
                      title="Download"
                    >
                      <Download />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Box mt={2}>
        <Typography variant="body2" color="text.secondary">
          Total: {filteredDocuments.length} document{filteredDocuments.length !== 1 ? 's' : ''}
          {searchTerm && ` (filtered from ${documents.length})`}
        </Typography>
      </Box>
    </Container>
  );
}
