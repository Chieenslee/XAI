import { useState, useRef } from 'react';
import ConfidenceGauge from '../components/ConfidenceGauge';

export default function Diagnosis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
      setResult(null);
      setError('');
    }
  };

  const analyzeImage = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError('');
    setResult(null);

    // Fake delay for scanning animation
    await new Promise(r => setTimeout(r, 2500));

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body: formData
      });
      
      if (!res.ok) throw new Error('Backend responded with an error');
      
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Lỗi kết nối Server FastAPI.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">🔬 Chẩn đoán Hình ảnh AI</h1>
        <p className="page-subtitle">Tải lên ảnh X-quang để nhận phân tích tức thì từ mô hình DenseNet-121</p>
      </div>

      <div 
        className="upload-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          onClick={(e) => (e.target.value = null)} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />
        <div className="upload-icon">📂</div>
        <div className="upload-title">Kéo thả ảnh X-quang vào đây hoặc nhấn để chọn file</div>
        <div className="upload-sub">Hỗ trợ định dạng JPG, JPEG, PNG</div>
      </div>

      {preview && (
        <div className="diag-grid" style={{ marginTop: '32px' }}>
          <div>
            <div className="card-label">📷 ẢNH X-QUANG GỐC</div>
            <div className="img-preview">
              <img src={preview} alt="X-ray preview" />
            </div>
            <div className="img-meta">
              <div className="img-meta-chip">
                <div className="img-meta-chip-label">TÊN FILE</div>
                <div className="img-meta-chip-value" style={{ fontSize: '0.8rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{file.name}</div>
              </div>
              <div className="img-meta-chip">
                <div className="img-meta-chip-label">DUNG LƯỢNG</div>
                <div className="img-meta-chip-value">{(file.size / 1024).toFixed(1)} KB</div>
              </div>
            </div>
          </div>

          <div>
            <div className="card-label">🤖 KẾT QUẢ PHÂN TÍCH AI</div>
            
            {!isAnalyzing && !result && !error && (
              <button className="analyze-btn" onClick={analyzeImage}>
                🚀 Phân tích ảnh với AI
              </button>
            )}

            {isAnalyzing && (
              <div>
                <div className="scan-container">
                  <img src={preview} alt="Scanning" />
                  <div className="laser-beam"></div>
                  <div className="scan-grid-overlay"></div>
                </div>
                <div className="scan-status">
                  <div className="scan-status-dot"></div>
                  <div style={{ color: '#00d4ff', fontWeight: 600, fontSize: '0.9rem' }}>
                    DenseNet-121 đang phân tích cấu trúc phổi...
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="glass-card red-glow" style={{ color: '#ff6b6b' }}>
                <strong>❌ Lỗi:</strong> {error}
                <button className="analyze-btn" onClick={analyzeImage} style={{ marginTop: '16px' }}>
                  Thử lại
                </button>
              </div>
            )}

            {result && (
              <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
                <ConfidenceGauge 
                  probability={result.probability} 
                  isEffusion={result.prediction === "Tràn dịch màng phổi"} 
                />
                
                <div style={{ marginTop: '24px' }}>
                  <div className="card-label">🧬 BẢN ĐỒ NHIỆT XAI (GRAD-CAM)</div>
                  <div className="img-preview">
                    <img src={`data:image/jpeg;base64,${result.heatmap_base64}`} alt="Heatmap" />
                  </div>
                  <div className="heatmap-legend">
                    Vùng <span className="red">Đỏ-Cam</span> = AI tập trung cao nhất • Vùng <span className="blue">Xanh</span> = Ít liên quan
                  </div>
                </div>

                <button className="analyze-btn" style={{ marginTop: '24px', background: 'rgba(255,255,255,0.05)', boxShadow: 'none' }} onClick={() => { setFile(null); setPreview(''); setResult(null); }}>
                  🔄 Phân tích ảnh khác
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
