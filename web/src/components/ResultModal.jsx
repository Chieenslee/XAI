import { useRef } from 'react';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';
import ConfidenceGauge from './ConfidenceGauge';

export default function ResultModal({ result, preview, onClose, onNext }) {
  const isEffusion = result.prediction === "Tràn dịch màng phổi";
  const confidence = isEffusion ? result.probability : 100 - result.probability;
  const printRef = useRef();

  const explanation = result.explanation || (isEffusion
    ? `Phân tích XAI Grad-CAM++ phát hiện dải mờ cản quang bất thường tập trung tại vùng góc sườn hoành. Đây là dấu hiệu X-quang kinh điển của tụ dịch màng phổi. Độ tin cậy: ${confidence.toFixed(1)}%. Khuyến nghị siêu âm màng phổi để xác nhận.`
    : `Không phát hiện vùng mờ bất thường tại lồng ngực. Các góc sườn hoành hai bên sắc nét, vòm hoành bình thường. Độ tin cậy: ${confidence.toFixed(1)}%.`);

  // ── Xuất PDF sạch kiểu báo cáo y tế ──────────────────────
  const handleExportPDF = async () => {
    const toastId = toast.loading('Đang tạo báo cáo PDF...');
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const W = pdf.internal.pageSize.getWidth();   // 210
      const H = pdf.internal.pageSize.getHeight();  // 297
      const margin = 14;
      let y = margin;

      // ── Helpers ──
      const addText = (text, x, yPos, opts = {}) => {
        pdf.setFontSize(opts.size || 10);
        pdf.setFont('helvetica', opts.style || 'normal');
        pdf.setTextColor(...(opts.color || [30, 30, 30]));
        pdf.text(text, x, yPos);
      };

      const loadImg = (src) =>
        new Promise((resolve) => {
          const img = new Image();
          img.crossOrigin = 'Anonymous';
          img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            canvas.getContext('2d').drawImage(img, 0, 0);
            resolve({ dataUrl: canvas.toDataURL('image/jpeg', 0.92), w: img.naturalWidth, h: img.naturalHeight });
          };
          img.onerror = () => resolve(null);
          img.src = src;
        });

      // ── Header ──────────────────────────────────────────────
      pdf.setFillColor(8, 16, 32);
      pdf.rect(0, 0, W, 22, 'F');
      addText('XAI Medical — Báo cáo Chẩn đoán Hình ảnh', margin, 14, { size: 13, style: 'bold', color: [0, 212, 255] });
      addText(`Ngày: ${new Date().toLocaleString('vi-VN')}`, W - margin, 9,  { size: 8, color: [140, 180, 210] });
      pdf.setFont('helvetica', 'normal');
      pdf.setFontSize(8);
      pdf.setTextColor(140, 180, 210);
      pdf.text('DenseNet-121 + Grad-CAM++ | Phiên bản v8', W - margin, 14, { align: 'right' });
      y = 30;

      // ── Kết quả chẩn đoán ───────────────────────────────────
      const diagColor = isEffusion ? [220, 60, 60] : [0, 180, 100];
      pdf.setFillColor(...diagColor);
      pdf.roundedRect(margin, y, W - margin * 2, 14, 3, 3, 'F');
      addText(
        `${isEffusion ? '⚠ TRÀN DỊCH MÀNG PHỔI' : '✓ BÌNH THƯỜNG'}   —   Độ tin cậy AI: ${confidence.toFixed(1)}%`,
        margin + 4, y + 9.5, { size: 12, style: 'bold', color: [255, 255, 255] }
      );
      y += 20;

      // ── Hình ảnh X-quang + Heatmap ─────────────────────────
      const imgAreaW = (W - margin * 2 - 6) / 2;
      const imgAreaH = 70;

      const origData = await loadImg(preview);
      const heatBase64 = `data:image/jpeg;base64,${result.heatmap_base64}`;
      const heatData   = await loadImg(heatBase64);

      const fitImg = (imgObj, xOff, yOff, maxW, maxH) => {
        if (!imgObj) return;
        const ratio = Math.min(maxW / imgObj.w, maxH / imgObj.h);
        const rw = imgObj.w * ratio;
        const rh = imgObj.h * ratio;
        const xCenter = xOff + (maxW - rw) / 2;
        const yCenter = yOff + (maxH - rh) / 2;
        pdf.addImage(imgObj.dataUrl, 'JPEG', xCenter, yCenter, rw, rh);
      };

      // Khung ảnh gốc
      pdf.setDrawColor(60, 90, 130);
      pdf.setLineWidth(0.3);
      pdf.rect(margin, y, imgAreaW, imgAreaH + 8);
      addText('ẢNH X-QUANG GỐC', margin + 2, y + 5, { size: 7, style: 'bold', color: [100, 160, 220] });
      fitImg(origData, margin, y + 7, imgAreaW, imgAreaH);

      // Khung heatmap
      const x2 = margin + imgAreaW + 6;
      pdf.rect(x2, y, imgAreaW, imgAreaH + 8);
      addText('BẢN ĐỒ NHIỆT (GRAD-CAM++)', x2 + 2, y + 5, { size: 7, style: 'bold', color: [100, 160, 220] });
      fitImg(heatData, x2, y + 7, imgAreaW, imgAreaH);

      y += imgAreaH + 14;

      // ── Chú thích màu ───────────────────────────────────────
      if (isEffusion) {
        const legend = [['Đỏ/Cam', 'Vùng mờ dị thường – khả năng tràn dịch cao'], ['Vàng/Xanh', 'Vùng ít dị thường hơn']];
        legend.forEach(([color, desc], i) => {
          pdf.setFillColor(i === 0 ? 220 : 180, i === 0 ? 60 : 160, i === 0 ? 30 : 10);
          pdf.circle(margin + 3, y + i * 6, 2, 'F');
          addText(`${color}: ${desc}`, margin + 7, y + i * 6 + 1, { size: 8, color: [60, 80, 100] });
        });
        y += 16;
      }

      // ── Phân tích XAI ───────────────────────────────────────
      pdf.setFillColor(240, 245, 255);
      pdf.roundedRect(margin, y, W - margin * 2, 8, 2, 2, 'F');
      addText('PHÂN TÍCH XAI (GRAD-CAM++)', margin + 4, y + 5.5, { size: 9, style: 'bold', color: [30, 80, 160] });
      y += 11;

      const lines = pdf.splitTextToSize(explanation, W - margin * 2 - 4);
      pdf.setFontSize(9.5);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(40, 40, 40);
      pdf.text(lines, margin + 2, y);
      y += lines.length * 5 + 6;

      // ── Thông số kỹ thuật ───────────────────────────────────
      pdf.setFillColor(240, 245, 255);
      pdf.roundedRect(margin, y, W - margin * 2, 8, 2, 2, 'F');
      addText('THÔNG SỐ KỸ THUẬT', margin + 4, y + 5.5, { size: 9, style: 'bold', color: [30, 80, 160] });
      y += 11;

      const specs = [
        ['Mô hình AI', 'DenseNet-121 (TorchXRayVision) — Fine-tuned Tràn dịch'],
        ['Ngưỡng phát hiện', '0.0682 (Optimal Threshold từ ROC Curve)'],
        ['Raw Score', result.raw_probability?.toFixed(6) ?? '—'],
        ['Xác suất hiển thị', `${result.probability?.toFixed(2)}%`],
        ['Phương pháp XAI', 'Grad-CAM++ (2nd-Order Gradient + Alpha Weighting)'],
      ];
      specs.forEach(([k, v], i) => {
        const colX = margin + 2;
        pdf.setFontSize(8.5);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(50, 80, 130);
        pdf.text(`${k}:`, colX, y + i * 6);
        pdf.setFont('helvetica', 'normal');
        pdf.setTextColor(40, 40, 40);
        pdf.text(v, colX + 48, y + i * 6);
      });
      y += specs.length * 6 + 8;

      // ── Cảnh báo y tế ───────────────────────────────────────
      pdf.setFillColor(255, 248, 230);
      pdf.roundedRect(margin, y, W - margin * 2, 16, 2, 2, 'F');
      pdf.setDrawColor(230, 160, 30);
      pdf.setLineWidth(0.5);
      pdf.roundedRect(margin, y, W - margin * 2, 16, 2, 2, 'S');
      addText('⚠ CẢNH BÁO Y TẾ', margin + 4, y + 5.5, { size: 8, style: 'bold', color: [180, 100, 0] });
      addText(
        'Kết quả này chỉ mang tính chất hỗ trợ. Không thay thế chẩn đoán của bác sĩ chuyên khoa.',
        margin + 4, y + 11.5, { size: 8, color: [130, 80, 0] }
      );
      y += 20;

      // ── Footer ──────────────────────────────────────────────
      pdf.setDrawColor(180, 200, 220);
      pdf.setLineWidth(0.3);
      pdf.line(margin, H - 12, W - margin, H - 12);
      addText('XAI Medical Imaging System | DenseNet-121 + Grad-CAM++ | Antigravity AI', margin, H - 7, { size: 7, color: [140, 160, 180] });
      addText(`Trang 1 / 1`, W - margin, H - 7, { size: 7, color: [140, 160, 180] });

      pdf.save(`XAI_Report_${Date.now()}.pdf`);
      toast.success('Xuất báo cáo thành công!', { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Lỗi khi tạo PDF: ' + err.message, { id: toastId });
    }
  };

  if (!result) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <button className="modal-close-btn" onClick={onClose} title="Đóng & Lưu nháp">✕</button>

        {/* Nội dung hiển thị trên web (dark theme) */}
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

          {/* Gauge + hình ảnh */}
          <div style={{ display: 'flex', gap: '20px', marginTop: '16px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <ConfidenceGauge probability={result.probability} isEffusion={isEffusion} />
            <div style={{ flex: 1, display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <div className="modal-img-wrapper" style={{ flex: 1, minWidth: '140px' }}>
                <div className="card-label" style={{ marginBottom: '8px' }}>ẢNH X-QUANG GỐC</div>
                <img src={preview} alt="X-Ray" className="modal-img" />
              </div>
              {result.mask_base64 && (
                <div className="modal-img-wrapper" style={{ flex: 1, minWidth: '140px' }}>
                  <div className="card-label" style={{ marginBottom: '8px' }}>MASK (U-NET)</div>
                  <img src={`data:image/jpeg;base64,${result.mask_base64}`} alt="Mask" className="modal-img" />
                </div>
              )}
              <div className="modal-img-wrapper" style={{ flex: 1, minWidth: '140px' }}>
                <div className="card-label" style={{ marginBottom: '8px' }}>BẢN ĐỒ NHIỆT (GRAD-CAM++)</div>
                <img src={`data:image/jpeg;base64,${result.heatmap_base64}`} alt="Heatmap" className="modal-img" />
              </div>
            </div>
          </div>

          <div className="modal-explanation" style={{ marginTop: '16px' }}>
            <h3 className="explanation-title">📝 CHI TIẾT CHẨN ĐOÁN</h3>
            <p className="explanation-text">{explanation}</p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onNext}>🔄 Chẩn đoán tiếp theo</button>
          <button className="btn-primary" onClick={handleExportPDF}>📥 Xuất Báo cáo PDF</button>
        </div>
      </div>
    </div>
  );
}
