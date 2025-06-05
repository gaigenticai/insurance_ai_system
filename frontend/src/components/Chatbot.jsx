import React, { useState } from 'react';
import api from '../api';

function Chatbot() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState([]);

  const ask = async () => {
    if (!question) return;
    try {
      const res = await api.post('/chatbot', { question });
      setHistory([...history, { speaker: 'You', text: question }, { speaker: 'Bot', text: res.data.answer }]);
      setQuestion('');
    } catch {
      setHistory([...history, { speaker: 'You', text: question }, { speaker: 'Bot', text: 'Error' }]);
      setQuestion('');
    }
  };

  return (
    <div style={{ border: '1px solid #ddd', padding: '0.5rem', marginTop: '1rem' }}>
      <h4>Chat with Assistant</h4>
      {history.slice(-6).map((msg, idx) => (
        <div key={idx}><strong>{msg.speaker}:</strong> {msg.text}</div>
      ))}
      <input value={question} onChange={e => setQuestion(e.target.value)} placeholder="Ask a question" />
      <button onClick={ask}>Send</button>
    </div>
  );
}

export default Chatbot;
