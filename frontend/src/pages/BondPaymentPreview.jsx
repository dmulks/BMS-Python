import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function BondPaymentPreview() {
  const { bondId, eventId } = useParams();
  const navigate = useNavigate();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchPreview();
  }, [bondId, eventId]);

  const fetchPreview = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/bonds/${bondId}/payments/preview?event_id=${eventId}`);
      setPreview(response.data);
    } catch (err) {
      setError('Failed to load payment preview');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!confirm('Generate payment records for all members? This will save the calculations to the database.')) {
      return;
    }

    try {
      setGenerating(true);
      const response = await api.post(`/api/v1/bonds/${bondId}/payments/generate?event_id=${eventId}`);
      alert(`Success! Generated ${response.data.payments_created} payment records.`);
      navigate(`/bonds/${bondId}`);
    } catch (err) {
      alert('Failed to generate payments: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleRecalculate = async () => {
    if (!confirm('Recalculate payments? This will delete existing payments and regenerate them.')) {
      return;
    }

    try {
      setGenerating(true);
      const response = await api.post(`/api/v1/bonds/${bondId}/payments/recalculate?event_id=${eventId}`);
      alert(`Success! Recalculated ${response.data.payments_created} payment records.`);
      fetchPreview();
    } catch (err) {
      alert('Failed to recalculate payments: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const exportToCSV = () => {
    if (!preview || !preview.payments) return;

    const headers = [
      'Member Code', 'Member Name', 'Bond Shares', 'Percentage Share', 'Face Value',
      'BOZ Award Value', 'Discount Value', 'Co-op Discount Fee', 'Net Discount Value',
      'Gross Coupon', 'WHT', 'BOZ Fee', 'Co-op Fee', 'Net Maturity Coupon', 'Net Coupon Payment'
    ];

    const rows = preview.payments.map(p => [
      p.member_code,
      p.member_name,
      p.bond_shares,
      p.percentage_share,
      p.member_face_value,
      p.boz_award_value,
      p.base_amount,
      p.coop_discount_fee,
      p.net_discount_value,
      p.gross_coupon_from_boz,
      p.withholding_tax,
      p.boz_fee,
      p.coop_fee_on_coupon,
      p.net_maturity_coupon,
      p.net_coupon_payment
    ]);

    const csvContent = [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `payment_preview_${eventId}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) return <div className="p-4">Loading preview...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!preview) return <div className="p-4">No preview available</div>;

  return (
    <div className="p-6">
      <div className="mb-6">
        <button
          onClick={() => navigate(`/bonds/${bondId}`)}
          className="mb-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Bond
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Preview</h1>
        <div className="bg-gray-50 p-4 rounded mb-4">
          <p className="text-lg"><strong>Bond:</strong> {preview.bond_name}</p>
          <p className="text-lg"><strong>Event:</strong> {preview.event_name}</p>
          <p className="text-lg"><strong>Type:</strong> {preview.event_type}</p>
          <p className="text-lg"><strong>Payment Date:</strong> {preview.payment_date}</p>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm text-gray-600">Total Members</p>
          <p className="text-2xl font-bold text-blue-900">{preview.summary.total_members}</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <p className="text-sm text-gray-600">BOZ Award</p>
          <p className="text-2xl font-bold text-green-900">${preview.summary.total_boz_award_value.toLocaleString()}</p>
        </div>
        <div className="bg-purple-50 p-4 rounded">
          <p className="text-sm text-gray-600">Net Discount</p>
          <p className="text-2xl font-bold text-purple-900">${preview.summary.total_net_discount_value.toLocaleString()}</p>
        </div>
        <div className="bg-orange-50 p-4 rounded">
          <p className="text-sm text-gray-600">Net Maturity Coupon</p>
          <p className="text-2xl font-bold text-orange-900">${preview.summary.total_net_maturity_coupon.toLocaleString()}</p>
        </div>
        <div className="bg-indigo-50 p-4 rounded">
          <p className="text-sm text-gray-600">Net Coupon Payment</p>
          <p className="text-2xl font-bold text-indigo-900">${preview.summary.total_net_coupon_payment.toLocaleString()}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-6 py-3 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
        >
          {generating ? 'Generating...' : 'Generate & Save Payments'}
        </button>
        <button
          onClick={handleRecalculate}
          disabled={generating}
          className="px-6 py-3 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:bg-gray-400"
        >
          {generating ? 'Recalculating...' : 'Recalculate Payments'}
        </button>
        <button
          onClick={exportToCSV}
          className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Export to CSV
        </button>
      </div>

      {/* Payments Table */}
      <div className="bg-white shadow overflow-x-auto rounded">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Member</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Shares</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">%</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Face Value</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">BOZ Award</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Discount</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gross Coupon</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Maturity</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Coupon</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {preview.payments.map((payment, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-4 py-3 whitespace-nowrap">
                  <div>
                    <div className="font-medium">{payment.member_name}</div>
                    <div className="text-xs text-gray-500">{payment.member_code}</div>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">{payment.bond_shares.toLocaleString()}</td>
                <td className="px-4 py-3 text-right">{payment.percentage_share.toFixed(4)}%</td>
                <td className="px-4 py-3 text-right">${payment.member_face_value.toLocaleString()}</td>
                <td className="px-4 py-3 text-right">${payment.boz_award_value.toLocaleString()}</td>
                <td className="px-4 py-3 text-right">${payment.net_discount_value.toLocaleString()}</td>
                <td className="px-4 py-3 text-right">${payment.gross_coupon_from_boz.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-semibold">${payment.net_maturity_coupon.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-semibold">${payment.net_coupon_payment.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default BondPaymentPreview;