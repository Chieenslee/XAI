import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Diagnosis from './pages/Diagnosis';
import About from './pages/About';
import './index.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="layout">
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
