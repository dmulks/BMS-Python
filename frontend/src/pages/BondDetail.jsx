import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Box, Typography, Button, Tabs, Tab } from '@mui/material';
import api from '../api/client';

function BondDetail() {
  const { bondId } = useParams();
  const navigate = useNavigate();
  const [bond, setBond] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('bond-info');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventPayments, setEventPayments] = useState({});
  const [loadingPayments, setLoadingPayments] = useState({});
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
      const response = await api.get('/admin/bond-issues');
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
      const response = await api.get(`/bonds/${bondId}/events`);
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
      await api.post(`/bonds/${bondId}/events`, eventForm);
      setEventForm({
        event_type: 'COUPON_SEMI_ANNUAL',
        event_name: '',
        payment_date: '',
        calculation_period: '',
        boz_award_amount: 0
      });
      fetchEvents();
      setActiveTab('payment-events');
      alert('Payment event created successfully!');
    } catch (err) {
      alert('Failed to create event: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handlePreview = (eventId) => {
    navigate(`/bonds/${bondId}/events/${eventId}/preview`);
  };

  const loadEventPayments = async (eventId) => {
    if (!eventPayments[eventId]) {
      setLoadingPayments(prev => ({ ...prev, [eventId]: true }));
      try {
        const response = await api.get(`/bonds/${bondId}/payments/preview?event_id=${eventId}`);
        setEventPayments(prev => ({ ...prev, [eventId]: response.data }));
      } catch (err) {
        console.error('Failed to load payment details:', err);
        const errorMsg = err.response?.data?.detail || err.message;
        alert('Failed to load payment details: ' + errorMsg);
      } finally {
        setLoadingPayments(prev => ({ ...prev, [eventId]: false }));
      }
    }
  };

  const handleEventClick = async (event) => {
    setSelectedEvent(event);
    setActiveTab('event-details');
    await loadEventPayments(event.event_id);
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!bond) return <div className="p-4">Bond not found</div>;

  const maturityEvents = events.filter(e => e.event_type === 'DISCOUNT_MATURITY');
  const couponEvents = events.filter(e => e.event_type === 'COUPON_SEMI_ANNUAL');

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Button
            onClick={() => navigate('/bonds')}
            sx={{ mb: 2 }}
          >
            ← Back to Bonds
          </Button>
          <Typography variant="h4" gutterBottom>
            {bond.issue_name}
          </Typography>
        </Box>

        {/* Tab Navigation */}
        <div style={{ backgroundColor: '#dbeafe', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderRadius: '8px', marginBottom: '24px', padding: '4px' }}>
          <div style={{ borderBottom: '2px solid #93c5fd' }}>
            <nav className="flex -mb-px" style={{ gap: '16px', paddingLeft: '8px' }}>
              <button
                onClick={() => setActiveTab('bond-info')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'bond-info'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Bond Information
              </button>
              <button
                onClick={() => setActiveTab('payment-events')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'payment-events'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Payment Events
              </button>
              <button
                onClick={() => setActiveTab('create-event')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'create-event'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                + Create Event
              </button>
              {maturityEvents.length > 0 && (
                <button
                  onClick={() => setActiveTab('maturity-payments')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'maturity-payments'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Maturity Payments
                </button>
              )}
              {couponEvents.length > 0 && (
                <button
                  onClick={() => setActiveTab('coupon-payments')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'coupon-payments'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Semi-Annual Coupon Payments
                </button>
              )}
              {selectedEvent && activeTab === 'event-details' && (
                <button
                  onClick={() => setActiveTab('event-details')}
                  className="px-6 py-4 text-sm font-medium border-b-2 border-blue-600 text-blue-600"
                >
                  {selectedEvent.event_name}
                </button>
              )}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white shadow-sm rounded-lg p-6">

          {/* Bond Information Tab */}
          {activeTab === 'bond-info' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Bond Information</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Issuer</td>
                      <td className="px-6 py-4 text-gray-900">{bond.issuer}</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Bond Type</td>
                      <td className="px-6 py-4 text-gray-900">{bond.bond_type}</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Coupon Rate</td>
                      <td className="px-6 py-4 text-gray-900">{(bond.coupon_rate * 100).toFixed(2)}%</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Discount Rate</td>
                      <td className="px-6 py-4 text-gray-900">{(bond.discount_rate * 100).toFixed(2)}%</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Issue Date</td>
                      <td className="px-6 py-4 text-gray-900">{bond.issue_date}</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Maturity Date</td>
                      <td className="px-6 py-4 text-gray-900">{bond.maturity_date}</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Holdings Count</td>
                      <td className="px-6 py-4 text-gray-900">{bond.holdings_count}</td>
                    </tr>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold text-gray-700 w-1/3">Total Face Value</td>
                      <td className="px-6 py-4 text-gray-900">${bond.total_face_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Payment Events Tab */}
          {activeTab === 'payment-events' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Payment Events</h2>
              {events.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No payment events created yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Event Name</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Payment Date</th>
                        <th className="px-6 py-3 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">BOZ Award</th>
                        <th className="px-6 py-3 text-center text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {events.map((event) => (
                        <tr key={event.event_id} className="hover:bg-blue-50 transition-colors">
                          <td className="px-6 py-4 font-semibold text-gray-900">{event.event_name}</td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                              event.event_type === 'DISCOUNT_MATURITY'
                                ? 'bg-purple-100 text-purple-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {event.event_type === 'DISCOUNT_MATURITY' ? 'Maturity' : 'Semi-Annual Coupon'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-900">{event.payment_date}</td>
                          <td className="px-6 py-4 text-right font-medium text-gray-900">
                            ${event.boz_award_amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <button
                              onClick={() => handleEventClick(event)}
                              className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 mr-2"
                            >
                              View Details
                            </button>
                            <button
                              onClick={() => handlePreview(event.event_id)}
                              className="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                            >
                              Generate Report
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Create Event Tab */}
          {activeTab === 'create-event' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Payment Event</h2>
              <form onSubmit={handleCreateEvent} className="max-w-2xl">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Event Type</label>
                    <select
                      value={eventForm.event_type}
                      onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="COUPON_SEMI_ANNUAL">Semi-Annual Coupon Payment</option>
                      <option value="DISCOUNT_MATURITY">Maturity Payment</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Event Name</label>
                    <input
                      type="text"
                      value={eventForm.event_name}
                      onChange={(e) => setEventForm({ ...eventForm, event_name: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Semi-Annual Coupon Payment Dec 2024"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Payment Date</label>
                    <input
                      type="date"
                      value={eventForm.payment_date}
                      onChange={(e) => setEventForm({ ...eventForm, payment_date: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">BOZ Award Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={eventForm.boz_award_amount}
                      onChange={(e) => setEventForm({ ...eventForm, boz_award_amount: parseFloat(e.target.value) })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Calculation Period</label>
                    <input
                      type="text"
                      value={eventForm.calculation_period}
                      onChange={(e) => setEventForm({ ...eventForm, calculation_period: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Jan-Jun 2024"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="mt-6 px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 shadow-sm"
                >
                  Create Payment Event
                </button>
              </form>
            </div>
          )}

          {/* Maturity Payments Tab */}
          {activeTab === 'maturity-payments' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Maturity Payments</h2>
              <div className="space-y-6">
                {maturityEvents.map((event) => {
                  const eventData = eventPayments[event.event_id];
                  return (
                    <div key={event.event_id} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-purple-50 px-6 py-4 border-b border-gray-200">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="text-lg font-bold text-gray-900">{event.event_name}</h3>
                            <p className="text-sm text-gray-600">{event.payment_date} • BOZ Award: ${event.boz_award_amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                          </div>
                          <button
                            onClick={() => loadEventPayments(event.event_id)}
                            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                          >
                            {eventData ? 'Refresh' : 'Load Details'}
                          </button>
                        </div>
                      </div>
                      {loadingPayments[event.event_id] ? (
                        <div className="p-8 text-center text-gray-500">Loading payment details...</div>
                      ) : eventData ? (
                        <div className="p-6">
                          {/* Summary */}
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-blue-50 p-4 rounded">
                              <p className="text-sm text-blue-700 font-medium">Total Members</p>
                              <p className="text-2xl font-bold text-blue-900">{eventData.summary.total_members}</p>
                            </div>
                            <div className="bg-orange-50 p-4 rounded">
                              <p className="text-sm text-orange-700 font-medium">Total Net Maturity Coupon</p>
                              <p className="text-2xl font-bold text-orange-900">${eventData.summary.total_net_maturity_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                            </div>
                          </div>
                          {/* Payment Table */}
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-50">
                                <tr>
                                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase">Member</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Shares</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Face Value</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Coupon at Maturity</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Less 15% WHT</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Less 1% BOZ</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-white uppercase bg-orange-600">Net Maturity Coupon</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {eventData.payments.map((payment, idx) => (
                                  <tr key={idx} className="hover:bg-orange-50">
                                    <td className="px-4 py-3">
                                      <div className="font-semibold text-gray-900">{payment.member_name}</div>
                                      <div className="text-xs text-gray-500">{payment.member_code}</div>
                                    </td>
                                    <td className="px-4 py-3 text-right text-gray-900">{payment.bond_shares.toLocaleString()}</td>
                                    <td className="px-4 py-3 text-right text-gray-900">${payment.member_face_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td className="px-4 py-3 text-right text-gray-900">${payment.gross_coupon_from_boz.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td className="px-4 py-3 text-right text-red-600">(${payment.withholding_tax.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                    <td className="px-4 py-3 text-right text-red-600">(${payment.boz_fee.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                    <td className="px-4 py-3 text-right font-bold text-orange-700 bg-orange-50">${payment.net_maturity_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Semi-Annual Coupon Payments Tab */}
          {activeTab === 'coupon-payments' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Semi-Annual Coupon Payments</h2>
              <div className="space-y-6">
                {couponEvents.map((event) => {
                  const eventData = eventPayments[event.event_id];
                  return (
                    <div key={event.event_id} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-blue-50 px-6 py-4 border-b border-gray-200">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="text-lg font-bold text-gray-900">{event.event_name}</h3>
                            <p className="text-sm text-gray-600">{event.payment_date} • BOZ Award: ${event.boz_award_amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                          </div>
                          <button
                            onClick={() => loadEventPayments(event.event_id)}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            {eventData ? 'Refresh' : 'Load Details'}
                          </button>
                        </div>
                      </div>
                      {loadingPayments[event.event_id] ? (
                        <div className="p-8 text-center text-gray-500">Loading payment details...</div>
                      ) : eventData ? (
                        <div className="p-6">
                          {/* Summary */}
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-blue-50 p-4 rounded">
                              <p className="text-sm text-blue-700 font-medium">Total Members</p>
                              <p className="text-2xl font-bold text-blue-900">{eventData.summary.total_members}</p>
                            </div>
                            <div className="bg-indigo-50 p-4 rounded">
                              <p className="text-sm text-indigo-700 font-medium">Total Net Coupon Payment</p>
                              <p className="text-2xl font-bold text-indigo-900">${eventData.summary.total_net_coupon_payment.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                            </div>
                          </div>
                          {/* Payment Table */}
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-50">
                                <tr>
                                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase">Member</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Shares</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Face Value</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Semi-Annual Coupon</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Less 15% WHT</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Less 1% BOZ</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-gray-700 uppercase">Less 2% Coop</th>
                                  <th className="px-4 py-3 text-right text-xs font-bold text-white uppercase bg-indigo-600">Net Coupon Payment</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {eventData.payments.map((payment, idx) => (
                                  <tr key={idx} className="hover:bg-indigo-50">
                                    <td className="px-4 py-3">
                                      <div className="font-semibold text-gray-900">{payment.member_name}</div>
                                      <div className="text-xs text-gray-500">{payment.member_code}</div>
                                    </td>
                                    <td className="px-4 py-3 text-right text-gray-900">{payment.bond_shares.toLocaleString()}</td>
                                    <td className="px-4 py-3 text-right text-gray-900">${payment.member_face_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td className="px-4 py-3 text-right text-gray-900">${payment.gross_coupon_from_boz.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td className="px-4 py-3 text-right text-red-600">(${payment.withholding_tax.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                    <td className="px-4 py-3 text-right text-red-600">(${payment.boz_fee.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                    <td className="px-4 py-3 text-right text-red-600">(${payment.coop_fee_on_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                    <td className="px-4 py-3 text-right font-bold text-indigo-700 bg-indigo-50">${payment.net_coupon_payment.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Individual Event Details Tab */}
          {activeTab === 'event-details' && selectedEvent && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedEvent.event_name}</h2>
              <p className="text-gray-600 mb-6">
                {selectedEvent.payment_date} • Type: {selectedEvent.event_type === 'DISCOUNT_MATURITY' ? 'Maturity Payment' : 'Semi-Annual Coupon'} • BOZ Award: ${selectedEvent.boz_award_amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </p>

              {loadingPayments[selectedEvent.event_id] ? (
                <div className="text-center py-12 text-gray-500">Loading payment details...</div>
              ) : eventPayments[selectedEvent.event_id] ? (
                <div>
                  {/* Summary Cards */}
                  <div className="grid grid-cols-4 gap-4 mb-8">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <p className="text-sm font-medium text-blue-700 mb-2">Total Members</p>
                      <p className="text-3xl font-bold text-blue-900">
                        {eventPayments[selectedEvent.event_id].summary.total_members}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                      <p className="text-sm font-medium text-green-700 mb-2">BOZ Award Total</p>
                      <p className="text-3xl font-bold text-green-900">
                        ${eventPayments[selectedEvent.event_id].summary.total_boz_award_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg">
                      <p className="text-sm font-medium text-orange-700 mb-2">Net Maturity Coupon</p>
                      <p className="text-3xl font-bold text-orange-900">
                        ${eventPayments[selectedEvent.event_id].summary.total_net_maturity_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                      </p>
                    </div>
                    <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-lg">
                      <p className="text-sm font-medium text-indigo-700 mb-2">Net Coupon Payment</p>
                      <p className="text-3xl font-bold text-indigo-900">
                        ${eventPayments[selectedEvent.event_id].summary.total_net_coupon_payment.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                      </p>
                    </div>
                  </div>

                  {/* Member Payments Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Member</th>
                          <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Shares</th>
                          <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Face Value</th>
                          {selectedEvent.event_type === 'DISCOUNT_MATURITY' ? (
                            <>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Coupon at Maturity</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Less 15% WHT</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Less 1% BOZ</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-white uppercase tracking-wider bg-orange-600">Net Maturity Coupon</th>
                            </>
                          ) : (
                            <>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Semi-Annual Coupon</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Less 15% WHT</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Less 1% BOZ</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Less 2% Coop</th>
                              <th className="px-6 py-4 text-right text-xs font-bold text-white uppercase tracking-wider bg-indigo-600">Net Coupon Payment</th>
                            </>
                          )}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {eventPayments[selectedEvent.event_id].payments.map((payment, idx) => (
                          <tr key={idx} className="hover:bg-blue-50 transition-colors">
                            <td className="px-6 py-4">
                              <div className="font-semibold text-gray-900">{payment.member_name}</div>
                              <div className="text-sm text-gray-500">{payment.member_code}</div>
                            </td>
                            <td className="px-6 py-4 text-right font-medium text-gray-900">{payment.bond_shares.toLocaleString()}</td>
                            <td className="px-6 py-4 text-right font-medium text-gray-900">${payment.member_face_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                            {selectedEvent.event_type === 'DISCOUNT_MATURITY' ? (
                              <>
                                <td className="px-6 py-4 text-right font-medium text-gray-900">${payment.gross_coupon_from_boz.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td className="px-6 py-4 text-right font-medium text-red-600">(${payment.withholding_tax.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                <td className="px-6 py-4 text-right font-medium text-red-600">(${payment.boz_fee.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                <td className="px-6 py-4 text-right font-bold text-orange-700 bg-orange-50">${payment.net_maturity_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                              </>
                            ) : (
                              <>
                                <td className="px-6 py-4 text-right font-medium text-gray-900">${payment.gross_coupon_from_boz.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td className="px-6 py-4 text-right font-medium text-red-600">(${payment.withholding_tax.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                <td className="px-6 py-4 text-right font-medium text-red-600">(${payment.boz_fee.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                <td className="px-6 py-4 text-right font-medium text-red-600">(${payment.coop_fee_on_coupon.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})</td>
                                <td className="px-6 py-4 text-right font-bold text-indigo-700 bg-indigo-50">${payment.net_coupon_payment.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                              </>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-6 flex justify-end">
                    <button
                      onClick={() => handlePreview(selectedEvent.event_id)}
                      className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 shadow-sm"
                    >
                      Generate Payment Report
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">No payment data available</div>
              )}
            </div>
          )}

        </div>

    </Container>
  );
}

export default BondDetail;