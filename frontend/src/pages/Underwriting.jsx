import React, { useState } from 'react';
import api from '../api';
import Chatbot from '../components/Chatbot';

function Underwriting() {
  const [name, setName] = useState('');
  const [age, setAge] = useState(30);
  const [notes, setNotes] = useState('');
  const [files, setFiles] = useState([]);
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('applicant_name', name);
    formData.append('age', age);
    formData.append('notes', notes);
    files.forEach((f, idx) => formData.append(`file_${idx}`, f));
    try {
      const res = await api.post('/run/underwriting', formData);
      setResponse(res.data);
    } catch (err) {
      setResponse({ status: 'error', message: err.message });
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Underwriting</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input value={name} onChange={e => setName(e.target.value)} title="Applicant full name" />
        </div>
        <div>
          <label>Age:</label>
          <input type="number" value={age} onChange={e => setAge(e.target.value)} title="Applicant age" />
        </div>
        <div>
          <label>Notes:</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} title="Additional notes" />
        </div>
        <div>
          <label>Documents:</label>
          <input type="file" multiple onChange={e => setFiles(Array.from(e.target.files))} title="Upload PDFs or images" />
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

export default Underwriting;
