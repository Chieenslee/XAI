import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Diagnosis from './pages/Diagnosis';
import About from './pages/About';
import './index.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="layout">
      <Toaster position="bottom-right" toastOptions={{ style: { background: '#081020', color: '#e0eaf4', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '12px' } }} />
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="main">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'diagnosis' && <Diagnosis />}
        {currentPage === 'about' && <About />}
      </main>
    </div>
  );
}

export default App;
