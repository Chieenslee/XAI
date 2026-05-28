export default function Sidebar({ currentPage, setCurrentPage }) {
  const navs = [
    { id: 'dashboard', label: 'Bảng Điều khiển', icon: <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /> },
    { id: 'diagnosis', label: 'Chẩn đoán AI', icon: <><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></> },
    { id: 'about', label: 'Về Hệ thống', icon: <><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></> }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-title">MedAI Vision</div>
        <div className="sidebar-brand-sub">XAI Medical Imaging System</div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '8px' }}>
        {navs.map(nav => (
          <div key={nav.id}
               className={`nav-item ${currentPage === nav.id ? 'active' : ''}`}
               onClick={() => setCurrentPage(nav.id)}>
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              {nav.icon}
            </svg>
            {nav.label}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="status-row">
          <div className="status-dot"></div> Backend API Online
        </div>
        <div className="status-row">
          <div className="status-dot" style={{animationDelay:'0.5s',boxShadow:'none'}}></div> DenseNet-121 Loaded
        </div>
        <div className="sidebar-version">v2.0.0 · Antigravity AI</div>
      </div>
    </div>
  );
}
