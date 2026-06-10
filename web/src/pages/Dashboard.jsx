import { API_BASE_URL } from '../utils/apiConfig';
import { useState, useEffect, useRef } from 'react';
import LungModel from '../components/LungModel';

// Animated counter hook
function useAnimatedNumber(target, duration = 1200) {
  const [value, setValue] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    if (target === 0) { setValue(0); return; }
    let start = 0;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(start + (target - start) * eased));
      if (progress < 1) ref.current = requestAnimationFrame(animate);
    };

    ref.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(ref.current);
  }, [target, duration]);

  return value;
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, healthRes] = await Promise.all([
          fetch('${API_BASE_URL}/stats'),
          fetch('${API_BASE_URL}/health')
        ]);
        if (statsRes.ok) setStats(await statsRes.json());
        if (healthRes.ok) setHealth(await healthRes.json());
      } catch (e) {
        console.error("Dashboard fetch error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 15000); // Refresh 15s
    return () => clearInterval(interval);
  }, []);

  const totalRecords = useAnimatedNumber(stats?.total_records || 0);
  const totalEffusion = useAnimatedNumber(stats?.total_effusion || 0);
  const totalNormal = useAnimatedNumber(stats?.total_normal || 0);
  const avgConf = useAnimatedNumber(stats?.avg_confidence || 0);

  const formatUptime = (seconds) => {
    if (!seconds) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  };

  return (
    <div className="page" style={{ animation: 'fadeIn 0.5s ease' }}>
      <div className="page-header">
        <h1 className="page-title">🫁 MedAI Vision</h1>
        <p className="page-subtitle">Hệ thống Chẩn đoán X-quang Phổi tích hợp Trí tuệ Nhân tạo Giải thích được (XAI)</p>
      </div>

      <div style={{ display: 'flex', gap: '32px', marginBottom: '32px' }}>
        <div style={{ flex: '0 0 240px', background: 'rgba(0,212,255,0.02)', borderRadius: '20px', border: '1px solid rgba(0,212,255,0.1)' }}>
          <LungModel size={120} />
        </div>
        <div style={{ display: 'flex', gap: '16px', flex: 1 }}>
          {loading ? (
            [1,2,3,4].map(i => (
              <div key={i} className="metric-card" style={{ flex: 1, minHeight: '90px' }}>
                <div className="skeleton" style={{ height: '14px', width: '60%', marginBottom: '12px', borderRadius: '4px', background: 'rgba(0,212,255,0.08)', animation: 'skeleton-pulse 1.5s ease infinite' }}></div>
                <div className="skeleton" style={{ height: '28px', width: '40%', borderRadius: '4px', background: 'rgba(0,212,255,0.12)', animation: 'skeleton-pulse 1.5s ease infinite' }}></div>
              </div>
            ))
          ) : (
            <>
              <div className="metric-card" style={{ flex: 1 }}>
                <div className="metric-label">TỔNG CA PHÂN TÍCH</div>
                <div className="metric-value">{totalRecords}</div>
                <div className="metric-delta">Thời gian thực từ DB</div>
              </div>
              <div className="metric-card" style={{ flex: 1, borderColor: 'rgba(255,107,107,0.25)' }}>
                <div className="metric-label" style={{ color: 'var(--red)' }}>CA TRÀN DỊCH</div>
                <div className="metric-value" style={{ color: 'var(--red)' }}>{totalEffusion}</div>
                <div className="metric-delta" style={{ color: 'var(--red)', opacity: 0.7 }}>Effusion Detected</div>
              </div>
              <div className="metric-card" style={{ flex: 1, borderColor: 'rgba(0,206,201,0.25)' }}>
                <div className="metric-label" style={{ color: '#00cec9' }}>CA BÌNH THƯỜNG</div>
                <div className="metric-value" style={{ color: '#00cec9' }}>{totalNormal}</div>
                <div className="metric-delta" style={{ color: '#00cec9', opacity: 0.7 }}>Normal Chest</div>
              </div>
              <div className="metric-card" style={{ flex: 1, borderColor: 'rgba(162,155,254,0.25)' }}>
                <div className="metric-label" style={{ color: '#a29bfe' }}>ĐỘ TIN CẬY TB</div>
                <div className="metric-value" style={{ color: '#a29bfe' }}>{avgConf}%</div>
                <div className="metric-delta" style={{ color: '#a29bfe', opacity: 0.7 }}>Avg Confidence</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Health Status */}
      {health && (
        <div className="glass-card" style={{ marginBottom: '20px', padding: '20px' }}>
          <div className="card-label">⚡ TRẠNG THÁI HỆ THỐNG (REAL-TIME)</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginTop: '12px' }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>TRẠNG THÁI</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: health.model_loaded ? '#00cec9' : '#ff6b6b', boxShadow: health.model_loaded ? '0 0 8px #00cec9' : '0 0 8px #ff6b6b' }}></div>
                <span style={{ fontSize: '0.9rem', fontWeight: 600, color: health.model_loaded ? '#00cec9' : '#ff6b6b' }}>
                  {health.model_loaded ? "Online" : "Offline"}
                </span>
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>THIẾT BỊ</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{health.device?.toUpperCase()}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>RAM SỬ DỤNG</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: health.ram_percent > 80 ? '#ff6b6b' : 'var(--text-primary)' }}>
                {health.ram_used_gb}GB / {health.ram_total_gb}GB ({health.ram_percent}%)
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>UPTIME</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{formatUptime(health.uptime_seconds)}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>BẢN GHI DB</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--cyan)' }}>{health.db_records} records</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {stats?.recent_records && stats.recent_records.length > 0 && (
        <div className="glass-card" style={{ marginBottom: '20px' }}>
          <div className="card-label">🕓 HOẠT ĐỘNG GẦN ĐÂY</div>
          <div style={{ marginTop: '12px' }}>
            {stats.recent_records.map((r, i) => (
              <div key={r.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '10px 0', borderBottom: i < stats.recent_records.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '4px', height: '32px', borderRadius: '2px',
                    background: r.prediction_label?.includes('Tràn') || r.prediction_label?.includes('Effusion') ? '#ff6b6b' : '#00cec9'
                  }}></div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{r.patient_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.timestamp}</div>
                  </div>
                </div>
                <div style={{
                  padding: '4px 12px', borderRadius: '12px', fontSize: '0.78rem', fontWeight: 700,
                  background: r.prediction_label?.includes('Tràn') || r.prediction_label?.includes('Effusion')
                    ? 'rgba(255,107,107,0.12)' : 'rgba(0,206,201,0.12)',
                  color: r.prediction_label?.includes('Tràn') || r.prediction_label?.includes('Effusion')
                    ? '#ff6b6b' : '#00cec9'
                }}>
                  {r.prediction_label} — {r.confidence_score}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
