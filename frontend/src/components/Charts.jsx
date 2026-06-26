import { useState, useRef, useEffect, useCallback } from "react";

/* ── helpers ── */
function lerp(a, b, t) { return a + (b - a) * t; }
function formatNum(v) { return Number(v || 0).toLocaleString("pt-BR"); }

/* ────────────────────────────────────────────────────
   GROUPED BAR CHART  –  compares two series side by side
   ──────────────────────────────────────────────────── */
export function GroupedBarChart({
  labels = [],
  series1 = [],
  series2 = [],
  series1Name = "Anterior",
  series2Name = "Atual",
  color1 = "#94a3b8",
  color2 = "#0048d7",
  height = 320,
}) {
  const [animProgress, setAnimProgress] = useState(0);
  const [hoveredIdx, setHoveredIdx] = useState(-1);
  const containerRef = useRef(null);

  useEffect(() => {
    let start = null;
    let raf;
    const duration = 800;
    function step(ts) {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnimProgress(t * t * (3 - 2 * t)); // smoothstep
      if (t < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [labels.join(",")]);

  const allValues = [...series1, ...series2];
  const maxVal = Math.max(...allValues, 1);

  const padL = 62, padR = 24, padT = 24, padB = 60;
  const chartW = 600 - padL - padR;
  const chartH = height - padT - padB;

  const n = labels.length || 1;
  const groupW = chartW / n;
  const barW = Math.min(groupW * 0.3, 36);
  const gap = 4;

  /* grid lines */
  const gridLines = 5;
  const gridStep = maxVal / gridLines;

  return (
    <div ref={containerRef} style={{ width: "100%", overflowX: "auto" }}>
      <svg viewBox={`0 0 600 ${height}`} style={{ width: "100%", maxWidth: 600, display: "block", margin: "0 auto" }}>
        {/* grid */}
        {Array.from({ length: gridLines + 1 }, (_, i) => {
          const y = padT + chartH - (chartH / gridLines) * i;
          const val = Math.round(gridStep * i);
          return (
            <g key={i}>
              <line x1={padL} x2={padL + chartW} y1={y} y2={y}
                stroke="var(--line, #e2e8f0)" strokeWidth={1} strokeDasharray={i === 0 ? "0" : "4,4"} />
              <text x={padL - 8} y={y + 4} textAnchor="end"
                style={{ fontSize: 11, fill: "var(--text-soft, #94a3b8)", fontFamily: "Inter, sans-serif" }}>
                {formatNum(val)}
              </text>
            </g>
          );
        })}

        {/* bars */}
        {labels.map((label, i) => {
          const cx = padL + groupW * i + groupW / 2;
          const h1 = (series1[i] / maxVal) * chartH * animProgress;
          const h2 = (series2[i] / maxVal) * chartH * animProgress;
          const isHov = hoveredIdx === i;
          return (
            <g key={i}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(-1)}
              style={{ cursor: "pointer" }}>
              {/* bar 1 */}
              <rect
                x={cx - barW - gap / 2} y={padT + chartH - h1}
                width={barW} height={h1} rx={4}
                fill={color1} opacity={isHov ? 1 : 0.75}
                style={{ transition: "opacity 0.2s" }}
              />
              {/* bar 2 */}
              <rect
                x={cx + gap / 2} y={padT + chartH - h2}
                width={barW} height={h2} rx={4}
                fill={color2} opacity={isHov ? 1 : 0.85}
                style={{ transition: "opacity 0.2s" }}
              />
              {/* label */}
              <text x={cx} y={padT + chartH + 18} textAnchor="middle"
                style={{ fontSize: 11, fill: "var(--text-soft, #64748b)", fontWeight: isHov ? 700 : 500, fontFamily: "Inter, sans-serif" }}>
                {label}
              </text>

              {/* tooltip */}
              {isHov && (
                <g>
                  <rect x={cx - 72} y={padT + chartH - Math.max(h1, h2) - 56} width={144} height={48} rx={8}
                    fill="var(--surface, #fff)" stroke="var(--line, #e2e8f0)" strokeWidth={1}
                    style={{ filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.10))" }} />
                  <text x={cx - 62} y={padT + chartH - Math.max(h1, h2) - 36}
                    style={{ fontSize: 11, fill: color1, fontWeight: 700, fontFamily: "Inter, sans-serif" }}>
                    {series1Name}: {formatNum(series1[i])}
                  </text>
                  <text x={cx - 62} y={padT + chartH - Math.max(h1, h2) - 20}
                    style={{ fontSize: 11, fill: color2, fontWeight: 700, fontFamily: "Inter, sans-serif" }}>
                    {series2Name}: {formatNum(series2[i])}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* legend */}
        <g transform={`translate(${padL}, ${height - 14})`}>
          <rect width={10} height={10} rx={2} fill={color1} />
          <text x={14} y={9} style={{ fontSize: 11, fill: "var(--text-soft, #64748b)", fontFamily: "Inter, sans-serif" }}>{series1Name}</text>
          <rect x={110} width={10} height={10} rx={2} fill={color2} />
          <text x={124} y={9} style={{ fontSize: 11, fill: "var(--text-soft, #64748b)", fontFamily: "Inter, sans-serif" }}>{series2Name}</text>
        </g>
      </svg>
    </div>
  );
}


/* ────────────────────────────────────────────────────
   DONUT CHART  –  shows proportion of each indicator
   ──────────────────────────────────────────────────── */
export function DonutChart({
  data = [], // [{label, value, color}]
  size = 220,
  thickness = 28,
}) {
  const [animProgress, setAnimProgress] = useState(0);
  const [hoveredIdx, setHoveredIdx] = useState(-1);

  useEffect(() => {
    let start = null;
    let raf;
    const duration = 900;
    function step(ts) {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnimProgress(t * t * (3 - 2 * t));
      if (t < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [data.map(d => d.value).join(",")]);

  const total = data.reduce((a, d) => a + (d.value || 0), 0) || 1;
  const cx = size / 2, cy = size / 2, r = (size - thickness) / 2;

  let cumAngle = -Math.PI / 2;
  const arcs = data.map((d, i) => {
    const fraction = (d.value || 0) / total;
    const angle = fraction * 2 * Math.PI * animProgress;
    const startAngle = cumAngle;
    cumAngle += angle;
    const endAngle = cumAngle;
    const largeArc = angle > Math.PI ? 1 : 0;

    const x1 = cx + r * Math.cos(startAngle);
    const y1 = cy + r * Math.sin(startAngle);
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy + r * Math.sin(endAngle);

    const path = angle > 0
      ? `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`
      : "";

    return { ...d, path, fraction, midAngle: (startAngle + endAngle) / 2 };
  });

  const hoveredItem = hoveredIdx >= 0 ? data[hoveredIdx] : null;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 28, flexWrap: "wrap", justifyContent: "center" }}>
      <div style={{ position: "relative", width: size, height: size }}>
        <svg width={size} height={size}>
          {/* bg ring */}
          <circle cx={cx} cy={cy} r={r} fill="none"
            stroke="var(--line, #e2e8f0)" strokeWidth={thickness} opacity={0.4} />
          {/* arcs */}
          {arcs.map((arc, i) => (
            <path key={i} d={arc.path} fill="none"
              stroke={arc.color} strokeWidth={hoveredIdx === i ? thickness + 6 : thickness}
              strokeLinecap="round"
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(-1)}
              style={{ cursor: "pointer", transition: "stroke-width 0.2s", filter: hoveredIdx === i ? "brightness(1.1)" : "none" }}
            />
          ))}
        </svg>
        {/* center label */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", pointerEvents: "none"
        }}>
          {hoveredItem ? (
            <>
              <strong style={{ fontSize: 22, fontWeight: 800, color: hoveredItem.color, lineHeight: 1 }}>
                {formatNum(hoveredItem.value)}
              </strong>
              <span style={{ fontSize: 10, color: "var(--text-soft, #64748b)", marginTop: 4, maxWidth: 80, textAlign: "center", lineHeight: 1.2 }}>
                {hoveredItem.label}
              </span>
            </>
          ) : (
            <>
              <strong style={{ fontSize: 24, fontWeight: 800, color: "var(--text, #1e293b)", lineHeight: 1 }}>
                {formatNum(total)}
              </strong>
              <span style={{ fontSize: 10, color: "var(--text-soft, #64748b)", marginTop: 4 }}>Total</span>
            </>
          )}
        </div>
      </div>

      {/* legend */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8, minWidth: 140 }}>
        {data.map((d, i) => {
          const pct = ((d.value / total) * 100).toFixed(1);
          return (
            <div key={i}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(-1)}
              style={{
                display: "flex", alignItems: "center", gap: 8, padding: "6px 10px",
                borderRadius: 8, cursor: "pointer",
                background: hoveredIdx === i ? "rgba(0,72,215,0.04)" : "transparent",
                transition: "background 0.15s"
              }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: d.color, flexShrink: 0 }} />
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text, #1e293b)", flex: 1 }}>{d.label}</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-soft, #64748b)", fontFamily: "Inter, monospace" }}>{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}


/* ────────────────────────────────────────────────────
   HORIZONTAL BAR CHART – ranking / top indicators
   ──────────────────────────────────────────────────── */
export function HorizontalBarChart({
  data = [], // [{label, value, color}]
  height: barH = 28,
  maxWidth = 500,
}) {
  const [animProgress, setAnimProgress] = useState(0);
  const [hoveredIdx, setHoveredIdx] = useState(-1);

  useEffect(() => {
    let start = null;
    let raf;
    const duration = 700;
    function step(ts) {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnimProgress(t * t * (3 - 2 * t));
      if (t < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [data.map(d => d.value).join(",")]);

  const maxVal = Math.max(...data.map(d => d.value || 0), 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, width: "100%" }}>
      {data.map((d, i) => {
        const pct = ((d.value / maxVal) * 100 * animProgress);
        const isHov = hoveredIdx === i;
        return (
          <div key={i}
            onMouseEnter={() => setHoveredIdx(i)}
            onMouseLeave={() => setHoveredIdx(-1)}
            style={{
              display: "flex", alignItems: "center", gap: 12, cursor: "pointer",
              padding: "4px 0", transition: "transform 0.15s",
              transform: isHov ? "translateX(4px)" : "none"
            }}>
            <span style={{
              fontSize: 12, fontWeight: 600, color: "var(--text, #1e293b)",
              minWidth: 140, textAlign: "right", whiteSpace: "nowrap"
            }}>
              {d.label}
            </span>
            <div style={{
              flex: 1, height: barH, borderRadius: barH / 2,
              background: "var(--surface-2, #f1f5f9)", position: "relative", overflow: "hidden"
            }}>
              <div style={{
                height: "100%", borderRadius: barH / 2,
                width: `${pct}%`,
                background: `linear-gradient(90deg, ${d.color}cc, ${d.color})`,
                transition: "width 0.3s ease",
                boxShadow: isHov ? `0 0 12px ${d.color}44` : "none"
              }} />
            </div>
            <span style={{
              fontSize: 13, fontWeight: 700, color: d.color,
              minWidth: 60, fontFamily: "Inter, monospace"
            }}>
              {formatNum(d.value)}
            </span>
          </div>
        );
      })}
    </div>
  );
}


/* ────────────────────────────────────────────────────
   VARIATION ARROW CHART – shows year-over-year % change
   ──────────────────────────────────────────────────── */
export function VariationChart({
  data = [], // [{label, percentage, color}]
}) {
  const [animProgress, setAnimProgress] = useState(0);

  useEffect(() => {
    let start = null;
    let raf;
    const duration = 600;
    function step(ts) {
      if (!start) start = ts;
      const t = Math.min((ts - start) / duration, 1);
      setAnimProgress(t * t * (3 - 2 * t));
      if (t < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [data.map(d => d.percentage).join(",")]);

  const maxAbsPct = Math.max(...data.map(d => Math.abs(d.percentage || 0)), 10);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {data.map((d, i) => {
        const pct = (d.percentage || 0);
        const barPct = (Math.abs(pct) / maxAbsPct) * 50 * animProgress;
        const isPositive = pct >= 0;
        return (
          <div key={i} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text, #1e293b)" }}>{d.label}</span>
              <span style={{
                fontSize: 13, fontWeight: 800,
                color: isPositive ? "#047857" : "#dc2626",
                fontFamily: "Inter, monospace"
              }}>
                {isPositive ? "+" : ""}{pct.toFixed(1)}%
              </span>
            </div>
            <div style={{
              display: "flex", height: 8, borderRadius: 4, overflow: "hidden",
              background: "var(--surface-2, #f1f5f9)"
            }}>
              {/* center marker */}
              <div style={{ width: "50%", display: "flex", justifyContent: "flex-end" }}>
                {!isPositive && (
                  <div style={{
                    width: `${barPct}%`, height: "100%", borderRadius: 4,
                    background: `linear-gradient(90deg, #dc2626, #dc262688)`,
                    marginLeft: "auto"
                  }} />
                )}
              </div>
              <div style={{ width: 2, background: "var(--text-soft, #94a3b8)", opacity: 0.3, flexShrink: 0 }} />
              <div style={{ width: "50%", display: "flex" }}>
                {isPositive && (
                  <div style={{
                    width: `${barPct}%`, height: "100%", borderRadius: 4,
                    background: `linear-gradient(90deg, #04785788, #047857)`
                  }} />
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
