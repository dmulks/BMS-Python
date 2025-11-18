import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function BozStatementUpload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      alert('Please select a CSV file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setError(null);
      const response = await api.post('/api/v1/admin/boz-statement-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
      setFile(null);
      // Reset file input
      document.getElementById('file-input').value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">BOZ Statement Upload</h1>

      <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
        <h3 className="font-semibold mb-2">Instructions</h3>
        <p className="text-sm mb-2">
          Upload a CSV file from Bank of Zambia containing expected payment totals.
          This will update the expected values for payment events to compare against calculated amounts.
        </p>
        <p className="text-sm font-mono bg-white p-2 rounded">
          CSV Format:<br />
          event_id,expected_total_net_maturity,expected_total_net_coupon<br />
          3,1500000.50,0<br />
          4,0,280000.75
        </p>
      </div>

      <div className="bg-white shadow rounded p-6 mb-6">
        <form onSubmit={handleUpload}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Select BOZ Statement CSV File
            </label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50 focus:outline-none p-2"
            />
          </div>

          {file && (
            <div className="mb-4 p-3 bg-gray-50 rounded">
              <p className="text-sm">
                <strong>Selected file:</strong> {file.name}
              </p>
              <p className="text-sm text-gray-600">
                Size: {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={!file || uploading}
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-6">
          <h3 className="font-semibold text-red-800 mb-2">Error</h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-white shadow rounded p-6">
          <h2 className="text-xl font-bold mb-4">Upload Results</h2>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-600">Successful Updates</p>
              <p className="text-3xl font-bold text-green-900">{result.successful_updates}</p>
            </div>
            <div className="bg-red-50 p-4 rounded">
              <p className="text-sm text-gray-600">Failed Updates</p>
              <p className="text-3xl font-bold text-red-900">{result.failed_updates}</p>
            </div>
          </div>

          {result.errors && result.errors.length > 0 && (
            <div>
              <h3 className="font-semibold text-red-800 mb-2">Errors ({result.errors.length})</h3>
              <div className="bg-red-50 rounded p-4 max-h-64 overflow-y-auto">
                <ul className="text-sm text-red-700 space-y-1">
                  {result.errors.map((error, idx) => (
                    <li key={idx} className="font-mono">{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {result.successful_updates > 0 && (
            <div className="mt-6">
              <button
                onClick={() => navigate('/admin/audit')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                View Audit Report →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BozStatementUpload;