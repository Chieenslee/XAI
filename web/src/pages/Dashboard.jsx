import LungModel from '../components/LungModel';

export default function Dashboard() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">🫁 MedAI Vision</h1>
        <p className="page-subtitle">Hệ thống Chẩn đoán X-quang Phổi tích hợp Trí tuệ Nhân tạo Giải thích được (XAI)</p>
      </div>

      <div style={{ display: 'flex', gap: '32px', marginBottom: '32px' }}>
        <div style={{ flex: '0 0 240px', background: 'rgba(0,212,255,0.02)', borderRadius: '20px', border: '1px solid rgba(0,212,255,0.1)' }}>
          <LungModel size={120} />
        </div>
        <div className="stats-grid" style={{ display: 'flex', gap: '16px', flex: 1 }}>
          <div className="stat-card glass-card" style={{ flex: 1, padding: '20px', borderRadius: '16px', background: 'rgba(255,255,255,0.05)' }}>
            <div className="stat-value" style={{ color: '#00d4ff', fontSize: '24px', fontWeight: 'bold' }}>81.46%</div>
            <div className="stat-label" style={{ fontSize: '12px', opacity: 0.7 }}>Độ chính xác (Test Set)</div>
          </div>
          <div className="stat-card glass-card" style={{ flex: 1, padding: '20px', borderRadius: '16px', background: 'rgba(255,255,255,0.05)' }}>
            <div className="stat-value" style={{ color: '#00ff88', fontSize: '24px', fontWeight: 'bold' }}>0.87</div>
            <div className="stat-label" style={{ fontSize: '12px', opacity: 0.7 }}>AUC-ROC Score</div>
          </div>
          <div className="stat-card glass-card" style={{ flex: 1, padding: '20px', borderRadius: '16px', background: 'rgba(255,255,255,0.05)' }}>
            <div className="stat-value" style={{ color: '#ff6b6b', fontSize: '24px', fontWeight: 'bold' }}>0.3s</div>
            <div className="stat-label" style={{ fontSize: '12px', opacity: 0.7 }}>Thời gian phản hồi</div>
          </div>
          <div className="stat-card glass-card" style={{ flex: 1, padding: '20px', borderRadius: '16px', background: 'rgba(255,255,255,0.05)' }}>
            <div className="stat-value" style={{ color: '#b388ff', fontSize: '24px', fontWeight: 'bold' }}>112K+</div>
            <div className="stat-label" style={{ fontSize: '12px', opacity: 0.7 }}>Ảnh X-quang huấn luyện</div>
          </div>
        </div>
      </div>

      <div className="glass-card purple-glow">
        <div className="card-label">🏗️ KIẾN TRÚC KỸ THUẬT</div>
        <div className="tech-grid">
          <div>
            <div className="tech-item-label">BACKBONE MODEL</div>
            <div className="tech-item-value">DenseNet-121</div>
            <div className="tech-item-sub">TorchXRayVision 1.4.0</div>
          </div>
          <div>
            <div className="tech-item-label">XAI METHOD</div>
            <div className="tech-item-value">Grad-CAM</div>
            <div className="tech-item-sub">Feature Map + Gradient Hook</div>
          </div>
          <div>
            <div className="tech-item-label">BACKEND / FRONTEND</div>
            <div className="tech-item-value">FastAPI + React Vite</div>
            <div className="tech-item-sub">REST API | Node.js</div>
          </div>
        </div>
      </div>

      <div className="glass-card">
        <div className="card-label">📖 HƯỚNG DẪN SỬ DỤNG</div>
        <div className="step">
          <div className="step-num">1</div>
          <div className="step-text">Chuyển sang tab <strong>Chẩn đoán AI</strong> ở thanh điều hướng bên trái.</div>
        </div>
        <div className="step">
          <div className="step-num">2</div>
          <div className="step-text">Kéo thả hoặc bấm để <strong>tải ảnh X-quang lồng ngực</strong> (JPG, PNG).</div>
        </div>
        <div className="step">
          <div className="step-num">3</div>
          <div className="step-text">AI sẽ phân tích và trả về <strong>Kết quả định lượng + Bản đồ nhiệt Grad-CAM</strong> giải thích trực quan vị trí bệnh lý.</div>
        </div>
      </div>
    </div>
  );
}
