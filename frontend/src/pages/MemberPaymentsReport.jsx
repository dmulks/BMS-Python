import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function MemberPaymentsReport() {
  const { memberId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReport();
  }, [memberId]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/members/${memberId}/payments`);
      setReport(response.data);
    } catch (err) {
      setError('Failed to load payments report');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4">Loading report...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!report) return <div className="p-4">No report available</div>;

  return (
    <div className="p-6">
      <button
        onClick={() => navigate('/members')}
        className="mb-4 text-blue-600 hover:text-blue-800"
      >
        ← Back to Members
      </button>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">Member Payments Report</h1>
      <div className="bg-gray-50 p-4 rounded mb-6">
        <p className="text-lg"><strong>Member:</strong> {report.member_name}</p>
        <p className="text-lg"><strong>Email:</strong> {report.member_email}</p>
        <p className="text-lg"><strong>Total Payments:</strong> {report.payment_count}</p>
      </div>

      {/* Summary Totals */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm text-gray-600">Total BOZ Award</p>
          <p className="text-xl font-bold text-blue-900">${report.totals.total_boz_award_value.toLocaleString()}</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <p className="text-sm text-gray-600">Total Net Discount</p>
          <p className="text-xl font-bold text-green-900">${report.totals.total_net_discount_value.toLocaleString()}</p>
        </div>
        <div className="bg-purple-50 p-4 rounded">
          <p className="text-sm text-gray-600">Total Net Maturity</p>
          <p className="text-xl font-bold text-purple-900">${report.totals.total_net_maturity_coupon.toLocaleString()}</p>
        </div>
        <div className="bg-orange-50 p-4 rounded">
          <p className="text-sm text-gray-600">Total Net Coupon</p>
          <p className="text-xl font-bold text-orange-900">${report.totals.total_net_coupon_payment.toLocaleString()}</p>
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-white shadow overflow-x-auto rounded">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bond</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">BOZ Award</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Discount</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Maturity</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Coupon</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {report.payments.length === 0 ? (
              <tr>
                <td colSpan="8" className="px-4 py-4 text-center text-gray-500">
                  No payments found
                </td>
              </tr>
            ) : (
              report.payments.map((payment) => (
                <tr key={payment.payment_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">{payment.event_name}</td>
                  <td className="px-4 py-3">{payment.bond_name}</td>
                  <td className="px-4 py-3">{payment.payment_date}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded ${
                      payment.event_type === 'DISCOUNT_MATURITY' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {payment.event_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">${payment.boz_award_value.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">${payment.net_discount_value.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-semibold">${payment.net_maturity_coupon.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-semibold">${payment.net_coupon_payment.toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default MemberPaymentsReport;