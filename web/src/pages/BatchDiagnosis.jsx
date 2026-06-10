import { useState, useRef } from 'react';
import { toast } from 'react-hot-toast';
import jsPDF from 'jspdf';

export default function BatchDiagnosis() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [expandedRow, setExpandedRow] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
      setResults([]);
      setExpandedRow(null);
    }
  };

  const handleProcessBatch = async () => {
    if (files.length === 0) return;
    setIsProcessing(true);
    setResults([]);
    setExpandedRow(null);
    setProgress(10);

    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      setProgress(30);
      const response = await fetch('http://localhost:8000/predict_batch', {
        method: 'POST',
        body: formData,
      });

      setProgress(80);
      const data = await response.json();

      if (response.ok && data.success) {
        setResults(data.results);
        toast.success(`Đã xử lý xong ${data.results.length} ảnh!`);
      } else {
        toast.error("Có lỗi xảy ra: " + (data.detail || "Không rõ nguyên nhân"));
      }
    } catch (err) {
      console.error(err);
      toast.error('Không thể kết nối đến máy chủ.');
    } finally {
      setProgress(100);
      setIsProcessing(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const generatePDF = (result) => {
    const doc = new jsPDF();
    doc.setFontSize(22);
    doc.setTextColor(0, 150, 200);
    doc.text("MedAI Vision - XAI Medical Report", 20, 20);

    doc.setFontSize(11);
    doc.setTextColor(120, 120, 120);
    doc.text(`Ngay xuat: ${new Date().toLocaleString('vi-VN')}`, 20, 30);

    doc.setFontSize(14);
    doc.setTextColor(0, 0, 0);
    doc.text(`Ten benh nhan: ${result.patient_name}`, 20, 45);
    doc.text(`File goc: ${result.filename}`, 20, 55);
    doc.text(`Ket qua: ${result.prediction}`, 20, 70);
    doc.text(`Do tin cay: ${result.probability}%`, 20, 80);

    if (result.heatmap_base64) {
      const imgData = `data:image/jpeg;base64,${result.heatmap_base64}`;
      doc.addImage(imgData, 'JPEG', 20, 90, 80, 80);
    }

    doc.setFontSize(12);
    const splitExplanation = doc.splitTextToSize(`Giai thich y khoa: ${result.explanation || ''}`, 170);
    doc.text(splitExplanation, 20, 180);

    doc.save(`HoSo_${result.patient_name.replace(/ /g, '_')}.pdf`);
    toast.success(`Đã in hồ sơ: ${result.patient_name}`);
  };

  const generateAllPDFs = () => {
    const validResults = results.filter(r => r.success && !r.is_ood);
    validResults.forEach(r => generatePDF(r));
    toast.success(`Đang xuất ${validResults.length} hồ sơ PDF!`);
  };

  // Thống kê
  const totalProcessed = results.length;
  const totalEffusion = results.filter(r => r.success && r.is_effusion).length;
  const totalNormal = results.filter(r => r.success && !r.is_effusion && !r.is_ood).length;
  const totalOOD = results.filter(r => r.is_ood || !r.success).length;

  const getRowBorderColor = (r) => {
    if (r.is_ood || !r.success) return '#ffab00';
    if (r.is_effusion) return '#ff6b6b';
    return '#00cec9';
  };

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      <div className="page-header">
        <h1 className="page-title">📋 Chẩn đoán Hàng loạt (Batch Processing)</h1>
        <p className="page-subtitle">Xử lý tự động đa luồng (Multi-threading). Tự động trích xuất thông tin bệnh nhân từ tên tệp.</p>
      </div>

      <div className="glass-card" style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
        <input type="file" multiple accept="image/*,.zip" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} />
        <button className="btn-secondary" onClick={() => fileInputRef.current.click()}>📁 Chọn Ảnh hoặc File ZIP</button>
        <span style={{ color: 'var(--text-muted)', flex: 1 }}>
          {files.length > 0 ? `Đã chọn ${files.length} tệp (ảnh hoặc zip) sẵn sàng xử lý.` : 'Chưa chọn tệp nào.'}
        </span>
        <button className="btn-primary" onClick={handleProcessBatch} disabled={files.length === 0 || isProcessing}>
          {isProcessing ? `⏳ Đang xử lý đa luồng...` : '▶ Bắt đầu Xử lý AI'}
        </button>
      </div>

      {isProcessing && (
        <div style={{ margin: '20px 0', height: '6px', background: 'rgba(0,212,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ width: `${progress}%`, height: '100%', background: 'linear-gradient(90deg, var(--cyan), #a29bfe)', transition: 'width 0.5s ease', boxShadow: '0 0 12px var(--cyan)' }}></div>
        </div>
      )}

      {results.length > 0 && (
        <>
          <div className="metrics-row" style={{ marginTop: '20px' }}>
            <div className="metric-card">
              <div className="metric-label">TỔNG SỐ ẢNH</div>
              <div className="metric-value">{totalProcessed}</div>
            </div>
            <div className="metric-card" style={{ borderColor: 'rgba(255,107,107,0.3)' }}>
              <div className="metric-label" style={{ color: 'var(--red)' }}>BỆNH TRÀN DỊCH</div>
              <div className="metric-value" style={{ color: 'var(--red)' }}>{totalEffusion}</div>
            </div>
            <div className="metric-card" style={{ borderColor: 'rgba(0,206,201,0.3)' }}>
              <div className="metric-label" style={{ color: '#00cec9' }}>BÌNH THƯỜNG</div>
              <div className="metric-value" style={{ color: '#00cec9' }}>{totalNormal}</div>
            </div>
            <div className="metric-card" style={{ borderColor: 'rgba(255,171,0,0.3)' }}>
              <div className="metric-label" style={{ color: '#ffab00' }}>ẢNH RÁC (OOD)</div>
              <div className="metric-value" style={{ color: '#ffab00' }}>{totalOOD}</div>
            </div>
          </div>

          <div className="glass-card" style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ color: 'var(--text-primary)' }}>Danh sách Kết quả Chi tiết</h3>
              <button className="btn-primary" onClick={generateAllPDFs} style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                🖨 In Toàn bộ Hồ sơ Hợp lệ
              </button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--cyan-border)', color: 'var(--cyan)', textAlign: 'left' }}>
                  <th style={{ padding: '12px', width: '4px' }}></th>
                  <th style={{ padding: '12px' }}>Tên Bệnh Nhân</th>
                  <th style={{ padding: '12px' }}>Tên File</th>
                  <th style={{ padding: '12px' }}>Trạng thái / Chẩn đoán</th>
                  <th style={{ padding: '12px' }}>Độ tin cậy</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, idx) => (
                  <>
                    <tr
                      key={`row-${idx}`}
                      onClick={() => r.success && !r.is_ood && setExpandedRow(expandedRow === idx ? null : idx)}
                      style={{
                        borderBottom: expandedRow === idx ? 'none' : '1px solid rgba(255,255,255,0.05)',
                        cursor: r.success && !r.is_ood ? 'pointer' : 'default',
                        transition: 'background 0.2s ease',
                        background: expandedRow === idx ? 'rgba(0,212,255,0.04)' : 'transparent'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0,212,255,0.04)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = expandedRow === idx ? 'rgba(0,212,255,0.04)' : 'transparent'}
                    >
                      <td style={{ padding: '0', width: '4px' }}>
                        <div style={{ width: '4px', height: '100%', minHeight: '44px', background: getRowBorderColor(r), borderRadius: '2px' }}></div>
                      </td>
                      <td style={{ padding: '12px', fontWeight: 'bold', color: 'var(--text-primary)' }}>{r.patient_name}</td>
                      <td style={{ padding: '12px', color: 'var(--text-muted)', fontSize: '0.82rem' }}>{r.filename}</td>
                      <td style={{ padding: '12px' }}>
                        {r.is_ood ? (
                          <span style={{ color: '#ffab00', fontWeight: 'bold' }}>⚠️ Không phải X-quang</span>
                        ) : !r.success ? (
                          <span style={{ color: '#ffab00', fontWeight: 'bold' }}>⚠️ Lỗi xử lý</span>
                        ) : (
                          <span style={{ color: r.is_effusion ? 'var(--red)' : '#00cec9', fontWeight: 'bold' }}>
                            {r.prediction}
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '12px' }}>{r.success && !r.is_ood ? `${r.probability}%` : '—'}</td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        {r.success && !r.is_ood && (
                          <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={(e) => { e.stopPropagation(); generatePDF(r); }}>
                            📄 PDF
                          </button>
                        )}
                      </td>
                    </tr>

                    {/* Expandable detail row */}
                    {expandedRow === idx && r.success && !r.is_ood && (
                      <tr key={`detail-${idx}`}>
                        <td colSpan="6" style={{ padding: '0 12px 16px 20px', background: 'rgba(0,212,255,0.02)', borderBottom: '1px solid rgba(0,212,255,0.15)' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '20px', paddingTop: '12px' }}>
                            {r.heatmap_base64 && (
                              <div>
                                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', letterSpacing: '1px' }}>BẢN ĐỒ NHIỆT (GRAD-CAM)</div>
                                <img
                                  src={`data:image/jpeg;base64,${r.heatmap_base64}`}
                                  alt="Heatmap"
                                  style={{ width: '100%', borderRadius: '8px', border: '1px solid rgba(0,212,255,0.2)' }}
                                />
                              </div>
                            )}
                            <div>
                              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', letterSpacing: '1px' }}>📝 GIẢI THÍCH Y KHOA (XAI TEXT)</div>
                              <p style={{ fontSize: '0.92rem', lineHeight: '1.7', color: 'var(--text-primary)', opacity: 0.9 }}>
                                {r.explanation || 'Không có dữ liệu giải thích.'}
                              </p>
                              <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
                                <span style={{ fontSize: '0.8rem', padding: '4px 12px', borderRadius: '8px', background: 'rgba(0,212,255,0.08)', color: 'var(--cyan)', fontWeight: 600 }}>
                                  Raw Score: {r.raw_probability?.toFixed(4) || '—'}
                                </span>
                                <span style={{ fontSize: '0.8rem', padding: '4px 12px', borderRadius: '8px', background: 'rgba(162,155,254,0.1)', color: '#a29bfe', fontWeight: 600 }}>
                                  Display: {r.probability}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
