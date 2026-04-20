/* ============================================================
   農業資料視覺化儀表板 — 元件
   依賴：React 18, data.js, 全域 DATA / COUNTY_GEO
   ============================================================ */

const { useState, useMemo, useEffect, useRef } = React;
const D = window.DATA;
const GEO = window.COUNTY_GEO;

// === Utility ===
const fmt = (n, d = 0) => n == null ? "—" : n.toLocaleString("zh-TW", { maximumFractionDigits: d, minimumFractionDigits: d });
const fmtPct = (n, d = 1) => n == null ? "—" : (n * 100).toFixed(d) + "%";

function useTooltip() {
  const [tt, setTT] = useState(null);
  useEffect(() => {
    function mv(e) { if (tt) setTT(t => t ? { ...t, x: e.clientX, y: e.clientY } : t); }
    window.addEventListener("mousemove", mv);
    return () => window.removeEventListener("mousemove", mv);
  }, [tt]);
  return [tt, setTT];
}

// === Brand ===
function Brand() {
  return (
    <div className="brand">
      <div className="brand-mark"></div>
      <div>
        <div className="brand-title">農業資料視覺化</div>
        <div className="brand-sub">AGRI-DATA · 115</div>
      </div>
    </div>
  );
}

// === Topbar ===
function Topbar({ page, onPrint }) {
  const crumbs = {
    overview: "總覽",
    map: "縣市風險地圖",
    crop: "作物 × 農藥矩陣",
    pesticide: "農藥抗藥性預警",
    detail: "深度檢視",
  };
  return (
    <div className="topbar">
      <div className="crumb">
        農業部資料治理平臺　/　<b>{crumbs[page]}</b>
      </div>
      <div className="topbar-sep"></div>
      <div className="topbar-meta">
        <span><span className="dot"></span>資料新鮮度 2026-04-13</span>
        <span>N = {fmt(D.meta.pesticideCount)} 筆登記 × {D.meta.matchedCount} 作物</span>
      </div>
      <button className="icon-btn" title="匯出" onClick={onPrint}>⬇ 匯出</button>
      <button className="icon-btn" title="列印" onClick={() => window.print()}>⎙</button>
    </div>
  );
}

// === Nav ===
function Nav({ page, setPage }) {
  const items = [
    { id: "overview", n: "01", name: "總覽" },
    { id: "map", n: "02", name: "縣市地圖" },
    { id: "crop", n: "03", name: "作物矩陣" },
    { id: "pesticide", n: "04", name: "抗藥性預警" },
    { id: "detail", n: "05", name: "深度檢視" },
  ];
  return (
    <div className="nav">
      <div className="nav-section">分析主題</div>
      {items.map(it => (
        <div key={it.id}
             className={"nav-item " + (page === it.id ? "active" : "")}
             onClick={() => setPage(it.id)}>
          <span className="n">{it.n}</span>
          <span>{it.name}</span>
        </div>
      ))}
      <div className="nav-section">資料集</div>
      <div className="nav-item"><span className="n">A</span>農藥登記 11,784</div>
      <div className="nav-item"><span className="n">B</span>農情調查 234</div>
      <div className="nav-item"><span className="n">C</span>IRAC / FRAC</div>
      <div className="nav-foot">
        報告 v2026.04.13<br/>
        資料基礎：pesticide_full.csv<br/>
        × agri_clean.csv
      </div>
    </div>
  );
}

// === KPI card ===
function KPI({ label, value, unit, trend, tone, spark }) {
  return (
    <div className="kpi" data-tone={tone}>
      <div className="kpi-accent"></div>
      <div className="kpi-label">{label}</div>
      <div>
        <span className="kpi-value tabular">{value}</span>
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>
      {trend && <div className="kpi-trend">{trend}</div>}
      {spark && <svg className="kpi-spark" width="60" height="24" viewBox="0 0 60 24">
        <polyline fill="none" stroke="var(--ink-4)" strokeWidth="1" points={spark}/>
      </svg>}
    </div>
  );
}

// === Risk color ramp ===
function riskColor(v, max) {
  const t = Math.min(1, v / max);
  const bucket = t < 0.15 ? 0 : t < 0.3 ? 1 : t < 0.5 ? 2 : t < 0.75 ? 3 : 4;
  return ["var(--risk-1)", "var(--risk-2)", "var(--risk-3)", "var(--risk-4)", "var(--risk-5)"][bucket];
}

