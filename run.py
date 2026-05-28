import subprocess
import sys
import time
import os

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
    
    # Chờ 3 giây để mô hình AI kịp load vào VRAM
    print("⏳ Đang tải mô hình học sâu vào bộ nhớ...")
    time.sleep(3) 
    
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
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
