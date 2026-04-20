/* ============================================================
   農業資料視覺化儀表板 — 頁面
   依賴：components.jsx
   ============================================================ */

// === Overview Page ===
function OverviewPage({ showKPIs, onPickCrop, onPickCounty }) {
  const maxA = D.cropRisk[0].exposure;
  const maxC = D.countyRisk[0].exposure;
  const genColors = { "舊世代(≤2005)": "var(--clay)", "中世代(2006-2015)": "var(--ochre)", "新世代(≥2016)": "var(--forest)" };

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">農業風險資料總覽</h1>
          <div className="page-sub">PESTICIDE × AGRI SURVEY · OVERVIEW · 115年度</div>
        </div>
        <div className="page-tools">
          <div className="seg"><button className="on">年度</button><button>季度</button><button>月度</button></div>
        </div>
      </div>

      {showKPIs && (
        <div className="kpi-row">
          <KPI label="農藥登記總筆數" value={fmt(D.meta.pesticideCount)} unit="筆" trend="↑ 2.4% vs. 114"
               spark="0,20 10,16 20,14 30,10 40,12 50,8 60,6"/>
          <KPI label="農情作物種數" value={D.meta.agriCropCount} unit="種" trend={`對應率 ${fmtPct(D.meta.matchRate, 1)}`}
               tone="info"/>
          <KPI label="有效種植面積" value={fmt(D.meta.totalArea, 0)} unit="公頃" trend="清洗後（去三重修正）"/>
          <KPI label="加權風險暴露總計" value={fmt(D.cropRisk.reduce((s,c)=>s+c.exposure,0), 0)} unit="" tone="alert"
               trend="前20作物累計"
               spark="0,22 10,20 20,14 30,10 40,6 50,4 60,2"/>
          <KPI label="極脆弱作物數" value="3" unit="/234" tone="warn" trend="登記≤10 且面積>100 ha"/>
        </div>
      )}

      <div className="grid-main">
        {/* 左：作物風險排行 */}
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">作物加權風險暴露（前 20）</div>
            <div className="panel-meta">A · 高風險機制占比 × 種植面積</div>
          </div>
          <div className="panel-body">
            <table className="data tabular">
              <thead><tr>
                <th style={{width:28}}>#</th>
                <th>作物</th>
                <th className="num" style={{width:90}}>面積 (ha)</th>
                <th className="num" style={{width:80}}>高風險%</th>
                <th style={{width:180}}>加權風險暴露</th>
                <th className="num" style={{width:70}}>登記數</th>
                <th className="num" style={{width:50}}>IRAC</th>
              </tr></thead>
              <tbody>
                {D.cropRisk.map((c, i) => (
                  <tr key={c.crop} onClick={() => onPickCrop(c.crop)}>
                    <td className="rank">{String(i+1).padStart(2,"0")}</td>
                    <td>{c.crop}</td>
                    <td className="num mono">{fmt(c.area, 0)}</td>
                    <td className="num mono">{(c.highRiskPct*100).toFixed(1)}%</td>
                    <td>
                      <div className="bar-cell">
                        <div className="bar-track">
                          <div className="bar-fill" data-risk={c.highRiskPct > 0.5 ? "high" : c.highRiskPct > 0.3 ? "mid" : "low"}
                               style={{width: (c.exposure/maxA*100) + "%"}}></div>
                        </div>
                        <span className="bar-num">{fmt(c.exposure,0)}</span>
                      </div>
                    </td>
                    <td className="num mono">{c.regCount}</td>
                    <td className="num mono">{c.iracDiv}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 右：政策發現 + 世代更替 */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--gap)" }}>
          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">五大政策關注發現</div>
              <div className="panel-meta">KEY FINDINGS</div>
            </div>
            <div>
              {D.keyFindings.map(f => (
                <div key={f.id} className="finding" data-sev={f.severity}>
                  <div className="finding-num">{String(f.id).padStart(2,"0")}</div>
                  <div>
                    <div className="finding-title">{f.title}</div>
                    <div className="finding-body">{f.body}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">IRAC 世代更替</div>
              <div className="panel-meta">GENERATION SHIFT</div>
            </div>
            <div className="panel-body">
              {Object.entries(D.generations).map(([gen, g]) => {
                const entries = Object.entries(g).filter(([k]) => k !== "total").sort((a,b)=>b[1]-a[1]).slice(0, 6);
                const total = g.total;
                return (
                  <div key={gen} style={{marginBottom: 10}}>
                    <div style={{display:"flex", justifyContent:"space-between", fontSize:11, marginBottom:4}}>
                      <span style={{fontWeight:600}}>{gen}</span>
                      <span className="mono" style={{color:"var(--ink-3)"}}>N = {fmt(total)}</span>
                    </div>
                    <div className="gen-bar">
                      {entries.map(([code, n], i) => {
                        const colors = ["var(--terra)", "var(--clay)", "var(--ochre)", "var(--olive)", "var(--forest)", "var(--sky)"];
                        return <div key={code} className="gen-seg"
                                    style={{width: (n/total*100) + "%", background: colors[i]}}
                                    title={`${code}: ${n} (${(n/total*100).toFixed(1)}%)`}></div>;
                      })}
                    </div>
                    <div style={{display:"flex", gap:8, marginTop:4, flexWrap:"wrap"}}>
                      {entries.map(([code, n], i) => (
                        <span key={code} className="chip mono" style={{fontSize:9}}>{code} {(n/total*100).toFixed(0)}%</span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// === Map Page ===
function MapPage({ selected, setSelected }) {
  const [tt, setTT] = useTooltip();
  const max = Math.max(...D.countyRisk.map(c => c.exposure));
  const county = D.countyRisk.find(c => c.county === selected);

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">縣市／鄉鎮風險地圖</h1>
          <div className="page-sub">COUNTY × TOWNSHIP RISK MAP · 分析 C + G</div>
        </div>
        <div className="page-tools">
          <div className="seg"><button className="on">加權風險</button><button>單一作物集中度</button><button>IRAC 多樣性</button></div>
        </div>
      </div>

      <div className="grid-map">
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">台灣加權風險暴露分布</div>
            <div className="panel-meta">22 COUNTIES · CLICK TO DRILL</div>
          </div>
          <div style={{padding: "var(--pad)"}}>
            <div className="map-wrap">
              <TaiwanMap selected={selected} onSelect={setSelected} setTT={setTT}/>
            </div>
            <div className="legend">
              <span>低</span>
              {[1,2,3,4,5].map(i => (
                <span key={i} className="legend-swatch" style={{background: `var(--risk-${i})`}}/>
              ))}
              <span>高</span>
              <span style={{marginLeft: "auto"}}>加權風險暴露 = 高風險機制占比 × 種植面積</span>
            </div>
          </div>
        </div>

        <div style={{display:"flex", flexDirection:"column", gap:"var(--gap)"}}>
          {county && (
            <div className="panel">
              <div className="detail-head">
                <div className="detail-crop">{county.county}</div>
                <div className="detail-sub">COUNTY · 已選擇</div>
              </div>
              <div className="detail-grid">
                <div className="detail-stat">
                  <div className="detail-stat-label">種植面積</div>
                  <div className="detail-stat-value">{fmt(county.area,0)}<span className="kpi-unit">ha</span></div>
                </div>
                <div className="detail-stat">
                  <div className="detail-stat-label">加權風險</div>
                  <div className="detail-stat-value" style={{color:"var(--terra)"}}>{fmt(county.exposure,0)}</div>
                </div>
                <div className="detail-stat" style={{gridColumn:"1/-1", borderRight:"none"}}>
                  <div className="detail-stat-label">前 3 高風險作物</div>
                  <div style={{marginTop:6, display:"flex", gap:6, flexWrap:"wrap"}}>
                    {county.topCrops.map((c,i) => (
                      <span key={i} className="chip" style={{fontSize:11, padding:"3px 8px"}}>
                        <span style={{color:"var(--ink-4)", marginRight:6}}>{i+1}</span>{c}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">鄉鎮絕對風險 TOP 15</div>
              <div className="panel-meta">G · 加權風險暴露</div>
            </div>
            <div className="panel-body" style={{padding: 0, maxHeight: 460, overflowY: "auto"}}>
              <table className="data tabular">
                <thead><tr>
                  <th style={{width:24}}>#</th>
                  <th>鄉鎮</th>
                  <th>主作物</th>
                  <th className="num" style={{width:80}}>風險</th>
                </tr></thead>
                <tbody>
                  {D.townshipRisk.map(t => (
                    <tr key={t.rank} onClick={() => setSelected(t.county)}>
                      <td className="rank">{t.rank}</td>
                      <td>
                        <div style={{fontSize:11.5}}>{t.town}</div>
                        <div className="mono" style={{fontSize:9.5, color:"var(--ink-4)"}}>{t.county}</div>
                      </td>
                      <td>
                        <div style={{fontSize:11}}>{t.topCrop}</div>
                        <div className="mono" style={{fontSize:9.5, color:"var(--ink-4)"}}>{(t.topPct*100).toFixed(0)}% 集中</div>
                      </td>
                      <td className="num mono">{fmt(t.exposure,0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className="panel" style={{marginTop: "var(--gap)"}}>
        <div className="panel-head">
          <div className="panel-title">縣市排行</div>
          <div className="panel-meta">C · ALL 22</div>
        </div>
        <div className="panel-body">
          <BarChart
            data={D.countyRisk.filter(c=>c.exposure>0).map(c => ({ label: c.county, value: c.exposure }))}
            max={max}
            colorFn={d => riskColor(d.value, max)}
          />
        </div>
      </div>
      <Tooltip tt={tt}/>
    </>
  );
}

// === Crop Matrix Page ===
function CropPage({ onPickCrop }) {
  const [query, setQuery] = useState("");
  const [moa, setMOA] = useState("IRAC");
  const iracCodes = ["1A", "1B", "3A", "4A", "4C", "6", "14", "15", "22A", "23", "28"];

  const filtered = D.cropRisk.filter(c => c.crop.includes(query));
  const maxE = D.cropRisk[0].exposure;

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">作物 × 農藥風險矩陣</h1>
          <div className="page-sub">CROP × MOA MATRIX · 分析 F</div>
        </div>
        <div className="page-tools">
          <div className="seg">
            <button className={moa==="IRAC"?"on":""} onClick={()=>setMOA("IRAC")}>IRAC（殺蟲）</button>
            <button className={moa==="FRAC"?"on":""} onClick={()=>setMOA("FRAC")}>FRAC（殺菌）</button>
          </div>
        </div>
      </div>

      <div className="filter-bar">
        <span className="filter-label">篩選</span>
        <input className="filter-input" placeholder="搜尋作物…" value={query} onChange={e=>setQuery(e.target.value)}/>
        <select className="filter-select"><option>全部類別</option><option>糧食</option><option>果樹</option><option>蔬菜</option><option>特作</option></select>
        <select className="filter-select"><option>面積 &gt; 0 ha</option><option>面積 &gt; 1,000 ha</option><option>面積 &gt; 10,000 ha</option></select>
        <span className="filter-label" style={{marginLeft:"auto"}}>顯示 {filtered.length} / 20</span>
      </div>

      <div className="panel">
        <div className="panel-head">
          <div className="panel-title">高風險機制集中度熱圖</div>
          <div className="panel-meta">深色 = 該機制筆數占比高</div>
        </div>
        <div className="matrix">
          <table>
            <thead>
              <tr>
                <th className="row-label">作物</th>
                {iracCodes.map(c => <th key={c} title={D.iracDict[c]?.name || c}>{c}</th>)}
                <th>面積</th>
                <th>高風險%</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => (
                <tr key={c.crop}>
                  <td className="row-label" onClick={()=>onPickCrop(c.crop)} style={{cursor:"pointer"}}>{c.crop}</td>
                  {iracCodes.map(code => {
                    const hit = c.moa.split(",").includes(code);
                    // 隨機但確定性的強度（基於作物與代碼名稱）
                    const idx = c.moa.split(",").indexOf(code);
                    const strength = hit ? [0.9, 0.6, 0.4, 0.28, 0.18, 0.1][Math.min(idx, 5)] : 0;
                    return (
                      <td key={code} className="cell"
                          style={{background: hit ? `color-mix(in oklab, ${riskColor(strength, 1)} ${strength*100}%, var(--bg-panel))` : "var(--bg-panel)"}}
                          title={`${c.crop} · ${code} · ${D.iracDict[code]?.name || ""}`}>
                        {hit && <span className="val mono">{(strength*100).toFixed(0)}</span>}
                      </td>
                    );
                  })}
                  <td className="cell mono" style={{width:70, fontSize:10}}>{fmt(c.area,0)}</td>
                  <td className="cell mono" style={{width:60, fontSize:10, color: c.highRiskPct>0.5 ? "var(--terra)" : "inherit"}}>
                    {(c.highRiskPct*100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="legend" style={{padding: "10px var(--pad)"}}>
          {iracCodes.slice(0,6).map(c => (
            <span key={c} style={{marginRight: 14, fontSize: 10}}>
              <span className="mono" style={{color:"var(--ink)", marginRight:4}}>{c}</span>
              <span style={{color:"var(--ink-3)"}}>{D.iracDict[c]?.name}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="grid-2" style={{marginTop: "var(--gap)"}}>
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">極脆弱作物（登記≤10 且面積&gt;100 ha）</div>
            <div className="panel-meta">B + E</div>
          </div>
          <div className="panel-body">
            {D.vulnerableCrops.map(v => (
              <div key={v.crop} style={{padding:"10px 0", borderBottom:"1px dashed var(--rule)"}}>
                <div style={{display:"flex", justifyContent:"space-between", alignItems:"baseline"}}>
                  <span style={{fontSize:14, fontWeight:600}}>{v.crop}</span>
                  <span className="mono" style={{fontSize:10, color:"var(--ink-3)"}}>{v.area ? fmt(v.area,0) + " ha" : "—"}</span>
                </div>
                <div style={{display:"flex", gap:8, marginTop:4, fontSize:11}}>
                  <span className="chip high">登記 {v.regCount}</span>
                  <span className="chip mid">IRAC 多樣性 {v.iracDiv}</span>
                </div>
                <div style={{fontSize:11, color:"var(--ink-3)", marginTop:4}}>{v.note}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">結構最脆弱鄉鎮（單一作物 &gt; 85%）</div>
            <div className="panel-meta">G · CONCENTRATION</div>
          </div>
          <div className="panel-body" style={{padding:0}}>
            <table className="data tabular">
              <thead><tr><th>#</th><th>鄉鎮</th><th>主作物</th><th className="num">占比</th><th className="num">IRAC</th></tr></thead>
              <tbody>
                {D.concentrationTownship.map(t => (
                  <tr key={t.rank}>
                    <td className="rank">{t.rank}</td>
                    <td>{t.town}<div className="mono" style={{fontSize:9.5, color:"var(--ink-4)"}}>{t.county}</div></td>
                    <td>{t.topCrop}</td>
                    <td className="num mono" style={{color:"var(--terra)"}}>{(t.topPct*100).toFixed(1)}%</td>
                    <td className="num mono">{t.iracDiv}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}

// === Pesticide Page ===
function PesticidePage() {
  const [gen, setGen] = useState("新世代(≥2016)");
  const genData = D.generations[gen];
  const genEntries = Object.entries(genData).filter(([k]) => k !== "total").sort((a,b)=>b[1]-a[1]);
  const genMax = genEntries[0][1];

  const formMax = D.formType[0].count;
  const colors = ["var(--forest)", "var(--olive)", "var(--ochre)", "var(--clay)", "var(--terra)", "var(--sky)", "var(--ink-3)", "var(--ink-4)"];

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">農藥抗藥性預警 · MOA 輪替</h1>
          <div className="page-sub">PESTICIDE RESISTANCE EARLY WARNING · 分析六～十</div>
        </div>
        <div className="page-tools">
          <button className="icon-btn" style={{width:"auto", padding:"0 10px"}}>＋ 新增預警規則</button>
        </div>
      </div>

      <div className="timeline">
        {Object.keys(D.generations).map(g => (
          <div key={g} className={"timeline-cell " + (gen === g ? "active" : "")} onClick={() => setGen(g)}>
            <div className="tl-year">GENERATION</div>
            <div className="tl-name">{g.replace(/\(.*\)/, "").trim()}</div>
            <div className="tl-count">N = {fmt(D.generations[g].total)}　{g.match(/\(.*\)/)?.[0]}</div>
          </div>
        ))}
      </div>

      <div className="grid-main">
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">{gen} · IRAC 代碼分布</div>
            <div className="panel-meta">TOP CODES · N = {fmt(genData.total)}</div>
          </div>
          <div className="panel-body">
            {genEntries.slice(0, 10).map(([code, n], i) => {
              const info = D.iracDict[code] || {};
              const pct = n / genData.total;
              return (
                <div key={code} style={{display:"grid", gridTemplateColumns:"44px 1fr 72px 54px", gap:10, alignItems:"center", padding:"7px 0", borderBottom:"1px dashed var(--rule)"}}>
                  <span className="mono" style={{fontSize:13, fontWeight:600}}>{code}</span>
                  <div>
                    <div style={{fontSize:12}}>{info.name || "—"}</div>
                    <div style={{fontSize:10, color:"var(--ink-4)"}}>{info.note}</div>
                  </div>
                  <div className="bar-track" style={{height:8}}>
                    <div className="bar-fill"
                         data-risk={info.risk === "高" ? "high" : info.risk === "中" ? "mid" : "low"}
                         style={{width: (n/genMax*100) + "%"}}></div>
                  </div>
                  <div className="mono tabular" style={{fontSize:11, textAlign:"right"}}>
                    <div>{fmt(n)}</div>
                    <div style={{color:"var(--ink-4)", fontSize:9.5}}>{(pct*100).toFixed(1)}%</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{display:"flex", flexDirection:"column", gap:"var(--gap)"}}>
          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">劑型分布 × 環境風險</div>
              <div className="panel-meta">分析十 · N = 10,147</div>
            </div>
            <div className="panel-body">
              <div className="donut-row">
                <Donut data={D.formType.slice(0, 6).map((f, i) => ({
                  label: f.code, value: f.count,
                  color: f.risk === "高風險" ? "var(--terra)" : f.risk === "環境友善" ? "var(--olive)" : "var(--ink-3)"
                }))}/>
                <div className="donut-legend">
                  {D.formType.slice(0, 8).map((f, i) => (
                    <div key={f.code} className="legend-item">
                      <span className="legend-swatch-sm" style={{
                        background: f.risk === "高風險" ? "var(--terra)" : f.risk === "環境友善" ? "var(--olive)" : "var(--ink-3)"
                      }}/>
                      <span className="legend-label"><b className="mono">{f.code}</b> · {f.name}</span>
                      <span className="legend-val">{f.pct}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">進口農藥原產國</div>
              <div className="panel-meta">分析九 · 排除「其他」</div>
            </div>
            <div className="panel-body">
              <BarChart
                data={D.origin.slice(0, 10).map(o => ({ label: o.country, value: o.count }))}
                max={D.origin[0].count}
                colorFn={() => "var(--sky)"}
                format={v => v}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="panel" style={{marginTop: "var(--gap)"}}>
        <div className="panel-head">
          <div className="panel-title">世代更替視覺化 · 同一座標軸比較三世代</div>
          <div className="panel-meta">GENERATIONAL DRIFT</div>
        </div>
        <div className="panel-body">
          {["1A", "1B", "3A", "4A", "4C", "23", "28", "14"].map(code => {
            const info = D.iracDict[code] || {};
            const bars = Object.entries(D.generations).map(([g, data]) => ({
              gen: g, pct: (data[code] || 0) / data.total
            }));
            const maxP = Math.max(...bars.map(b => b.pct));
            return (
              <div key={code} style={{display:"grid", gridTemplateColumns:"80px 1fr", gap:12, padding:"8px 0", borderBottom:"1px dashed var(--rule)", alignItems:"center"}}>
                <div>
                  <div className="mono" style={{fontSize:13, fontWeight:600}}>{code}</div>
                  <div style={{fontSize:10, color:"var(--ink-3)"}}>{info.name}</div>
                </div>
                <div style={{display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap:8}}>
                  {bars.map(b => (
                    <div key={b.gen}>
                      <div className="mono" style={{fontSize:9, color:"var(--ink-4)", marginBottom:3}}>{b.gen.match(/\((.*)\)/)?.[1]}</div>
                      <div className="bar-track" style={{height:10}}>
                        <div className="bar-fill" style={{
                          width: (b.pct / maxP * 100) + "%",
                          background: info.risk === "高" ? "var(--terra)" : info.risk === "中" ? "var(--ochre)" : "var(--olive)"
                        }}></div>
                      </div>
                      <div className="mono" style={{fontSize:10, marginTop:2, color:"var(--ink-2)"}}>{(b.pct*100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}

// === Detail Page ===
function DetailPage({ crop }) {
  const c = D.cropRisk.find(x => x.crop === crop) || D.cropRisk[0];
  const moa = c.moa.split(",");
  const relatedCounties = D.countyRisk.filter(cc => cc.topCrops.includes(c.crop)).slice(0, 6);

  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">{c.crop}</h1>
          <div className="page-sub">CROP DETAIL · CASE DEEP-DIVE</div>
        </div>
        <div className="page-tools">
          <button className="icon-btn" style={{width:"auto", padding:"0 10px"}}>⎙ 輸出報告</button>
          <button className="icon-btn" style={{width:"auto", padding:"0 10px"}}>加入關注清單</button>
        </div>
      </div>

      <div className="kpi-row" style={{gridTemplateColumns: "repeat(4, 1fr)"}}>
        <KPI label="全台種植面積" value={fmt(c.area,0)} unit="ha"/>
        <KPI label="高風險機制占比" value={(c.highRiskPct*100).toFixed(1)} unit="%" tone={c.highRiskPct>0.5?"alert":c.highRiskPct>0.3?"warn":undefined}/>
        <KPI label="有效登記農藥" value={fmt(c.regCount)} unit="種" tone="info"/>
        <KPI label="IRAC 多樣性" value={c.iracDiv} unit="代碼" tone={c.iracDiv < 6 ? "warn" : undefined}/>
      </div>

      <div className="grid-main">
        <div className="panel">
          <div className="panel-head">
            <div className="panel-title">主要 IRAC 機制</div>
            <div className="panel-meta">MOA BREAKDOWN</div>
          </div>
          <div className="panel-body">
            {moa.map((code, i) => {
              const info = D.iracDict[code] || {};
              const intensity = [0.9, 0.6, 0.4, 0.28, 0.18, 0.1][i] || 0.05;
              return (
                <div key={code} style={{display:"grid", gridTemplateColumns:"60px 1fr auto", gap:12, alignItems:"center", padding:"10px 0", borderBottom:"1px dashed var(--rule)"}}>
                  <span className="mono" style={{fontSize:14, fontWeight:600}}>{code}</span>
                  <div>
                    <div style={{fontSize:12.5}}>{info.name || "—"}</div>
                    <div style={{fontSize:10.5, color:"var(--ink-3)"}}>{info.note}</div>
                    <div className="bar-track" style={{height:6, marginTop:5}}>
                      <div className="bar-fill" style={{width:(intensity*100)+"%", background: info.risk === "高" ? "var(--terra)" : info.risk === "中" ? "var(--ochre)" : "var(--olive)"}}/>
                    </div>
                  </div>
                  <span className={"chip " + (info.risk === "高" ? "high" : info.risk === "中" ? "mid" : "low")}>
                    {info.risk || "—"} 風險
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{display:"flex", flexDirection:"column", gap:"var(--gap)"}}>
          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">風險評估摘要</div>
              <div className="panel-meta">ADVISORY</div>
            </div>
            <div className="panel-body">
              <div style={{fontSize:12, lineHeight:1.6, color:"var(--ink-2)"}}>
                <p style={{marginTop:0}}>
                  <b>{c.crop}</b> 全台種植 {fmt(c.area,0)} 公頃，高風險機制占比 <b style={{color: c.highRiskPct>0.5 ? "var(--terra)" : "inherit"}}>{(c.highRiskPct*100).toFixed(1)}%</b>，加權風險暴露值 {fmt(c.exposure, 0)}。
                </p>
                <p>
                  有效登記農藥 {fmt(c.regCount)} 種，IRAC 多樣性 {c.iracDiv} 代碼，
                  {c.iracDiv < 6 ? "輪藥策略空間有限，建議納入優先輔導。" : c.iracDiv < 10 ? "輪藥策略尚有空間。" : "輪藥選項相對充裕。"}
                </p>
                <p>
                  主要依賴機制 <span className="mono chip">{moa[0]}</span>，
                  {D.iracDict[moa[0]]?.risk === "高" ? "屬於結構性高風險，建議鼓勵農民使用低風險替代劑型。" : "風險相對可控。"}
                </p>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <div className="panel-title">主要分布縣市</div>
              <div className="panel-meta">GEO DISTRIBUTION</div>
            </div>
            <div className="panel-body" style={{padding:0}}>
              <table className="data tabular">
                <thead><tr><th>縣市</th><th className="num">面積</th><th className="num">風險暴露</th></tr></thead>
                <tbody>
                  {relatedCounties.length > 0 ? relatedCounties.map(cc => (
                    <tr key={cc.county}>
                      <td>{cc.county} <span className="mono" style={{fontSize:9.5, color:"var(--ink-4)"}}>TOP#{cc.topCrops.indexOf(c.crop)+1}</span></td>
                      <td className="num mono">{fmt(cc.area,0)}</td>
                      <td className="num mono" style={{color:"var(--terra)"}}>{fmt(cc.exposure,0)}</td>
                    </tr>
                  )) : <tr><td colSpan={3} style={{color:"var(--ink-4)", textAlign:"center", padding:16}}>無縣市級前 3 分布</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

Object.assign(window, { OverviewPage, MapPage, CropPage, PesticidePage, DetailPage });
