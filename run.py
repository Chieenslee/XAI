import subprocess
import sys
import time
import os
import signal

# Fix lỗi hiển thị Unicode (Emoji) trên Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=====================================================")
    print("🚀 KHỞI ĐỘNG HỆ THỐNG TRỢ LÝ Y KHOA XAI - ANTIGRAVITY")
    print("=====================================================\n")
    
    python_exe = sys.executable
    
    # 1. Start Backend FastAPI
    print("⏳ [1/2] Đang khởi động Não Bộ AI (FastAPI) tại cổng 8000...")
    backend_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        env=os.environ.copy()
    )
    
    # Chờ backend khởi động hoàn tất bằng cách kiểm tra cổng 8000
    print("⏳ Đang tải mô hình học sâu vào bộ nhớ (Vui lòng đợi 5-10s)...")
    import socket
    start_time = time.time()
    while True:
        try:
            with socket.create_connection(("127.0.0.1", 8000), timeout=1):
                break
        except (ConnectionRefusedError, socket.timeout, OSError):
            if time.time() - start_time > 30:
                print("❌ Lỗi: Backend không khởi động được sau 30 giây!")
                break
            time.sleep(1)
            
    print("✅ Mô hình AI đã tải xong!")
    
    # 2. Start Frontend React (Vite)
    print("🎨 [2/2] Đang khởi động Giao diện Web (React Vite)...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "web"),
        shell=True,
        env=os.environ.copy()
    )
    
    print("\n✅ Hệ thống đã hoạt động hoàn toàn.")
    print("🌐 Truy cập: http://localhost:5173")
    print("Nhấn Ctrl+C để tắt hệ thống.")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Đang tắt toàn bộ hệ thống. Tạm biệt!")
        # Trên Windows, gửi CTRL_C_EVENT để tắt sạch uvicorn reload và các process con
        try:
            backend_process.send_signal(signal.CTRL_C_EVENT)
            frontend_process.send_signal(signal.CTRL_C_EVENT)
        except (AttributeError, ValueError):
            backend_process.terminate()
            frontend_process.terminate()


if __name__ == "__main__":
    main()
