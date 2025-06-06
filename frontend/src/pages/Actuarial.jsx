import React, { useState } from 'react';
import api from '../api';
import Chatbot from '../components/Chatbot';

function Actuarial() {
  const [analysisId, setAnalysisId] = useState('');
  const [source, setSource] = useState('');
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/run/actuarial', { analysis_id: analysisId, source });
      setResponse(res.data);
    } catch (err) {
      setResponse({ status: 'error', message: err.message });
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Actuarial</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Analysis ID:</label>
          <input value={analysisId} onChange={e => setAnalysisId(e.target.value)} title="Unique analysis identifier" />
        </div>
        <div>
          <label>Data Source:</label>
          <input value={source} onChange={e => setSource(e.target.value)} title="Path or URL to data" />
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

export default Actuarial;
