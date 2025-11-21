import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function BondDetailTest() {
  const { bondId } = useParams();
  const navigate = useNavigate();
  const [bond, setBond] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [bondId]);

  const fetchData = async () => {
    try {
      const [bondRes, eventsRes] = await Promise.all([
        api.get('/admin/bond-issues'),
        api.get(`/bonds/${bondId}/events`)
      ]);

      const foundBond = bondRes.data.find(b => b.id === parseInt(bondId));
      setBond(foundBond);
      setEvents(eventsRes.data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!bond) return <div>Bond not found</div>;

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '32px', marginBottom: '20px' }}>{bond.issue_name}</h1>

      <h2 style={{ fontSize: '24px', marginTop: '40px', marginBottom: '20px' }}>
        Payment Events ({events.length})
      </h2>

      {events.map((event) => (
        <div key={event.event_id} style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => alert('Event ID: ' + event.event_id)}
              style={{
                fontSize: '24px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '8px 16px',
                cursor: 'pointer'
              }}
            >
              ▶
            </button>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                {event.event_name}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {event.payment_date} • BOZ Award: ${event.boz_award_amount.toLocaleString()}
              </div>
            </div>
            <span style={{
              background: event.event_type === 'DISCOUNT_MATURITY' ? '#fce7f3' : '#dbeafe',
              color: event.event_type === 'DISCOUNT_MATURITY' ? '#9333ea' : '#2563eb',
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '12px'
            }}>
              {event.event_type}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default BondDetailTest;
