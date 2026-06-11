import { useRef } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import toast from 'react-hot-toast';

export default function ResultModal({ result, preview, onClose, onNext }) {
  const isEffusion = result.prediction === "Tràn dịch màng phổi";
  const confidence = isEffusion ? result.probability : 100 - result.probability;
  const printRef = useRef();

  const explanation = result.explanation || (isEffusion
    ? `Phân tích XAI Grad-CAM++ phát hiện dải mờ cản quang bất thường tập trung tại vùng góc sườn hoành. Độ tin cậy: ${confidence.toFixed(1)}%. Khuyến nghị siêu âm màng phổi để xác nhận.`
    : `Không phát hiện vùng mờ bất thường tại lồng ngực. Các góc sườn hoành hai bên sắc nét. Độ tin cậy: ${confidence.toFixed(1)}%.`);

  const waitForImages = async (element) => {
    const images = Array.from(element.querySelectorAll('img'));
    await Promise.all(images.map((img) => {
      if (img.complete && img.naturalWidth > 0) return Promise.resolve();
      return new Promise((resolve) => {
        img.onload = resolve;
        img.onerror = resolve;
      });
    }));
  };

  // Render DOM thay vì tự ghi text bằng font mặc định của jsPDF.
  // Cách này giữ đúng tiếng Việt, icon và layout như đang hiển thị trên modal.
  const handleExportPDF = async () => {
    const toastId = toast.loading('Đang tạo báo cáo PDF...');
    try {
      const reportElement = printRef.current;
      if (!reportElement) throw new Error('Không tìm thấy nội dung báo cáo.');

      await waitForImages(reportElement);

      const canvas = await html2canvas(reportElement, {
        backgroundColor: '#0f172a',
        scale: Math.min(window.devicePixelRatio || 1, 2),
        useCORS: true,
        allowTaint: false,
        logging: false,
      });

      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 8;
      const contentWidth = pageWidth - margin * 2;
      const pageCanvasHeight = Math.floor((pageHeight - margin * 2) * canvas.width / contentWidth);
      let sourceY = 0;
      let pageIndex = 0;

      while (sourceY < canvas.height) {
        const sliceHeight = Math.min(pageCanvasHeight, canvas.height - sourceY);
        const pageCanvas = document.createElement('canvas');
        pageCanvas.width = canvas.width;
        pageCanvas.height = sliceHeight;

        const ctx = pageCanvas.getContext('2d');
        ctx.drawImage(canvas, 0, sourceY, canvas.width, sliceHeight, 0, 0, canvas.width, sliceHeight);

        if (pageIndex > 0) pdf.addPage();

        const imgData = pageCanvas.toDataURL('image/jpeg', 0.95);
        const imgHeight = sliceHeight * contentWidth / canvas.width;
        pdf.addImage(imgData, 'JPEG', margin, margin, contentWidth, imgHeight);

        sourceY += sliceHeight;
        pageIndex += 1;
      }

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
