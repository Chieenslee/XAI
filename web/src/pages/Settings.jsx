import { useState } from 'react';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../utils/apiConfig';

export default function Settings() {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleClearHistory = async () => {
    if (!window.confirm("CẢNH BÁO: Hành động này sẽ xóa toàn bộ lịch sử chẩn đoán X-quang cũ. Bạn có chắc chắn không?")) {
      return;
    }
    
    setIsDeleting(true);
    const toastId = toast.loading('Đang dọn dẹp dữ liệu...');
    
    try {
      const response = await fetch(`${API_BASE_URL}/admin/clear-db`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      if (response.ok) {
        toast.success(`Đã xóa ${data.deleted_count} hồ sơ bệnh án thành công.`, { id: toastId });
      } else {
        throw new Error(data.detail || "Lỗi xóa dữ liệu");
      }
    } catch (err) {
      console.error(err);
      toast.error(err.message || 'Không thể kết nối đến máy chủ.', { id: toastId });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleBackup = () => {
    window.location.href = `${API_BASE_URL}/admin/backup-db`;
  };

  return (
    <div className="page" style={{ animation: 'fadeIn 0.5s ease' }}>
      <div className="page-header">
        <h1 className="page-title">⚙️ Cài đặt & Dữ liệu Hệ thống</h1>
        <p className="page-subtitle">Quản lý cơ sở dữ liệu bệnh án, sao lưu và cấu hình hệ thống.</p>
      </div>

      <div className="diag-grid">
        <div className="glass-card" style={{ padding: '30px' }}>
          <h3 style={{ color: 'var(--cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Sao lưu Dữ liệu (Backup)
          </h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', lineHeight: '1.6' }}>
            Tải xuống toàn bộ cơ sở dữ liệu SQLite hiện tại (patients.db) để lưu trữ ngoại tuyến hoặc chuyển giao dữ liệu sang hệ thống máy chủ khác một cách an toàn.
          </p>
          <button className="btn-secondary" onClick={handleBackup}>
            ⬇️ Tải xuống Bản sao lưu (.db)
          </button>
        </div>

        <div className="glass-card" style={{ padding: '30px', borderColor: 'rgba(255, 107, 107, 0.2)' }}>
          <h3 style={{ color: 'var(--red)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
            Dọn dẹp Cơ sở dữ liệu (Clean up)
          </h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', lineHeight: '1.6' }}>
            Xóa vĩnh viễn toàn bộ các lịch sử chẩn đoán X-quang cũ khỏi hệ thống để giải phóng dung lượng. Hành động này không thể hoàn tác nếu chưa Backup.
          </p>
          <button 
            className="btn-primary" 
            style={{ background: 'linear-gradient(135deg, #ff4757, #ff6b81)', border: 'none', boxShadow: '0 4px 15px rgba(255,107,107,0.3)' }} 
            onClick={handleClearHistory}
            disabled={isDeleting}
          >
            {isDeleting ? '⏳ Đang xóa...' : '🗑 Xóa sạch Dữ liệu Cũ'}
          </button>
        </div>
      </div>
    </div>
  );
}
