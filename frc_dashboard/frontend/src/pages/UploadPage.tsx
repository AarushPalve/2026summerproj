import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { uploadMatchData } from '../services/api';

const UploadPage: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [uploadResults, setUploadResults] = useState<{
    file: File;
    success: boolean;
    message: string;
  }[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
    setError(null);
  }, []);

  const removeFile = (fileToRemove: File) => {
    setFiles(files.filter(file => file !== fileToRemove));
  };

  const clearAllFiles = () => {
    setFiles([]);
    setUploadResults([]);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('No files selected for upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setUploadResults([]);

    try {
      const results = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        try {
          setUploadProgress(((i + 1) / files.length) * 100);

          const response = await uploadMatchData(file);
          results.push({
            file,
            success: true,
            message: response.message || 'File uploaded successfully'
          });
        } catch (err) {
          results.push({
            file,
            success: false,
            message: err instanceof Error ? err.message : 'Upload failed'
          });
        }
      }

      setUploadResults(results);

      // Check if all uploads failed
      const allFailed = results.every(r => !r.success);
      if (allFailed) {
        setError('All file uploads failed');
      }

    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Upload process failed';
      setError(errorMessage);
    } finally {
      setUploadProgress(100);
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    multiple: true,
    maxFiles: 10,
    maxSize: 10 * 1024 * 1024 // 10MB max per file
  });

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Match Data
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Upload
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Upload FRC match data files in CSV or JSON format. The system will automatically process
          the data and update team metrics, predictions, and statistics.
        </Typography>

        {/* File Upload Zone */}
        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed',
            borderColor: 'primary.main',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            bgcolor: 'action.hover',
            transition: 'all 0.3s',
            '&:hover': {
              bgcolor: 'action.selected',
              borderColor: 'primary.dark'
            },
            ...(isDragActive && {
              bgcolor: 'primary.light',
              borderColor: 'primary.dark'
            })
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to browse'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: CSV, JSON (Max 10MB per file, max 10 files)
          </Typography>
        </Box>

        {/* File List */}
        {files.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Selected Files ({files.length})
            </Typography>
            <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto' }}>
              <List dense>
                {files.map((file, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton edge="end" onClick={() => removeFile(file)}>
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      {file.type === 'text/csv' || file.name.endsWith('.csv') ?
                        <Typography variant="body2" sx={{ width: 40, bgcolor: 'success.light', p: 1, borderRadius: 1 }}>
                          CSV
                        </Typography> :
                        <Typography variant="body2" sx={{ width: 40, bgcolor: 'info.light', p: 1, borderRadius: 1 }}>
                          JSON
                        </Typography>}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={`${(file.size / 1024).toFixed(1)} KB`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
              <Button
                variant="text"
                color="error"
                onClick={clearAllFiles}
                disabled={uploading}
                startIcon={<DeleteIcon />}
              >
                Clear All
              </Button>
            </Box>
          </Box>
        )}

        {/* Upload Button */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={uploading || files.length === 0}
            startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
            size="large"
          >
            {uploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </Box>

        {/* Upload Progress */}
        {uploading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Upload Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={uploadProgress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" display="block" textAlign="right" sx={{ mt: 0.5 }}>
              {Math.round(uploadProgress)}%
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Upload Results
          </Typography>

          {uploadResults.map((result, index) => (
            <Alert
              key={index}
              severity={result.success ? 'success' : 'error'}
              icon={result.success ? <CheckCircleIcon /> : <ErrorIcon />}
              sx={{ mb: 1 }}
              action={
                <IconButton color="inherit" size="small">
                  <InfoIcon />
                </IconButton>
              }
            >
              <strong>{result.file.name}</strong>: {result.message}
            </Alert>
          ))}

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2">
              {uploadResults.filter(r => r.success).length} of {uploadResults.length} files uploaded successfully
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={clearAllFiles}
              startIcon={<RefreshIcon />}
            >
              Clear Results
            </Button>
          </Box>
        </Paper>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Information Section */}
      <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload Instructions
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>Supported File Formats:</strong>
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="CSV files with FRC match data" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">•</Typography></ListItemIcon>
            <ListItemText primary="JSON files with match results" />
          </ListItem>
        </List>"

        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
          <strong>Data Requirements:</strong>
        </Typography>
        <Typography variant="body2" paragraph>
          Files should contain match information including team numbers, scores, and match details.
          The system will automatically extract and process relevant data.
        </Typography>

        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
          <strong>Processing:</strong> After upload, the system will:
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon><Typography variant="body2">1.</Typography></ListItemIcon>
            <ListItemText primary="Parse and validate the data" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">2.</Typography></ListItemIcon>
            <ListItemText primary="Update team metrics (EPA, OPR, cOPR)" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">3.</Typography></ListItemIcon>
            <ListItemText primary="Recalculate predictions and statistics" />
          </ListItem>
          <ListItem>
            <ListItemIcon><Typography variant="body2">4.</Typography></ListItemIcon>
            <ListItemText primary="Sync data across the dashboard" />
          </ListItem>
        </List>
      </Paper>
    </Box>
  );
};

export default UploadPage;