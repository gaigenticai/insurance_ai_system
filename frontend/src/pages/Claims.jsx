import React, { useState } from 'react';
import api from '../api';
import Chatbot from '../components/Chatbot';

function Claims() {
  const [claimId, setClaimId] = useState('');
  const [description, setDescription] = useState('');
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/run/claims', { claim_id: claimId, description });
      setResponse(res.data);
    } catch (err) {
      setResponse({ status: 'error', message: err.message });
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Claims</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Claim ID:</label>
          <input value={claimId} onChange={e => setClaimId(e.target.value)} title="Unique claim identifier" />
        </div>
        <div>
          <label>Description:</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} title="Claim details" />
        </div>
        <button type="submit">Submit</button>
      </form>
      {response && (
        <pre>{JSON.stringify(response, null, 2)}</pre>
      )}
      <Chatbot />
    </div>
  );
}

export default Claims;
