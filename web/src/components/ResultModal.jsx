import { useRef } from 'react';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';

export default function ResultModal({ result, preview, onClose, onNext }) {
  const isEffusion = result.prediction === "Tràn dịch màng phổi";
  const confidence = isEffusion ? result.probability : 100 - result.probability;
  const printRef = useRef();

  const explanation = result.explanation || (isEffusion
    ? `Phân tích XAI Grad-CAM++ phát hiện dải mờ cản quang bất thường tập trung tại vùng góc sườn hoành. Độ tin cậy: ${confidence.toFixed(1)}%. Khuyến nghị siêu âm màng phổi để xác nhận.`
    : `Không phát hiện vùng mờ bất thường tại lồng ngực. Các góc sườn hoành hai bên sắc nét. Độ tin cậy: ${confidence.toFixed(1)}%.`);

  // ── Load ảnh thành base64 để nhúng vào jsPDF ──────────────
  // Blob URL (same-origin): KHÔNG set crossOrigin, tránh taint canvas
  // Data URL (heatmap base64): không cần crossOrigin
  const loadImgAsDataUrl = (src) =>
    new Promise((resolve) => {
      const img = new Image();
      // Chỉ set crossOrigin cho URL bên ngoài (http/https), không phải blob:/data:
      if (src && src.startsWith('http')) img.crossOrigin = 'Anonymous';
      img.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = img.naturalWidth || 224;
          canvas.height = img.naturalHeight || 224;
          canvas.getContext('2d').drawImage(img, 0, 0);
          resolve({ url: canvas.toDataURL('image/jpeg', 0.92), w: canvas.width, h: canvas.height });
        } catch (e) {
          resolve(null);
        }
      };
      img.onerror = () => resolve(null);
      img.src = src;
    });

  // ── Xuất PDF sạch — layout y tế A4 ───────────────────────
  const handleExportPDF = async () => {
    const toastId = toast.loading('Đang tạo báo cáo PDF...');
    try {
      const pdf   = new jsPDF('p', 'mm', 'a4');
      const W     = pdf.internal.pageSize.getWidth();
      const H     = pdf.internal.pageSize.getHeight();
      const mg    = 14;
      let   y     = mg;

      // helpers
      const txt = (text, x, yy, { size = 10, style = 'normal', color = [30, 30, 30] } = {}) => {
        pdf.setFontSize(size);
        pdf.setFont('helvetica', style);
        pdf.setTextColor(...color);
        pdf.text(text, x, yy);
      };

      const fitImg = (imgObj, bx, by, bw, bh) => {
        if (!imgObj || !imgObj.url) return;
        const iw = imgObj.w || bw;
        const ih = imgObj.h || bh;
        const ratio = Math.min(bw / iw, bh / ih);
        const rw = iw * ratio, rh = ih * ratio;
        pdf.addImage(imgObj.url, 'JPEG', bx + (bw - rw) / 2, by + (bh - rh) / 2, rw, rh);
      };

      // ── Header bar ────────────────────────────────────────
      pdf.setFillColor(8, 16, 32);
      pdf.rect(0, 0, W, 20, 'F');
      txt('XAI Medical — Báo cáo Chẩn đoán Hình ảnh', mg, 13, { size: 13, style: 'bold', color: [0, 212, 255] });
      txt(`${new Date().toLocaleString('vi-VN')}`, W - mg, 8,  { size: 7.5, color: [140, 180, 210] });
      txt('DenseNet-121 + Grad-CAM++ | v8', W - mg, 14, { size: 7.5, color: [140, 180, 210] });
      // fix align right
      pdf.setFontSize(7.5); pdf.setFont('helvetica', 'normal'); pdf.setTextColor(140, 180, 210);
      pdf.text(`${new Date().toLocaleString('vi-VN')}`, W - mg, 8, { align: 'right' });
      pdf.text('DenseNet-121 + Grad-CAM++ | v8', W - mg, 14, { align: 'right' });
      y = 28;

      // ── Kết quả ───────────────────────────────────────────
      const diagCol = isEffusion ? [200, 50, 50] : [0, 160, 100];
      pdf.setFillColor(...diagCol);
      pdf.roundedRect(mg, y, W - mg * 2, 13, 3, 3, 'F');
      const diagLabel = isEffusion
        ? `TRÀN DỊCH MÀNG PHỔI   —   Độ tin cậy: ${confidence.toFixed(1)}%`
        : `BÌNH THƯỜNG   —   Độ tin cậy: ${confidence.toFixed(1)}%`;
      txt(diagLabel, mg + 4, y + 8.5, { size: 11, style: 'bold', color: [255, 255, 255] });
      y += 18;

      // ── Hình ảnh ──────────────────────────────────────────
      const imgW  = (W - mg * 2 - 6) / 2;
      const imgH  = 72;

      const origImg  = await loadImgAsDataUrl(preview);
      // heatmap: data URL → dùng trực tiếp, không cần decode qua canvas
      const heatDataUrl = `data:image/jpeg;base64,${result.heatmap_base64}`;
      const heatImg = await loadImgAsDataUrl(heatDataUrl).then(r => r || { url: heatDataUrl, w: 224, h: 224 });

      // khung ảnh gốc
      pdf.setDrawColor(60, 90, 130); pdf.setLineWidth(0.3);
      pdf.rect(mg, y, imgW, imgH + 7);
      txt('ẢNH X-QUANG GỐC', mg + 2, y + 5, { size: 7, style: 'bold', color: [100, 160, 220] });
      fitImg(origImg, mg, y + 6, imgW, imgH);

      // khung heatmap
      const x2 = mg + imgW + 6;
      pdf.rect(x2, y, imgW, imgH + 7);
      txt('BẢN ĐỒ NHIỆT (GRAD-CAM++)', x2 + 2, y + 5, { size: 7, style: 'bold', color: [100, 160, 220] });
      fitImg(heatImg, x2, y + 6, imgW, imgH);
      y += imgH + 12;

      // ── Phân tích XAI ─────────────────────────────────────
      pdf.setFillColor(238, 244, 255);
      pdf.roundedRect(mg, y, W - mg * 2, 7, 2, 2, 'F');
      txt('PHÂN TÍCH XAI (GRAD-CAM++)', mg + 3, y + 5, { size: 8.5, style: 'bold', color: [30, 80, 160] });
      y += 9;
      const lines = pdf.splitTextToSize(explanation, W - mg * 2 - 4);
      pdf.setFontSize(9); pdf.setFont('helvetica', 'normal'); pdf.setTextColor(40, 40, 40);
      pdf.text(lines, mg + 2, y);
      y += lines.length * 5 + 7;

      // ── Thông số kỹ thuật ─────────────────────────────────
      pdf.setFillColor(238, 244, 255);
      pdf.roundedRect(mg, y, W - mg * 2, 7, 2, 2, 'F');
      txt('THÔNG SỐ KỸ THUẬT', mg + 3, y + 5, { size: 8.5, style: 'bold', color: [30, 80, 160] });
      y += 10;
      const specs = [
        ['Mô hình',        'DenseNet-121 (TorchXRayVision) — Fine-tuned'],
        ['Phương pháp XAI','Grad-CAM++ (2nd-Order Gradient + Alpha Weighting)'],
        ['Ngưỡng',         '0.0682 (Optimal Threshold từ ROC Curve)'],
        ['Raw Score',      result.raw_probability?.toFixed(6) ?? '—'],
        ['Xác suất',       `${result.probability?.toFixed(2)}%`],
      ];
      specs.forEach(([k, v], i) => {
        pdf.setFontSize(8.5); pdf.setFont('helvetica', 'bold'); pdf.setTextColor(50, 80, 130);
        pdf.text(`${k}:`, mg + 2, y + i * 5.8);
        pdf.setFont('helvetica', 'normal'); pdf.setTextColor(40, 40, 40);
        pdf.text(v, mg + 46, y + i * 5.8);
      });
      y += specs.length * 5.8 + 7;

      // ── Cảnh báo ──────────────────────────────────────────
      pdf.setFillColor(255, 248, 225);
      pdf.setDrawColor(210, 150, 0); pdf.setLineWidth(0.4);
      pdf.roundedRect(mg, y, W - mg * 2, 14, 2, 2, 'FD');
      txt('⚠ CẢNH BÁO', mg + 3, y + 5.5, { size: 8, style: 'bold', color: [160, 90, 0] });
      txt('Kết quả AI chỉ mang tính hỗ trợ, không thay thế chẩn đoán của bác sĩ chuyên khoa.', mg + 3, y + 10.5, { size: 8, color: [130, 80, 0] });
      y += 18;

      // ── Footer ────────────────────────────────────────────
      pdf.setDrawColor(180, 200, 220); pdf.setLineWidth(0.3);
      pdf.line(mg, H - 11, W - mg, H - 11);
      txt('XAI Medical Imaging System | Antigravity AI', mg, H - 6, { size: 7, color: [140, 160, 180] });
      pdf.setFontSize(7); pdf.setFont('helvetica', 'normal'); pdf.setTextColor(140, 160, 180);
      pdf.text('Trang 1 / 1', W - mg, H - 6, { align: 'right' });

      pdf.save(`XAI_Report_${Date.now()}.pdf`);
      toast.success('Xuất báo cáo thành công!', { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Lỗi PDF: ' + err.message, { id: toastId });
    }
  };

  if (!result) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">

        <button className="modal-close-btn" onClick={onClose} title="Đóng & Lưu nháp">✕</button>

        {/* ── Layout modal GIỮ NGUYÊN như bản gốc ── */}
        <div ref={printRef} className="modal-print-area">
          <div className="modal-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div className="modal-logo">🩺 XAI Medical</div>
              <div>
                <h2 className="modal-title">BÁO CÁO CHẨN ĐOÁN HÌNH ẢNH</h2>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  📅 {new Date().toLocaleString('vi-VN')}
                </div>
              </div>
            </div>
            <div className={`modal-badge ${isEffusion ? 'effusion' : 'normal'}`}>
              {result.prediction.toUpperCase()} ({confidence.toFixed(1)}%)
            </div>
          </div>

          <div className="modal-body">
            <div className="modal-images">
              <div className="modal-img-wrapper">
                <div className="card-label" style={{ marginBottom: '8px' }}>ẢNH X-QUANG GỐC</div>
                <img src={preview} alt="Original X-Ray" className="modal-img" />
              </div>
              {result.mask_base64 && (
                <div className="modal-img-wrapper">
                  <div className="card-label" style={{ marginBottom: '8px' }}>MASK PHÂN ĐOẠN (U-NET)</div>
                  <img src={`data:image/jpeg;base64,${result.mask_base64}`} alt="Mask" className="modal-img" />
                </div>
              )}
              <div className="modal-img-wrapper">
                <div className="card-label" style={{ marginBottom: '8px' }}>BẢN ĐỒ NHIỆT (GRAD-CAM++)</div>
                <img src={`data:image/jpeg;base64,${result.heatmap_base64}`} alt="Heatmap" className="modal-img" />
              </div>
            </div>
          </div>

          <div className="modal-explanation">
            <h3 className="explanation-title">📝 CHI TIẾT CHẨN ĐOÁN</h3>
            <p className="explanation-text">{explanation}</p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onNext}>🔄 Chẩn đoán tiếp theo</button>
          <button className="btn-primary" onClick={handleExportPDF}>📥 Xuất Báo cáo Bệnh án (PDF)</button>
        </div>

      </div>
    </div>
  );
}
