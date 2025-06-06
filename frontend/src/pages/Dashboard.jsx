import React, { useEffect, useState } from 'react';
import api from '../api';
import Chatbot from '../components/Chatbot';

function Dashboard() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    api.get('/status/recent')
      .then(res => setTasks(res.data.tasks || []))
      .catch(() => setTasks([]));
  }, []);

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Dashboard</h2>
      <ul>
        {tasks.map(task => (
          <li key={task.task_id}>{task.task_type} - {task.status}</li>
        ))}
      </ul>
      <Chatbot />
    </div>
  );
}

export default Dashboard;
