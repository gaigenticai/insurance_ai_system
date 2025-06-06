import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard';
import Underwriting from './Underwriting';
import Claims from './Claims';
import Actuarial from './Actuarial';

function App() {
  return (
    <Router>
      <nav style={{ padding: '1rem', background: '#f0f2f5' }}>
        <Link to="/" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link to="/underwriting" style={{ marginRight: '1rem' }}>Underwriting</Link>
        <Link to="/claims" style={{ marginRight: '1rem' }}>Claims</Link>
        <Link to="/actuarial">Actuarial</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/underwriting" element={<Underwriting />} />
        <Route path="/claims" element={<Claims />} />
        <Route path="/actuarial" element={<Actuarial />} />
      </Routes>
    </Router>
  );
}

export default App;
