import { useState, useEffect } from 'react';

export default function CompareView() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Lưu trữ 2 record đang được chọn để so sánh
  const [record1Id, setRecord1Id] = useState('');
  const [record2Id, setRecord2Id] = useState('');
  
  const [record1, setRecord1] = useState(null);
  const [record2, setRecord2] = useState(null);

  // Fetch lịch sử bệnh án
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('http://localhost:8000/history');
        const data = await res.json();
        if (data.success) {
          setHistory(data.data);
        }
      } catch (err) {
        console.error("Lỗi khi tải lịch sử:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  // Fetch chi tiết record 1 khi thay đổi
  useEffect(() => {
    if (!record1Id) {
      setRecord1(null);
      return;
    }
    const fetchRecord = async () => {
      try {
        const res = await fetch(`http://localhost:8000/record/${record1Id}`);
        const data = await res.json();
        if (data.success) setRecord1(data.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchRecord();
  }, [record1Id]);

  // Fetch chi tiết record 2 khi thay đổi
  useEffect(() => {
    if (!record2Id) {
      setRecord2(null);
      return;
    }
    const fetchRecord = async () => {
      try {
        const res = await fetch(`http://localhost:8000/record/${record2Id}`);
        const data = await res.json();
        if (data.success) setRecord2(data.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchRecord();
  }, [record2Id]);

  const renderRecordCard = (record, recordNum) => {
    if (!record) {
      return (
        <div className="glass-card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', opacity: 0.5 }}>
          Vui lòng chọn ca bệnh {recordNum} từ danh sách bên trên
        </div>
      );
    }

    const isEffusion = record.prediction_label?.includes('Tràn') || record.prediction_label?.includes('Effusion');

    return (
      <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ paddingBottom: '16px', borderBottom: '1px solid rgba(0,212,255,0.2)' }}>
          <h3 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>{record.patient_name}</h3>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Mã HS: #{record.id} | Ngày: {record.timestamp}</div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{
            padding: '6px 12px', borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem',
            background: isEffusion ? 'rgba(255,107,107,0.1)' : 'rgba(0,206,201,0.1)',
            color: isEffusion ? '#ff6b6b' : '#00cec9',
            border: `1px solid ${isEffusion ? 'rgba(255,107,107,0.3)' : 'rgba(0,206,201,0.3)'}`
          }}>
            {record.prediction_label}
          </div>
          <div style={{ fontWeight: 'bold', color: 'var(--text-primary)' }}>
            Độ tin cậy: {record.confidence_score}%
          </div>
        </div>

        <div>
          <div className="card-label" style={{ marginBottom: '8px' }}>Ghi chú lâm sàng</div>
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            {record.clinical_notes || 'Không có ghi chú'}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '8px' }}>
          <div>
            <div className="card-label" style={{ marginBottom: '8px', fontSize: '0.7rem' }}>ẢNH GỐC</div>
            {/* Vì ảnh gốc không lưu trong DB (chỉ lưu filename), ở bản demo này ta có thể chỉ hiển thị heatmap */}
            <div style={{ background: 'rgba(0,0,0,0.2)', height: '200px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              [Ảnh gốc: {record.image_path}]
            </div>
          </div>
          <div>
            <div className="card-label" style={{ marginBottom: '8px', fontSize: '0.7rem' }}>BẢN ĐỒ NHIỆT (GRAD-CAM)</div>
            {record.heatmap_path && record.heatmap_path !== "N/A" && record.heatmap_path !== "base64_data" && !record.heatmap_path.includes("HIDDEN") ? (
              <img src={`data:image/jpeg;base64,${record.heatmap_path}`} alt="Heatmap" style={{ width: '100%', height: '200px', objectFit: 'contain', borderRadius: '8px', background: '#000' }} />
            ) : (
              <div style={{ background: 'rgba(0,0,0,0.2)', height: '200px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '10px' }}>
                Dữ liệu Heatmap quá lớn đã bị lược bỏ trong DB hoặc bị ẩn.
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="page" style={{ animation: 'fadeIn 0.5s ease' }}>
      <div className="page-header">
        <h1 className="page-title">⚖️ So sánh Ca bệnh</h1>
        <p className="page-subtitle">Theo dõi tiến triển của bệnh nhân qua các thời điểm chụp X-quang khác nhau hoặc đối chiếu 2 ca bệnh độc lập.</p>
      </div>

      <div className="glass-card" style={{ marginBottom: '24px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '250px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--cyan)' }}>CHỌN CA BỆNH SỐ 1</label>
          <select 
            className="text-input" 
            value={record1Id} 
            onChange={(e) => setRecord1Id(e.target.value)}
            style={{ width: '100%', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--cyan-border)', color: '#fff', padding: '10px', borderRadius: '8px' }}
          >
            <option value="">-- Chọn bệnh nhân --</option>
            {history.map(h => (
              <option key={h.id} value={h.id}>#{h.id} - {h.patient_name} ({h.timestamp})</option>
            ))}
          </select>
        </div>
        
        <div style={{ flex: 1, minWidth: '250px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600, color: '#a29bfe' }}>CHỌN CA BỆNH SỐ 2</label>
          <select 
            className="text-input" 
            value={record2Id} 
            onChange={(e) => setRecord2Id(e.target.value)}
            style={{ width: '100%', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(162,155,254,0.3)', color: '#fff', padding: '10px', borderRadius: '8px' }}
          >
            <option value="">-- Chọn bệnh nhân --</option>
            {history.map(h => (
              <option key={h.id} value={h.id}>#{h.id} - {h.patient_name} ({h.timestamp})</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--cyan)' }}>Đang tải danh sách lịch sử...</div>
      ) : (
        <div style={{ display: 'flex', gap: '24px', flexDirection: 'row', alignItems: 'stretch' }}>
          {/* Ca bệnh 1 */}
          {renderRecordCard(record1, 1)}
          
          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ width: '1px', height: '100%', background: 'rgba(255,255,255,0.1)', position: 'relative' }}>
              <div style={{ 
                position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                background: '#1a1a2e', padding: '8px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.1)',
                fontSize: '0.8rem', color: 'var(--text-muted)'
              }}>VS</div>
            </div>
          </div>

          {/* Ca bệnh 2 */}
          {renderRecordCard(record2, 2)}
        </div>
      )}
    </div>
  );
}
