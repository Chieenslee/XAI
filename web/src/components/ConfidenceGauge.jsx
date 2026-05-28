import { useMemo } from 'react';

// Arc SVG Gauge showing confidence %
export default function ConfidenceGauge({ probability, isEffusion }) {
  const color     = isEffusion ? '#ff6b6b' : '#00d4ff';
  const typeClass = isEffusion ? 'effusion' : 'normal';
  const label     = isEffusion ? '⚠️ TRÀN DỊCH MÀNG PHỔI' : '✅ BÌNH THƯỜNG';
  
  // Tính toán độ tin cậy thực sự của dự đoán (luôn >= 50%)
  const confidence = isEffusion ? probability : 100 - probability;

  // Build SVG arc path (semicircle 180°)
  const arc = useMemo(() => {
    const cx = 120, cy = 110, r = 80;
    const angle = (confidence / 100) * 180;           // 0-180 deg
    const rad   = (Math.PI / 180) * (180 - angle);     // measure from left
    const ex    = cx + r * Math.cos(rad);
    const ey    = cy - r * Math.sin(rad);
    const large = angle > 90 ? 1 : 0;
    return `M ${cx - r} ${cy} A ${r} ${r} 0 ${large} 1 ${ex.toFixed(2)} ${ey.toFixed(2)}`;
  }, [confidence]);

  return (
    <div className={`gauge-card ${typeClass}`}>
      <svg width="240" height="130" viewBox="0 0 240 130" style={{ overflow: 'visible' }}>
        {/* Background arc */}
        <path d="M 40 110 A 80 80 0 0 1 200 110"
          fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="14" strokeLinecap="round" />
        {/* Value arc */}
        <path d={arc}
          fill="none" stroke={color} strokeWidth="14" strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 8px ${color})` }} />
        {/* Center value */}
        <text x="120" y="98" textAnchor="middle"
          fontFamily="Inter,sans-serif" fontWeight="800" fontSize="30" fill={color}>
          {confidence.toFixed(1)}%
        </text>
        <text x="120" y="116" textAnchor="middle"
          fontFamily="Inter,sans-serif" fontWeight="400" fontSize="11" fill="#5a7a9a">
          Độ tin cậy AI
        </text>
      </svg>
      <div className={`gauge-label ${typeClass}`}>{label}</div>
    </div>
  );
}
