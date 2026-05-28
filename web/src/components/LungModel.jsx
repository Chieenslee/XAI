// SVG Lung 3D with rings and float animation
export default function LungModel({ size = 100 }) {
  return (
    <div className="lung-container">
      <div className="lung-wrap">
        <div className="ring" />
        <div className="ring" />
        <div className="ring" />
        <div className="lung-core" />
        <svg className="lung-svg" xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 100 100" width={size} height={size}>
          {/* Left lobe */}
          <path d="M48,20 C48,20 30,18 22,32 C14,46 12,60 16,72 C20,84 30,88 36,84 C42,80 44,70 46,56 L48,20Z"
            fill="none" stroke="#00d4ff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
          {/* Right lobe */}
          <path d="M52,20 C52,20 70,18 78,32 C86,46 88,60 84,72 C80,84 70,88 64,84 C58,80 56,70 54,56 L52,20Z"
            fill="none" stroke="#00d4ff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
          {/* Trachea */}
          <line x1="50" y1="10" x2="50" y2="22" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" />
          <line x1="44" y1="20" x2="56" y2="20" stroke="#00d4ff" strokeWidth="2" strokeLinecap="round" />
          {/* Inner veins left */}
          <path d="M34,38 C32,46 32,56 34,64" stroke="#4dd0e1" strokeWidth="1.2" fill="none" strokeLinecap="round" opacity="0.65" />
          <path d="M28,44 C27,52 28,60 30,66" stroke="#4dd0e1" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />
          {/* Inner veins right */}
          <path d="M66,38 C68,46 68,56 66,64" stroke="#4dd0e1" strokeWidth="1.2" fill="none" strokeLinecap="round" opacity="0.65" />
          <path d="M72,44 C73,52 72,60 70,66" stroke="#4dd0e1" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.45" />
          {/* Animated scan line */}
          <line x1="18" y1="55" x2="82" y2="55"
            stroke="#00ff88" strokeWidth="1.5" strokeLinecap="round" opacity="0.6">
            <animate attributeName="y1" values="20;80;20" dur="2.8s" repeatCount="indefinite" />
            <animate attributeName="y2" values="20;80;20" dur="2.8s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.1;0.8;0.1" dur="2.8s" repeatCount="indefinite" />
          </line>
        </svg>
      </div>
    </div>
  );
}
