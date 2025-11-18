import { useState, useEffect } from 'react';
import api from '../api/client';

function AdminAuditReport() {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAuditReport();
  }, []);

  const fetchAuditReport = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/audit');
      setAuditData(response.data);
    } catch (err) {
      setError('Failed to load audit report');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4">Loading audit report...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!auditData) return <div className="p-4">No audit data available</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Audit Report</h1>

      {/* Summary */}
      <div className="bg-white shadow rounded p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Overall Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Events</p>
            <p className="text-2xl font-bold">{auditData.summary.total_events}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Events with Discrepancies</p>
            <p className="text-2xl font-bold text-red-600">{auditData.summary.events_with_discrepancies}</p>
          </div>
          <div className={auditData.summary.has_overall_discrepancy ? 'bg-red-50 p-2 rounded' : ''}>
            <p className="text-sm text-gray-600">Overall Status</p>
            <p className={`text-2xl font-bold ${auditData.summary.has_overall_discrepancy ? 'text-red-600' : 'text-green-600'}`}>
              {auditData.summary.has_overall_discrepancy ? 'DISCREPANCY' : 'MATCHED'}
            </p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="border-t pt-4">
            <h3 className="font-semibold mb-2">Maturity Totals</h3>
            <p className="text-sm">Calculated: <span className="font-bold">${auditData.summary.total_calculated_net_maturity.toLocaleString()}</span></p>
            <p className="text-sm">Expected: <span className="font-bold">${auditData.summary.total_expected_net_maturity.toLocaleString()}</span></p>
            <p className={`text-sm font-bold ${Math.abs(auditData.summary.total_maturity_difference) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
              Difference: ${auditData.summary.total_maturity_difference.toLocaleString()}
            </p>
          </div>
          <div className="border-t pt-4">
            <h3 className="font-semibold mb-2">Coupon Totals</h3>
            <p className="text-sm">Calculated: <span className="font-bold">${auditData.summary.total_calculated_net_coupon.toLocaleString()}</span></p>
            <p className="text-sm">Expected: <span className="font-bold">${auditData.summary.total_expected_net_coupon.toLocaleString()}</span></p>
            <p className={`text-sm font-bold ${Math.abs(auditData.summary.total_coupon_difference) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
              Difference: ${auditData.summary.total_coupon_difference.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Event-level details */}
      <div className="bg-white shadow overflow-x-auto rounded">
        <h2 className="text-xl font-bold p-6 border-b">Event-Level Details</h2>
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bond</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Calc Maturity</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Exp Maturity</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Mat Diff</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Calc Coupon</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Exp Coupon</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cpn Diff</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {auditData.report.length === 0 ? (
              <tr>
                <td colSpan="10" className="px-4 py-4 text-center text-gray-500">
                  No events to audit
                </td>
              </tr>
            ) : (
              auditData.report.map((event) => (
                <tr key={event.event_id} className={event.has_discrepancy ? 'bg-red-50' : 'hover:bg-gray-50'}>
                  <td className="px-4 py-3">
                    <div className="font-medium">{event.event_name}</div>
                    <div className="text-xs text-gray-500">{event.event_type}</div>
                  </td>
                  <td className="px-4 py-3">{event.bond_name}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{event.payment_date}</td>
                  <td className="px-4 py-3 text-right">${event.calculated_net_maturity.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">${event.expected_net_maturity.toLocaleString()}</td>
                  <td className={`px-4 py-3 text-right font-semibold ${Math.abs(event.maturity_difference) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
                    ${event.maturity_difference.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right">${event.calculated_net_coupon.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">${event.expected_net_coupon.toLocaleString()}</td>
                  <td className={`px-4 py-3 text-right font-semibold ${Math.abs(event.coupon_difference) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
                    ${event.coupon_difference.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 text-xs rounded font-semibold ${
                      event.has_discrepancy ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {event.has_discrepancy ? 'DIFF' : 'OK'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminAuditReport;