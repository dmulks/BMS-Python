import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function BondDetail() {
  const { bondId } = useParams();
  const navigate = useNavigate();
  const [bond, setBond] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventForm, setEventForm] = useState({
    event_type: 'COUPON_SEMI_ANNUAL',
    event_name: '',
    payment_date: '',
    calculation_period: '',
    boz_award_amount: 0
  });

  useEffect(() => {
    fetchBondDetails();
    fetchEvents();
  }, [bondId]);

  const fetchBondDetails = async () => {
    try {
      // Get bond from admin/bond-issues endpoint
      const response = await api.get('/api/v1/admin/bond-issues');
      const foundBond = response.data.find(b => b.id === parseInt(bondId));
      if (foundBond) {
        setBond(foundBond);
      }
    } catch (err) {
      setError('Failed to load bond details');
      console.error(err);
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await api.get(`/api/v1/bonds/${bondId}/events`);
      setEvents(response.data);
    } catch (err) {
      setError('Failed to load payment events');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/api/v1/bonds/${bondId}/events`, eventForm);
      setShowEventForm(false);
      setEventForm({
        event_type: 'COUPON_SEMI_ANNUAL',
        event_name: '',
        payment_date: '',
        calculation_period: '',
        boz_award_amount: 0
      });
      fetchEvents();
    } catch (err) {
      alert('Failed to create event: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handlePreview = (eventId) => {
    navigate(`/bonds/${bondId}/events/${eventId}/preview`);
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!bond) return <div className="p-4">Bond not found</div>;

  return (
    <div className="p-6">
      <div className="mb-6">
        <button
          onClick={() => navigate('/bonds')}
          className="mb-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Bonds
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">{bond.issue_name}</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded">
          <div>
            <p className="text-sm text-gray-600">Issuer</p>
            <p className="font-semibold">{bond.issuer}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Bond Type</p>
            <p className="font-semibold">{bond.bond_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Coupon Rate</p>
            <p className="font-semibold">{(bond.coupon_rate * 100).toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Discount Rate</p>
            <p className="font-semibold">{(bond.discount_rate * 100).toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Issue Date</p>
            <p className="font-semibold">{bond.issue_date}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Maturity Date</p>
            <p className="font-semibold">{bond.maturity_date}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Holdings Count</p>
            <p className="font-semibold">{bond.holdings_count}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Face Value</p>
            <p className="font-semibold">${bond.total_face_value.toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Payment Events</h2>
          <button
            onClick={() => setShowEventForm(!showEventForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {showEventForm ? 'Cancel' : 'Create Event'}
          </button>
        </div>

        {showEventForm && (
          <form onSubmit={handleCreateEvent} className="mb-6 p-4 bg-gray-50 rounded">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Event Type</label>
                <select
                  value={eventForm.event_type}
                  onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="COUPON_SEMI_ANNUAL">Semi-Annual Coupon</option>
                  <option value="DISCOUNT_MATURITY">Maturity</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Event Name</label>
                <input
                  type="text"
                  value={eventForm.event_name}
                  onChange={(e) => setEventForm({ ...eventForm, event_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Payment Date</label>
                <input
                  type="date"
                  value={eventForm.payment_date}
                  onChange={(e) => setEventForm({ ...eventForm, payment_date: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">BOZ Award Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={eventForm.boz_award_amount}
                  onChange={(e) => setEventForm({ ...eventForm, boz_award_amount: parseFloat(e.target.value) })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-1">Calculation Period</label>
                <input
                  type="text"
                  value={eventForm.calculation_period}
                  onChange={(e) => setEventForm({ ...eventForm, calculation_period: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., Jan-Jun 2024"
                />
              </div>
            </div>
            <button
              type="submit"
              className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Create Event
            </button>
          </form>
        )}

        <div className="bg-white shadow overflow-hidden rounded">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">BOZ Award</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {events.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                    No payment events yet
                  </td>
                </tr>
              ) : (
                events.map((event) => (
                  <tr key={event.event_id}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">{event.event_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${
                        event.event_type === 'DISCOUNT_MATURITY' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {event.event_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{event.payment_date}</td>
                    <td className="px-6 py-4 whitespace-nowrap">${event.boz_award_amount.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handlePreview(event.event_id)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Preview/Generate →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default BondDetail;