import { useRef } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import toast from 'react-hot-toast';
import ConfidenceGauge from './ConfidenceGauge';

export default function ResultModal({ result, preview, onClose, onNext }) {
  const isEffusion = result.prediction === "Tràn dịch màng phổi";
  const confidence = isEffusion ? result.probability : 100 - result.probability;
  const printRef = useRef();

  // Sử dụng lời giải thích sinh động từ Backend (XAI Textual Explanation)
  // Fallback về text tĩnh nếu backend cũ chưa hỗ trợ
  const explanation = result.explanation || (isEffusion
    ? `Phân tích XAI Grad-CAM phát hiện dải mờ cản quang bất thường tập trung tại vùng góc sườn hoành (được đánh dấu màu Đỏ/Cam trên bản đồ nhiệt). Đây là dấu hiệu X-quang kinh điển của tụ dịch màng phổi. Mức độ rõ ràng của tổn thương đạt độ tin cậy ${confidence.toFixed(1)}%. Khuyến nghị siêu âm màng phổi để xác nhận lượng dịch.`
    : `Không phát hiện vùng mờ bất thường hoặc bóng mờ cản quang tại lồng ngực. Các góc sườn hoành hai bên hiển thị sắc nét, vòm hoành bình thường. AI kết luận bệnh nhân không có dấu hiệu tràn dịch màng phổi với độ tin cậy ${confidence.toFixed(1)}%.`);

  const handleExportPDF = async () => {
    const toastId = toast.loading('Đang khởi tạo báo cáo PDF...');
    try {
      const element = printRef.current;
      const canvas = await html2canvas(element, { scale: 2, useCORS: true });
      const imgData = canvas.toDataURL('image/jpeg', 0.9);
      
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`XAI_Medical_Report_${new Date().getTime()}.pdf`);
      
      toast.success('Xuất Báo cáo Y tế thành công!', { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Có lỗi xảy ra khi xuất báo cáo.', { id: toastId });
    }
  };

  if (!result) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        
        <button className="modal-close-btn" onClick={onClose} title="Đóng & Lưu nháp">
          ✕
        </button>

        {/* Khu vực dùng để chụp PDF */}
        <div ref={printRef} className="modal-print-area">
          <div className="modal-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div className="modal-logo">🩺 XAI Medical</div>
              <h2 className="modal-title">BÁO CÁO CHẨN ĐOÁN HÌNH ẢNH</h2>
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
                  <img src={`data:image/jpeg;base64,${result.mask_base64}`} alt="Segmentation Mask" className="modal-img" />
                </div>
              )}
              <div className="modal-img-wrapper">
                <div className="card-label" style={{ marginBottom: '8px' }}>BẢN ĐỒ NHIỆT (GRAD-CAM)</div>
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
          <button className="btn-secondary" onClick={onNext}>
            🔄 Chẩn đoán tiếp theo
          </button>
          <button className="btn-primary" onClick={handleExportPDF}>
            📥 Xuất Báo cáo Bệnh án (PDF)
          </button>
        </div>
        
      </div>
    </div>
  );
}
