import { useState, useEffect } from 'react';

export default function DeveloperLogModal({ onClose }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:8000/history');
      if (!res.ok) throw new Error("Failed to fetch logs");
      const data = await res.json();
      if (data.success) {
        setLogs(data.data);
      } else {
        throw new Error(data.detail);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    
    // Auto refresh every 5 seconds for real-time feel
    const interval = setInterval(() => {
      fetchLogs();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="modal-overlay" style={{ zIndex: 9999 }}>
      <div className="modal-container" style={{ maxWidth: '1000px', height: '80vh' }}>
        
        <button className="modal-close-btn" onClick={onClose} title="Đóng Developer Logs">
          ✕
        </button>

        <div style={{ padding: '32px 36px 16px', borderBottom: '1px solid rgba(0, 212, 255, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="modal-logo" style={{ background: 'rgba(162, 155, 254, 0.15)', color: '#a29bfe' }}>
              🛠️ DEV MODE
            </div>
            <h2 className="modal-title">Live System Logs & History</h2>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>
            Giám sát luồng dữ liệu (Data Pipeline), kết nối Database và lịch sử chẩn đoán thời gian thực. (Tự động cập nhật 5s/lần)
          </p>
        </div>

        <div style={{ padding: '24px 36px', overflowY: 'auto', flex: 1, fontFamily: '"JetBrains Mono", monospace' }}>
          {loading && logs.length === 0 && <div style={{ color: 'var(--cyan)' }}>Loading system records...</div>}
          {error && <div style={{ color: '#ff6b6b' }}>Error: {error}</div>}
          
          {!loading && logs.length === 0 && (
            <div style={{ color: 'var(--text-muted)' }}>Chưa có bản ghi (Record) nào trong hệ thống.</div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {logs.map(log => (
              <div key={log.id} style={{ 
                background: 'rgba(0,0,0,0.4)', 
                border: '1px solid rgba(255,255,255,0.08)', 
                borderRadius: '8px', 
                padding: '16px',
                fontSize: '0.85rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#a29bfe', fontWeight: 'bold' }}>
                  <span>[RECORD #{log.id}] - {log.timestamp}</span>
                  <span style={{ color: log.prediction_label.includes('Bình thường') ? '#00cec9' : '#ff6b6b' }}>
                    {log.prediction_label} ({log.confidence_score}%)
                  </span>
                </div>
                
                <div style={{ color: '#00d4ff', marginBottom: '4px' }}>{'>'} Image Target: <span style={{ color: '#e0eaf4' }}>{log.image_path}</span></div>
                <div style={{ color: '#00d4ff', marginBottom: '4px' }}>{'>'} Clinical Notes (Multimodal Text): <span style={{ color: '#e0eaf4' }}>{log.clinical_notes || 'N/A'}</span></div>
                <div style={{ color: '#00d4ff', marginBottom: '4px' }}>{'>'} Heatmap Generated: <span style={{ color: '#e0eaf4' }}>{log.heatmap_path}</span></div>
                <div style={{ color: '#00d4ff' }}>{'>'} Status: <span style={{ color: '#00cec9' }}>SUCCESS (200 OK) - Saved to SQLite</span></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
