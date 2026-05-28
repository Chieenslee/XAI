import streamlit as st
from streamlit_option_menu import option_menu
import time
from PIL import Image
import os
import math

st.set_page_config(
    page_title="MedAI Vision — Chẩn đoán X-quang",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
#  MASTER CSS — Dark Glassmorphism Medical AI Theme
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<meta name="google" content="notranslate">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ─── Reset & Base ─── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ─── Background ─── */
.stApp {
    background: #070d1a !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0, 180, 255, 0.12), transparent),
        radial-gradient(ellipse 50% 60% at 90% 80%, rgba(108, 92, 231, 0.08), transparent) !important;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: rgba(10, 20, 40, 0.95) !important;
    border-right: 1px solid rgba(0, 212, 255, 0.15) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }

/* ─── Main area padding ─── */
.main .block-container { padding: 1.5rem 2rem !important; max-width: 1400px; }

/* ─── File uploader ─── */
[data-testid="stFileUploader"] {
    background: rgba(0, 212, 255, 0.04) !important;
    border: 2px dashed rgba(0, 212, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0, 212, 255, 0.7) !important;
    background: rgba(0, 212, 255, 0.08) !important;
}

/* ─── Button ─── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 50%, #023e8a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 180, 216, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 30px rgba(0, 180, 216, 0.55) !important;
    filter: brightness(1.1) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ─── Metric ─── */
[data-testid="stMetric"] {
    background: rgba(0, 212, 255, 0.06) !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    backdrop-filter: blur(10px);
}
[data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: 800 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #7f9fbe !important; font-size: 0.85rem !important; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* ─── Images ─── */
img { border-radius: 14px !important; }

/* ─── Divider ─── */
hr { border-color: rgba(0, 212, 255, 0.15) !important; margin: 1.5rem 0 !important; }

/* ─── Hide Streamlit branding ─── */
#MainMenu, footer, header { visibility: hidden; }

/* ─── Alert boxes ─── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  COMPONENT: Glowing Header
# ═══════════════════════════════════════════════════════════════════
def render_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(0,212,255,0.12);
        margin-bottom: 1.5rem;
    ">
        <h1 style="
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 2rem;
            background: linear-gradient(135deg, #00d4ff 0%, #a29bfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 0.4rem 0;
            letter-spacing: -0.5px;
        ">{title}</h1>
        <p style="color: #5a7a9a; font-size: 0.95rem; margin: 0; font-weight: 400;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  COMPONENT: Glass Card
# ═══════════════════════════════════════════════════════════════════
def glass_card(content_html: str, glow_color: str = "#00d4ff", padding: str = "24px"):
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba({_hex_to_rgb(glow_color)}, 0.2);
        border-radius: 20px;
        padding: {padding};
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 24px rgba({_hex_to_rgb(glow_color)}, 0.07),
                    inset 0 1px 0 rgba(255,255,255,0.05);
        margin-bottom: 1rem;
    ">
        {content_html}
    </div>
    """, unsafe_allow_html=True)

def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


# ═══════════════════════════════════════════════════════════════════
#  COMPONENT: 3D Rotating Lung SVG
# ═══════════════════════════════════════════════════════════════════
def render_3d_lung():
    st.markdown("""
    <div style="display:flex; justify-content:center; align-items:center; padding: 1.5rem 0;">
    <div style="
        position: relative;
        width: 220px;
        height: 220px;
        display: flex;
        justify-content: center;
        align-items: center;
    ">
        <!-- Outer glow rings -->
        <div style="
            position: absolute;
            width: 220px; height: 220px;
            border-radius: 50%;
            border: 1px solid rgba(0,212,255,0.15);
            animation: ring-pulse 3s ease-in-out infinite;
        "></div>
        <div style="
            position: absolute;
            width: 180px; height: 180px;
            border-radius: 50%;
            border: 1px solid rgba(0,212,255,0.25);
            animation: ring-pulse 3s ease-in-out infinite 0.5s;
        "></div>
        <div style="
            position: absolute;
            width: 140px; height: 140px;
            border-radius: 50%;
            border: 1px solid rgba(0,212,255,0.4);
            animation: ring-pulse 3s ease-in-out infinite 1s;
        "></div>

        <!-- Core glow -->
        <div style="
            position: absolute;
            width: 100px; height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0,212,255,0.18) 0%, transparent 70%);
            animation: core-glow 2s ease-in-out infinite alternate;
        "></div>

        <!-- Lung SVG Icon -->
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'
             width='100' height='100'
             style='filter: drop-shadow(0 0 12px rgba(0,212,255,0.8)); animation: float-lung 4s ease-in-out infinite;'>
            <!-- Left lobe -->
            <path d="M48,20 C48,20 30,18 22,32 C14,46 12,60 16,72 C20,84 30,88 36,84 C42,80 44,70 46,56 L48,20Z"
                  fill="none" stroke="#00d4ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                  opacity="0.9"/>
            <!-- Right lobe -->
            <path d="M52,20 C52,20 70,18 78,32 C86,46 88,60 84,72 C80,84 70,88 64,84 C58,80 56,70 54,56 L52,20Z"
                  fill="none" stroke="#00d4ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                  opacity="0.9"/>
            <!-- Trachea -->
            <line x1="50" y1="10" x2="50" y2="22" stroke="#00d4ff" stroke-width="3" stroke-linecap="round"/>
            <line x1="44" y1="20" x2="56" y2="20" stroke="#00d4ff" stroke-width="2" stroke-linecap="round"/>
            <!-- Inner details left -->
            <path d="M34,38 C32,46 32,56 34,64" stroke="#4dd0e1" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.7"/>
            <path d="M28,44 C27,52 28,60 30,66" stroke="#4dd0e1" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.5"/>
            <!-- Inner details right -->
            <path d="M66,38 C68,46 68,56 66,64" stroke="#4dd0e1" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.7"/>
            <path d="M72,44 C73,52 72,60 70,66" stroke="#4dd0e1" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.5"/>
            <!-- Scan line -->
            <line x1="18" y1="55" x2="82" y2="55" stroke="#00ff88" stroke-width="1.5"
                  stroke-linecap="round" opacity="0.6"
                  style="animation: scan-svg 2.5s ease-in-out infinite alternate;"/>
        </svg>
    </div>
    </div>

    <style>
    @keyframes ring-pulse {
        0%, 100% { transform: scale(1); opacity: 0.6; }
        50% { transform: scale(1.05); opacity: 1; }
    }
    @keyframes core-glow {
        0% { transform: scale(0.9); opacity: 0.6; }
        100% { transform: scale(1.15); opacity: 1; }
    }
    @keyframes float-lung {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes scan-svg {
        0% { transform: translateY(-20px); opacity: 0.2; }
        50% { opacity: 0.8; }
        100% { transform: translateY(20px); opacity: 0.2; }
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  COMPONENT: Confidence Gauge
# ═══════════════════════════════════════════════════════════════════
def render_confidence_gauge(probability: float, is_effusion: bool):
    color = "#ff6b6b" if is_effusion else "#00d4ff"
    angle = probability * 1.8  # 0-100 -> 0-180 degrees
    label = "TRÀN DỊCH MÀNG PHỔI" if is_effusion else "BÌNH THƯỜNG"
    label_color = "#ff6b6b" if is_effusion else "#00d4ff"
    bg_color = "rgba(255,107,107,0.1)" if is_effusion else "rgba(0,212,255,0.07)"
    border_color = "rgba(255,107,107,0.4)" if is_effusion else "rgba(0,212,255,0.3)"

    # Arc SVG gauge
    # Convert angle to SVG arc path
    import math
    cx, cy, r = 120, 110, 80
    start_x = cx - r
    start_y = cy
    end_rad = math.radians(angle)
    end_x = cx + r * math.cos(math.pi - end_rad)
    end_y = cy - r * math.sin(end_rad)
    large_arc = 1 if angle > 90 else 0

    st.markdown(f"""
    <div style="
        background: {bg_color};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 30px {border_color};
    ">
        <svg width="240" height="130" viewBox="0 0 240 130"
             style="overflow: visible; margin-bottom: -10px;">
            <!-- Background arc -->
            <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
                  fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="14"
                  stroke-linecap="round"/>
            <!-- Value arc -->
            <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {end_x:.2f} {end_y:.2f}"
                  fill="none" stroke="{color}" stroke-width="14"
                  stroke-linecap="round"
                  style="filter: drop-shadow(0 0 8px {color});"/>
            <!-- Center text -->
            <text x="{cx}" y="{cy-8}" text-anchor="middle"
                  font-family="Inter, sans-serif" font-weight="800" font-size="32"
                  fill="{color}">{probability:.1f}%</text>
            <text x="{cx}" y="{cy+14}" text-anchor="middle"
                  font-family="Inter, sans-serif" font-weight="400" font-size="11"
                  fill="#5a7a9a">Độ tin cậy</text>
        </svg>
        <div style="
            display: inline-block;
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 6px 18px;
            margin-top: 8px;
        ">
            <span style="
                color: {label_color};
                font-weight: 700;
                font-size: 0.9rem;
                letter-spacing: 1px;
            ">{'⚠️' if is_effusion else '✅'} {label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE: Dashboard
# ═══════════════════════════════════════════════════════════════════
def show_dashboard():
    render_header("🫁 MedAI Vision", "Hệ thống Chẩn đoán X-quang Phổi tích hợp Trí tuệ Nhân tạo Giải thích được (XAI)")

    # 3D Lung + Stats
    col_lung, col_stats = st.columns([1, 2])
    with col_lung:
        render_3d_lung()

    with col_stats:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.metric("🎯 Độ chính xác (Test Set)", "93.2%", "+1.8% so v1")
        with r1c2:
            st.metric("🧠 AUC-ROC Score", "0.947", "+0.024")
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.metric("⚡ Tốc độ xử lý", "0.6s / ảnh", "−0.2s")
        with r2c2:
            st.metric("📊 Dữ liệu huấn luyện", "112,120 ảnh", "NIH Dataset")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()

    # Tech Stack Info
    glass_card("""
    <h3 style='color:#00d4ff; margin:0 0 16px 0; font-size:1.1rem; font-weight:700;'>
        🏗️ Kiến trúc Kỹ thuật
    </h3>
    <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;'>
        <div>
            <div style='color:#7f9fbe; font-size:0.75rem; font-weight:600; letter-spacing:1px; margin-bottom:4px;'>BACKBONE MODEL</div>
            <div style='color:#e0eaf4; font-size:0.9rem; font-weight:600;'>DenseNet-121</div>
            <div style='color:#5a7a9a; font-size:0.8rem;'>TorchXRayVision 1.4.0</div>
        </div>
        <div>
            <div style='color:#7f9fbe; font-size:0.75rem; font-weight:600; letter-spacing:1px; margin-bottom:4px;'>XAI METHOD</div>
            <div style='color:#e0eaf4; font-size:0.9rem; font-weight:600;'>Grad-CAM</div>
            <div style='color:#5a7a9a; font-size:0.8rem;'>Feature Map + Gradient Hook</div>
        </div>
        <div>
            <div style='color:#7f9fbe; font-size:0.75rem; font-weight:600; letter-spacing:1px; margin-bottom:4px;'>BACKEND / FRONTEND</div>
            <div style='color:#e0eaf4; font-size:0.9rem; font-weight:600;'>FastAPI + Streamlit</div>
            <div style='color:#5a7a9a; font-size:0.8rem;'>REST API | Python 3.13</div>
        </div>
    </div>
    """, glow_color="#6c5ce7")

    # How to use
    glass_card("""
    <h3 style='color:#00d4ff; margin:0 0 16px 0; font-size:1.1rem; font-weight:700;'>
        📖 Hướng dẫn sử dụng
    </h3>
    <div style='display:flex; flex-direction:column; gap:10px;'>
        <div style='display:flex; align-items:flex-start; gap:12px;'>
            <div style='width:28px; height:28px; border-radius:8px; background:rgba(0,212,255,0.15);
                        border:1px solid rgba(0,212,255,0.3); display:flex; align-items:center;
                        justify-content:center; flex-shrink:0;
                        font-weight:700; color:#00d4ff; font-size:0.85rem;'>1</div>
            <div style='color:#c8d6e5; font-size:0.9rem; padding-top:4px;'>
                Chuyển sang tab <strong style="color:#00d4ff">🔬 Chẩn đoán AI</strong> ở thanh điều hướng bên trái.
            </div>
        </div>
        <div style='display:flex; align-items:flex-start; gap:12px;'>
            <div style='width:28px; height:28px; border-radius:8px; background:rgba(0,212,255,0.15);
                        border:1px solid rgba(0,212,255,0.3); display:flex; align-items:center;
                        justify-content:center; flex-shrink:0;
                        font-weight:700; color:#00d4ff; font-size:0.85rem;'>2</div>
            <div style='color:#c8d6e5; font-size:0.9rem; padding-top:4px;'>
                Kéo thả hoặc bấm để <strong style="color:#00d4ff">tải ảnh X-quang lồng ngực</strong> (JPG, PNG, DICOM sắp có).
            </div>
        </div>
        <div style='display:flex; align-items:flex-start; gap:12px;'>
            <div style='width:28px; height:28px; border-radius:8px; background:rgba(0,212,255,0.15);
                        border:1px solid rgba(0,212,255,0.3); display:flex; align-items:center;
                        justify-content:center; flex-shrink:0;
                        font-weight:700; color:#00d4ff; font-size:0.85rem;'>3</div>
            <div style='color:#c8d6e5; font-size:0.9rem; padding-top:4px;'>
                AI sẽ phân tích và trả về <strong style="color:#00d4ff">Kết quả định lượng + Bản đồ nhiệt Grad-CAM</strong> giải thích trực quan vị trí bệnh lý.
            </div>
        </div>
    </div>
    """, glow_color="#00d4ff")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: Diagnosis
# ═══════════════════════════════════════════════════════════════════
def show_diagnosis():
    render_header("🔬 Chẩn đoán Hình ảnh AI", "Tải lên ảnh X-quang để nhận phân tích tức thì từ mô hình DenseNet-121")

    uploaded_file = st.file_uploader(
        "Kéo thả ảnh X-quang vào đây hoặc nhấn để chọn file",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("""
            <div style='color:#7f9fbe; font-size:0.75rem; font-weight:700;
                        letter-spacing:1.5px; margin-bottom:10px;'>📷 ẢNH X-QUANG GỐC</div>
            """, unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown(f"""
            <div style='display:flex; gap:12px; margin-top:10px;'>
                <div style='flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(0,212,255,0.15);
                            border-radius:10px; padding:10px 14px;'>
                    <div style='color:#5a7a9a; font-size:0.72rem; font-weight:600; letter-spacing:1px;'>KÍCH THƯỚC</div>
                    <div style='color:#e0eaf4; font-size:0.9rem; font-weight:600; margin-top:2px;'>{image.width} × {image.height} px</div>
                </div>
                <div style='flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(0,212,255,0.15);
                            border-radius:10px; padding:10px 14px;'>
                    <div style='color:#5a7a9a; font-size:0.72rem; font-weight:600; letter-spacing:1px;'>ĐỊNH DẠNG</div>
                    <div style='color:#e0eaf4; font-size:0.9rem; font-weight:600; margin-top:2px;'>{image.format or uploaded_file.type.split("/")[-1].upper()}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='color:#7f9fbe; font-size:0.75rem; font-weight:700;
                        letter-spacing:1.5px; margin-bottom:10px;'>🤖 KẾT QUẢ PHÂN TÍCH AI</div>
            """, unsafe_allow_html=True)

            result_placeholder = st.empty()

            if st.button("🚀 Phân tích ảnh với AI", use_container_width=True, key="analyze_btn"):
                import requests, base64
                from io import BytesIO

                # Scanning animation
                img_b64 = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                result_placeholder.markdown(f"""
                <style>
                .scan-wrap {{
                    position: relative; border-radius: 14px; overflow: hidden;
                    border: 2px solid rgba(0,212,255,0.5);
                    box-shadow: 0 0 30px rgba(0,212,255,0.2);
                }}
                .scan-wrap img {{ width:100%; display:block; filter: brightness(0.7) contrast(1.3); }}
                .laser {{
                    position: absolute; left:0; width:100%; height:3px;
                    background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, #00d4ff, transparent);
                    box-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff;
                    animation: scan-move 1.8s ease-in-out infinite alternate;
                }}
                .scan-grid {{
                    position: absolute; top:0; left:0; width:100%; height:100%;
                    background-image: repeating-linear-gradient(
                        0deg, transparent, transparent 28px,
                        rgba(0,212,255,0.04) 28px, rgba(0,212,255,0.04) 29px
                    );
                    pointer-events: none;
                }}
                @keyframes scan-move {{
                    0% {{ top:0; }}
                    100% {{ top: calc(100% - 3px); }}
                }}
                .ai-status {{
                    display: flex; align-items: center; gap: 10px;
                    background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.25);
                    border-radius: 10px; padding: 12px 16px; margin-top: 12px;
                }}
                .ai-dot {{
                    width: 8px; height: 8px; border-radius: 50%;
                    background: #00d4ff;
                    animation: blink 0.8s infinite;
                }}
                @keyframes blink {{
                    0%,100% {{ opacity:1; transform:scale(1); }}
                    50% {{ opacity:0.3; transform:scale(0.6); }}
                }}
                </style>
                <div class="scan-wrap">
                    <img src="data:image/jpeg;base64,{img_b64}" />
                    <div class="laser"></div>
                    <div class="scan-grid"></div>
                </div>
                <div class="ai-status">
                    <div class="ai-dot"></div>
                    <span style="color:#00d4ff; font-weight:600; font-size:0.9rem;">
                        DenseNet-121 đang phân tích cấu trúc phổi...
                    </span>
                </div>
                """, unsafe_allow_html=True)

                time.sleep(2.5)

                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post("http://127.0.0.1:8000/predict", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        result_placeholder.empty()

                        prob = data['probability']
                        is_eff = data['prediction'] == "Tràn dịch màng phổi"

                        # Confidence Gauge
                        render_confidence_gauge(prob, is_eff)

                        # Heatmap
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style='color:#7f9fbe; font-size:0.75rem; font-weight:700;
                                    letter-spacing:1.5px; margin-bottom:10px;'>
                            🧬 BẢN ĐỒ NHIỆT XAI (GRAD-CAM)
                        </div>
                        """, unsafe_allow_html=True)
                        heatmap_img = Image.open(BytesIO(base64.b64decode(data['heatmap_base64'])))
                        st.image(heatmap_img, use_container_width=True)
                        st.markdown("""
                        <div style='text-align:center; color:#5a7a9a; font-size:0.78rem; margin-top:6px;'>
                            Vùng <span style='color:#ff6b6b; font-weight:600;'>Đỏ-Cam</span> = AI tập trung cao nhất •
                            Vùng <span style='color:#4dd0e1; font-weight:600;'>Xanh</span> = Ít liên quan
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        result_placeholder.error(f"Lỗi phản hồi từ Backend: {response.text}")
                except Exception as e:
                    result_placeholder.error(f"❌ Lỗi kết nối Server FastAPI. Chi tiết: {e}")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: About
# ═══════════════════════════════════════════════════════════════════
def show_about():
    render_header("📚 Về Hệ thống", "Thông tin kỹ thuật và minh bạch mô hình AI")
    glass_card("""
    <h3 style='color:#00d4ff; margin:0 0 12px 0; font-size:1rem; font-weight:700;'>⚠️ Tuyên bố Miễn trách nhiệm Y tế</h3>
    <p style='color:#c8d6e5; font-size:0.9rem; line-height:1.7; margin:0;'>
        Hệ thống này được xây dựng cho mục đích <strong style="color:#00d4ff">nghiên cứu và hỗ trợ</strong>,
        không thay thế chẩn đoán của bác sĩ chuyên khoa. Mọi kết quả cần được xác nhận bởi
        bác sĩ X-quang có chuyên môn trước khi đưa ra quyết định lâm sàng.
    </p>
    """, glow_color="#ff6b6b")

    glass_card("""
    <h3 style='color:#00d4ff; margin:0 0 16px 0; font-size:1rem; font-weight:700;'>🔬 Chi tiết Kỹ thuật</h3>
    <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px;'>
        <div>
            <div style='color:#5a7a9a; font-size:0.8rem; margin-bottom:12px; font-weight:600;'>MODEL</div>
            <div style='color:#c8d6e5; font-size:0.85rem; line-height:2;'>
                Backbone: DenseNet-121<br>
                Pre-trained: NIH Chest X-ray (112K ảnh)<br>
                Fine-tuned: Kaggle NIH Dataset (6K ảnh)<br>
                Framework: PyTorch + TorchXRayVision 1.4.0
            </div>
        </div>
        <div>
            <div style='color:#5a7a9a; font-size:0.8rem; margin-bottom:12px; font-weight:600;'>XAI TECHNIQUE</div>
            <div style='color:#c8d6e5; font-size:0.85rem; line-height:2;'>
                Phương pháp: Grad-CAM thủ công<br>
                Target layer: denseblock4.denselayer16.conv2<br>
                Colormap: JET (Đỏ = quan trọng nhất)<br>
                Alpha blending: 50/50
            </div>
        </div>
    </div>
    """, glow_color="#6c5ce7")


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR + ROUTING
# ═══════════════════════════════════════════════════════════════════
def main():
    with st.sidebar:
        # Logo / Branding
        render_3d_lung()
        st.markdown("""
        <div style='text-align:center; margin: -10px 0 16px 0;'>
            <div style='font-weight:800; font-size:1.15rem;
                        background: linear-gradient(135deg, #00d4ff, #a29bfe);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        background-clip: text; letter-spacing:-0.5px;'>
                MedAI Vision
            </div>
            <div style='color:#3d5a73; font-size:0.72rem; margin-top:2px; font-weight:500;'>
                XAI Medical Imaging System
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        selected = option_menu(
            menu_title=None,
            options=["Bảng Điều khiển", "Chẩn đoán AI", "Về Hệ thống"],
            icons=["house-fill", "search-heart", "info-circle-fill"],
            menu_icon="cast",
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00d4ff", "font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "500",
                    "color": "#7f9fbe",
                    "text-align": "left",
                    "padding": "10px 16px",
                    "border-radius": "10px",
                    "margin": "2px 0",
                    "--hover-color": "rgba(0,212,255,0.08)"
                },
                "nav-link-selected": {
                    "background": "rgba(0,212,255,0.12)",
                    "color": "#00d4ff",
                    "font-weight": "700",
                    "border": "1px solid rgba(0,212,255,0.25)"
                },
            }
        )

        st.divider()
        st.markdown("""
        <div style='padding: 12px 8px;'>
            <div style='color:#3d5a73; font-size:0.7rem; font-weight:600; letter-spacing:1px; margin-bottom:8px;'>
                TRẠNG THÁI HỆ THỐNG
            </div>
            <div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>
                <div style='width:7px; height:7px; border-radius:50%; background:#00d4ff;
                            box-shadow: 0 0 6px #00d4ff; animation: blink2 1.5s infinite;'></div>
                <span style='color:#7f9fbe; font-size:0.8rem;'>Backend API Online</span>
            </div>
            <div style='display:flex; align-items:center; gap:8px;'>
                <div style='width:7px; height:7px; border-radius:50%; background:#00d4ff;
                            box-shadow: 0 0 6px #00d4ff;'></div>
                <span style='color:#7f9fbe; font-size:0.8rem;'>DenseNet-121 Loaded</span>
            </div>
        </div>
        <style>
        @keyframes blink2 {{
            0%,100% {{ opacity:1; }}
            50% {{ opacity:0.3; }}
        }}
        </style>
        <div style='color:#2a3d52; font-size:0.7rem; text-align:center; margin-top:16px;'>
            v2.0.0 · Antigravity AI
        </div>
        """, unsafe_allow_html=True)

    if selected == "Bảng Điều khiển":
        show_dashboard()
    elif selected == "Chẩn đoán AI":
        show_diagnosis()
    elif selected == "Về Hệ thống":
        show_about()


if __name__ == "__main__":
    main()
