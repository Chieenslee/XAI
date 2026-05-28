export default function About() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📚 Về Hệ thống</h1>
        <p className="page-subtitle">Thông tin kỹ thuật và minh bạch mô hình AI</p>
      </div>

      <div className="glass-card red-glow">
        <h3 style={{ color: '#00d4ff', fontSize: '1rem', marginBottom: '12px' }}>⚠️ Tuyên bố Miễn trách nhiệm Y tế</h3>
        <p style={{ color: '#c8d6e5', fontSize: '0.9rem', lineHeight: 1.7 }}>
          Hệ thống này được xây dựng cho mục đích <strong style={{ color: '#00d4ff' }}>nghiên cứu và hỗ trợ</strong>,
          không thay thế chẩn đoán của bác sĩ chuyên khoa. Mọi kết quả cần được xác nhận bởi
          bác sĩ X-quang có chuyên môn trước khi đưa ra quyết định lâm sàng.
        </p>
      </div>

      <div className="glass-card purple-glow">
        <h3 style={{ color: '#00d4ff', fontSize: '1rem', marginBottom: '16px' }}>🔬 Chi tiết Kỹ thuật</h3>
        <div className="about-grid">
          <div>
            <div style={{ color: '#5a7a9a', fontSize: '0.8rem', fontWeight: 600, marginBottom: '12px' }}>MODEL</div>
            <div style={{ color: '#c8d6e5', fontSize: '0.85rem', lineHeight: 2 }}>
              Backbone: DenseNet-121<br/>
              Pre-trained: NIH Chest X-ray (112K ảnh)<br/>
              Fine-tuned: Kaggle NIH Dataset (6K ảnh)<br/>
              Framework: PyTorch + TorchXRayVision 1.4.0
            </div>
          </div>
          <div>
            <div style={{ color: '#5a7a9a', fontSize: '0.8rem', fontWeight: 600, marginBottom: '12px' }}>XAI TECHNIQUE</div>
            <div style={{ color: '#c8d6e5', fontSize: '0.85rem', lineHeight: 2 }}>
              Phương pháp: Grad-CAM thủ công<br/>
              Target layer: denseblock4.denselayer16.conv2<br/>
              Colormap: JET (Đỏ = quan trọng nhất)<br/>
              Alpha blending: 50/50
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