// === SVG-based Taiwan map (stylized square blocks per county) ===
function TaiwanMap({ selected, onSelect, setTT }) {
  const byCounty = Object.fromEntries(D.countyRisk.map(c => [c.county, c]));
  const max = Math.max(...D.countyRisk.map(c => c.exposure));

  return (
    <svg className="map-svg" viewBox="0 0 400 560" preserveAspectRatio="xMidYMid meet">
      {/* Decorative coast */}
      <path d="M 200 20 Q 290 40 300 140 Q 310 260 280 360 Q 250 460 180 500 Q 140 470 130 400 Q 100 300 120 200 Q 140 60 200 20 Z"
            fill="color-mix(in oklab, var(--forest) 3%, var(--bg-panel))"
            stroke="var(--rule)" strokeWidth="0.6" strokeDasharray="2,3" opacity="0.6"/>
      {/* Grid ref labels */}
      {[120, 240, 360, 480].map(y => (
        <text key={y} x="8" y={y} fill="var(--ink-4)" fontFamily="var(--mono)" fontSize="8">{y}</text>
      ))}

      {Object.entries(GEO).map(([name, pos]) => {
        const d = byCounty[name];
        if (!d) return null;
        const sel = selected === name;
        const size = pos.size;
        return (
          <g key={name} className={"county " + (sel ? "selected" : "")}
             onClick={() => onSelect(name)}
             onMouseEnter={e => setTT({
               x: e.clientX, y: e.clientY,
               title: name,
               body: `加權風險 ${fmt(d.exposure, 0)}　面積 ${fmt(d.area, 0)} ha\n前3作物：${d.topCrops.join("、")}`
             })}
             onMouseLeave={() => setTT(null)}>
            <rect x={pos.cx - size/2} y={pos.cy - size/2}
                  width={size} height={size}
                  className="county-fill"
                  fill={riskColor(d.exposure, max)}/>
            <text x={pos.cx} y={pos.cy + size/2 + 10} className="county-label">{name.replace(/[縣市]$/, "")}</text>
          </g>
        );
      })}

      {/* North arrow */}
      <g transform="translate(350, 40)">
        <polygon points="0,-10 6,10 0,4 -6,10" fill="var(--ink-3)"/>
        <text y="24" textAnchor="middle" fontFamily="var(--mono)" fontSize="9" fill="var(--ink-3)">N</text>
      </g>
      {/* Scale */}
      <g transform="translate(320, 540)">
        <line x1="0" y1="0" x2="60" y2="0" stroke="var(--ink-3)" strokeWidth="1"/>
        <text x="30" y="-4" textAnchor="middle" fontFamily="var(--mono)" fontSize="9" fill="var(--ink-3)">~100 km</text>
      </g>
    </svg>
  );
}

// === Tooltip ===
function Tooltip({ tt }) {
  if (!tt) return null;
  return (
    <div className="tt" style={{ left: tt.x, top: tt.y }}>
      <b>{tt.title}</b><br/>
      <span style={{ whiteSpace: "pre-line" }}>{tt.body}</span>
    </div>
  );
}

// === Bar chart ===
function BarChart({ data, max, colorFn, format }) {
  const fmtF = format || (v => fmt(v, 0));
  return (
    <div className="bar-chart">
      {data.map((d, i) => (
        <div className="row" key={i}>
          <div className="label">{d.label}</div>
          <div className="track">
            <div className="fill" style={{ width: (d.value / max * 100) + "%", background: colorFn ? colorFn(d, i) : "var(--forest)" }}></div>
          </div>
          <div className="val">{fmtF(d.value)}</div>
        </div>
      ))}
    </div>
  );
}

// === Donut ===
function Donut({ data, size = 160 }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  let acc = 0;
  const R = size/2 - 6;
  const C = 2 * Math.PI * R;
  return (
    <svg className="donut" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={R} fill="none" stroke="var(--bg-sunken)" strokeWidth="18"/>
      {data.map((d, i) => {
        const frac = d.value / total;
        const dash = frac * C;
        const off = -acc * C;
        acc += frac;
        return (
          <circle key={i} cx={size/2} cy={size/2} r={R} fill="none"
                  stroke={d.color} strokeWidth="18"
                  strokeDasharray={`${dash} ${C - dash}`}
                  strokeDashoffset={off}
                  transform={`rotate(-90 ${size/2} ${size/2})`}/>
        );
      })}
      <text x={size/2} y={size/2 - 2} textAnchor="middle"
            fontFamily="var(--sans)" fontSize="18" fontWeight="600" fill="var(--ink)">
        {fmt(total)}
      </text>
      <text x={size/2} y={size/2 + 14} textAnchor="middle"
            fontFamily="var(--mono)" fontSize="9" fill="var(--ink-3)">TOTAL</text>
    </svg>
  );
}

Object.assign(window, { D, GEO, fmt, fmtPct, useTooltip, Brand, Topbar, Nav, KPI, riskColor, TaiwanMap, Tooltip, BarChart, Donut });
