// ============================================================
// 農業資料視覺化 — 核心資料集
// 來源：pesticide_full.csv (11,784筆) × agri_clean.csv (113年農情調查)
// ============================================================

window.DATA = {
  meta: {
    reportDate: "2026-04-13",
    pesticideCount: 11784,
    agriCropCount: 234,
    matchedCount: 149,
    matchRate: 0.637,
    totalArea: 621492.6,
  },

  // 分析A：加權風險暴露前作物（高風險機制占比 × 種植面積）
  cropRisk: [
    { crop: "稉稻", area: 146496.76, highRiskPct: 0.636, exposure: 93171.94, regCount: 7276, iracDiv: 14, moa: "1A,1B,14,3A,4A" },
    { crop: "硬質玉米", area: 24396.01, highRiskPct: 0.5765, exposure: 14064.30, regCount: 685, iracDiv: 9, moa: "1B,3A,4A,6,28" },
    { crop: "食用玉米", area: 14514.03, highRiskPct: 0.5765, exposure: 8367.34, regCount: 685, iracDiv: 9, moa: "1B,3A,4A,6,28" },
    { crop: "鳳梨", area: 10745.18, highRiskPct: 0.6618, exposure: 7111.16, regCount: 709, iracDiv: 6, moa: "1B,3A,4A" },
    { crop: "落花生", area: 17190.36, highRiskPct: 0.3496, exposure: 6009.75, regCount: 1534, iracDiv: 11, moa: "1B,3A,6,4A" },
    { crop: "香蕉", area: 14802.92, highRiskPct: 0.3487, exposure: 5161.78, regCount: 2738, iracDiv: 11, moa: "1B,3A,28,6" },
    { crop: "荔枝", area: 9533.50, highRiskPct: 0.3683, exposure: 3511.19, regCount: 1929, iracDiv: 9, moa: "1B,3A,4A,6" },
    { crop: "龍眼", area: 10296.13, highRiskPct: 0.3165, exposure: 3258.73, regCount: 1391, iracDiv: 7, moa: "1B,3A,4A" },
    { crop: "茶", area: 12078.24, highRiskPct: 0.2372, exposure: 2864.96, regCount: 4245, iracDiv: 20, moa: "3A,4A,6,28,1B" },
    { crop: "竹筍", area: 25943.98, highRiskPct: 0.1006, exposure: 2609.96, regCount: 652, iracDiv: 9, moa: "1B,3A,6" },
    { crop: "甘藍", area: 8105.86, highRiskPct: 0.2643, exposure: 2142.38, regCount: 877, iracDiv: 8, moa: "1B,3A,6,28" },
    { crop: "大豆", area: 4473.96, highRiskPct: 0.4513, exposure: 2019.10, regCount: 2996, iracDiv: 17, moa: "1B,3A,4A,6,28" },
    { crop: "番荔枝(鳳梨釋迦)", area: 2618.09, highRiskPct: 0.6618, exposure: 1732.65, regCount: 709, iracDiv: 6, moa: "1B,3A,4A" },
    { crop: "番石榴", area: 8028.65, highRiskPct: 0.2153, exposure: 1728.57, regCount: 2232, iracDiv: 14, moa: "1B,3A,4A,6" },
    { crop: "甘藷", area: 9403.90, highRiskPct: 0.1834, exposure: 1724.68, regCount: 3060, iracDiv: 10, moa: "1B,3A,4A" },
    { crop: "蜀黍(高粱)", area: 4414.95, highRiskPct: 0.3722, exposure: 1643.24, regCount: 493, iracDiv: 9, moa: "1B,3A,4A,6" },
    { crop: "西瓜", area: 6777.95, highRiskPct: 0.2414, exposure: 1636.20, regCount: 297, iracDiv: 9, moa: "1B,3A,6" },
    { crop: "紅豆", area: 5258.41, highRiskPct: 0.2743, exposure: 1442.38, regCount: 778, iracDiv: 6, moa: "1B,3A,6" },
    { crop: "洋菇", area: 785.53, highRiskPct: 0.9891, exposure: 776.97, regCount: 328, iracDiv: 2, moa: "1B,3A" },
    { crop: "蔥", area: 4149.64, highRiskPct: 0.1825, exposure: 757.31, regCount: 979, iracDiv: 13, moa: "1B,3A,4A,6" },
  ],

  // 分析C：縣市風險排名（加權風險暴露）
  countyRisk: [
    { county: "雲林縣", area: 106207.82, exposure: 30578.34, topCrops: ["稉稻", "落花生", "食用玉米"] },
    { county: "台南市", area: 71863.11, exposure: 20287.06, topCrops: ["稉稻", "硬質玉米", "龍眼"] },
    { county: "嘉義縣", area: 70433.67, exposure: 20087.14, topCrops: ["稉稻", "硬質玉米", "鳳梨"] },
    { county: "彰化縣", area: 57440.44, exposure: 19171.76, topCrops: ["稉稻", "落花生", "荔枝"] },
    { county: "台中市", area: 42163.95, exposure: 11637.92, topCrops: ["稉稻", "龍眼", "荔枝"] },
    { county: "屏東縣", area: 58646.72, exposure: 10780.95, topCrops: ["稉稻", "鳳梨", "香蕉"] },
    { county: "高雄市", area: 37257.54, exposure: 9074.10, topCrops: ["稉稻", "荔枝", "鳳梨"] },
    { county: "桃園市", area: 23316.98, exposure: 8287.32, topCrops: ["稉稻", "蜀黍(高粱)", "大豆"] },
    { county: "花蓮縣", area: 24867.29, exposure: 7688.14, topCrops: ["稉稻", "硬質玉米", "西瓜"] },
    { county: "宜蘭縣", area: 17070.48, exposure: 7554.92, topCrops: ["稉稻", "甘藍", "西瓜"] },
    { county: "南投縣", area: 44999.31, exposure: 7297.44, topCrops: ["茶", "稉稻", "香蕉"] },
    { county: "台東縣", area: 21098.07, exposure: 7281.44, topCrops: ["稉稻", "番荔枝(鳳梨釋迦)", "番荔枝(大目種)"] },
    { county: "苗栗縣", area: 19930.86, exposure: 5262.43, topCrops: ["稉稻", "竹筍", "食用玉米"] },
    { county: "新竹縣", area: 10594.56, exposure: 3495.14, topCrops: ["稉稻", "茶", "食用玉米"] },
    { county: "金門縣", area: 2986.59, exposure: 1084.68, topCrops: ["蜀黍(高粱)", "小麥", "落花生"] },
    { county: "新北市", area: 7857.65, exposure: 814.13, topCrops: ["竹筍", "茶", "稉稻"] },
    { county: "嘉義市", area: 1293.55, exposure: 509.50, topCrops: ["稉稻", "鳳梨", "荔枝"] },
    { county: "新竹市", area: 839.69, exposure: 419.81, topCrops: ["稉稻", "荔枝", "食用玉米"] },
    { county: "台北市", area: 1452.56, exposure: 244.10, topCrops: ["稉稻", "竹筍", "茶"] },
    { county: "澎湖縣", area: 967.06, exposure: 100.22, topCrops: ["落花生", "食用玉米", "甘藷"] },
    { county: "基隆市", area: 204.71, exposure: 18.52, topCrops: ["竹筍", "香蕉", "山藥"] },
    { county: "連江縣", area: 0, exposure: 0, topCrops: [] },
  ],

  // 分析G：鄉鎮風險前 15
  townshipRisk: [
    { rank: 1, county: "雲林縣", town: "水林鄉", area: 9278.34, cropCount: 81, topCrop: "稉稻", topPct: 0.3178, exposure: 3484.83, iracDiv: 11.68 },
    { rank: 2, county: "雲林縣", town: "元長鄉", area: 9661.16, cropCount: 84, topCrop: "落花生", topPct: 0.2681, exposure: 3443.38, iracDiv: 11.69 },
    { rank: 3, county: "彰化縣", town: "二林鎮", area: 6967.57, cropCount: 111, topCrop: "稉稻", topPct: 0.4178, exposure: 2590.58, iracDiv: 11.88 },
    { rank: 4, county: "桃園市", town: "新屋區", area: 5387.58, cropCount: 80, topCrop: "稉稻", topPct: 0.6743, exposure: 2415.06, iracDiv: 12.47 },
    { rank: 5, county: "台南市", town: "後壁區", area: 5006.37, cropCount: 79, topCrop: "稉稻", topPct: 0.6213, exposure: 2351.97, iracDiv: 12.67 },
    { rank: 6, county: "雲林縣", town: "土庫鎮", area: 6075.94, cropCount: 86, topCrop: "落花生", topPct: 0.2686, exposure: 2275.48, iracDiv: 10.98 },
    { rank: 7, county: "雲林縣", town: "虎尾鎮", area: 5969.30, cropCount: 100, topCrop: "稉稻", topPct: 0.2426, exposure: 2196.73, iracDiv: 11.47 },
    { rank: 8, county: "嘉義縣", town: "民雄鄉", area: 4248.67, cropCount: 86, topCrop: "稉稻", topPct: 0.5551, exposure: 2132.15, iracDiv: 11.66 },
    { rank: 9, county: "嘉義縣", town: "新港鄉", area: 5238.61, cropCount: 106, topCrop: "稉稻", topPct: 0.5162, exposure: 2043.09, iracDiv: 12.65 },
    { rank: 10, county: "花蓮縣", town: "玉里鎮", area: 4685.53, cropCount: 75, topCrop: "稉稻", topPct: 0.6261, exposure: 1994.88, iracDiv: 12.68 },
    { rank: 11, county: "嘉義縣", town: "義竹鄉", area: 5993.78, cropCount: 77, topCrop: "硬質玉米", topPct: 0.4433, exposure: 1986.72, iracDiv: 9.31 },
    { rank: 12, county: "雲林縣", town: "崙背鄉", area: 6769.67, cropCount: 82, topCrop: "稉稻", topPct: 0.2704, exposure: 1935.73, iracDiv: 10.31 },
    { rank: 13, county: "台南市", town: "鹽水區", area: 4194.11, cropCount: 65, topCrop: "硬質玉米", topPct: 0.6532, exposure: 1878.39, iracDiv: 9.68 },
    { rank: 14, county: "彰化縣", town: "芳苑鄉", area: 6571.93, cropCount: 82, topCrop: "落花生", topPct: 0.2501, exposure: 1790.70, iracDiv: 10.76 },
    { rank: 15, county: "雲林縣", town: "大埤鄉", area: 3509.38, cropCount: 71, topCrop: "稉稻", topPct: 0.6520, exposure: 1597.67, iracDiv: 12.64 },
  ],

  // 分析G-concentration：結構最脆弱鄉鎮（單一作物占比最高）
  concentrationTownship: [
    { rank: 1, county: "台中市", town: "梧棲區", area: 376.69, topCrop: "稉稻", topPct: 0.9659, iracDiv: 13.89 },
    { rank: 2, county: "新竹市", town: "北區", area: 205.40, topCrop: "稉稻", topPct: 0.9635, iracDiv: 13.90 },
    { rank: 3, county: "屏東縣", town: "枋山鄉", area: 677.70, topCrop: "改良種芒果", topPct: 0.9473, iracDiv: 7.44 },
    { rank: 4, county: "彰化縣", town: "線西鄉", area: 639.11, topCrop: "稉稻", topPct: 0.9449, iracDiv: 13.87 },
    { rank: 5, county: "新北市", town: "烏來區", area: 105.96, topCrop: "竹筍", topPct: 0.9069, iracDiv: 9.02 },
    { rank: 6, county: "台中市", town: "龍井區", area: 1020.70, topCrop: "稉稻", topPct: 0.8856, iracDiv: 13.63 },
    { rank: 7, county: "新北市", town: "坪林區", area: 551.69, topCrop: "茶", topPct: 0.8854, iracDiv: 18.68 },
    { rank: 8, county: "苗栗縣", town: "獅潭鄉", area: 2129.86, topCrop: "竹筍", topPct: 0.8591, iracDiv: 9.22 },
    { rank: 9, county: "宜蘭縣", town: "壯圍鄉", area: 2206.31, topCrop: "稉稻", topPct: 0.8573, iracDiv: 13.54 },
    { rank: 10, county: "嘉義縣", town: "大埔鄉", area: 1479.96, topCrop: "竹筍", topPct: 0.8519, iracDiv: 8.90 },
  ],

  // 分析六：世代更替（IRAC 代碼在各世代分布）
  generations: {
    "舊世代(≤2005)": { total: 1701, "1B": 953, "1A": 269, "3A": 228, "14": 27, "4A": 7, "12B": 42, "12C": 23, "4C": 14 },
    "中世代(2006-2015)": { total: 872, "1B": 368, "1A": 229, "3A": 61, "14": 20, "4A": 50, "2B": 17, "4C": 30, "23": 1 },
    "新世代(≥2016)": { total: 2678, "1B": 469, "1A": 246, "3A": 551, "4A": 36, "14": 46, "4C": 288, "23": 79, "13": 58, "22A": 41, "28": 49, "15": 68, "12A": 46 },
  },

  // 分析十：劑型分布
  formType: [
    { code: "EC", name: "乳劑", count: 3067, pct: 30.1, risk: "高風險" },
    { code: "WP", name: "可濕性粉劑", count: 2426, pct: 23.8, risk: "高風險" },
    { code: "SC", name: "水懸劑", count: 1610, pct: 15.8, risk: "環境友善" },
    { code: "SL", name: "可溶液劑", count: 1041, pct: 10.2, risk: "其他" },
    { code: "GR", name: "粒劑", count: 557, pct: 5.5, risk: "其他" },
    { code: "WG", name: "水分散粒劑", count: 301, pct: 3.0, risk: "環境友善" },
    { code: "SP", name: "可溶粉劑", count: 299, pct: 2.9, risk: "其他" },
    { code: "DP", name: "粉劑", count: 233, pct: 2.3, risk: "高風險" },
    { code: "EW", name: "水乳劑", count: 166, pct: 1.6, risk: "環境友善" },
    { code: "SG", name: "可溶粒劑", count: 118, pct: 1.2, risk: "其他" },
  ],

  // 分析九：進口農藥原產國
  origin: [
    { country: "德國", count: 196, pct: 5.5 },
    { country: "瑞士", count: 124, pct: 3.5 },
    { country: "日本", count: 79, pct: 2.2 },
    { country: "美國", count: 69, pct: 1.9 },
    { country: "台灣", count: 62, pct: 1.7 },
    { country: "韓國", count: 51, pct: 1.4 },
    { country: "義大利", count: 47, pct: 1.3 },
    { country: "以色列", count: 36, pct: 1.0 },
    { country: "法國", count: 28, pct: 0.8 },
    { country: "西班牙", count: 25, pct: 0.7 },
  ],

  // IRAC 機制代碼字典
  iracDict: {
    "1A": { name: "胺基甲酸鹽類", risk: "高", note: "老化學、抗藥性案例多" },
    "1B": { name: "有機磷類", risk: "高", note: "結構性依賴，預警訊號" },
    "2A": { name: "環二烯有機氯", risk: "高", note: "多數國家已禁用" },
    "2B": { name: "苯基吡唑類 (Fipronil)", risk: "中", note: "" },
    "3A": { name: "合成除蟲菊酯類", risk: "中", note: "各世代穩定" },
    "4A": { name: "新菸鹼類", risk: "中", note: "新世代明顯成長" },
    "4C": { name: "Sulfoximines", risk: "低", note: "新世代新進" },
    "5": { name: "多殺菌素類 (Spinosyn)", risk: "低", note: "" },
    "6": { name: "阿巴汀類 (Avermectin)", risk: "中", note: "" },
    "14": { name: "Nereistoxin 類似物", risk: "中", note: "" },
    "15": { name: "幾丁質合成抑制劑", risk: "低", note: "" },
    "22A": { name: "Oxadiazine", risk: "低", note: "新世代" },
    "23": { name: "四環結構衍生物", risk: "低", note: "新世代明顯" },
    "28": { name: "雙醯胺類", risk: "低", note: "環境友善" },
  },

  // 低替代性、高暴露作物（分析B）
  vulnerableCrops: [
    { crop: "其他柑桔", regCount: 11, iracDiv: 0, area: null, note: "有效登記 ≤ 20 且面積 > 500 ha" },
    { crop: "愛玉子", regCount: 4, iracDiv: 1, area: 565.77, note: "新興作物，登記嚴重不足" },
    { crop: "草菇", regCount: 2, iracDiv: 0, area: 226.20, note: "新興作物，登記嚴重不足" },
  ],

  // 政策關注五大發現
  keyFindings: [
    {
      id: 1,
      title: "IRAC 1B（有機磷）仍主導全市場",
      body: "跨世代、跨作物、跨劑型結構性依賴。已有多起田間抗藥性案例，是最迫切的預警訊號。",
      severity: "high",
    },
    {
      id: 2,
      title: "極低充裕度作物存在防治斷鍊風險",
      body: "僅 ≤5 種農藥可選的作物一旦爆發抗藥性，幾乎無輪藥空間。此類作物往往 IRAC 多樣性也極低。",
      severity: "high",
    },
    {
      id: 3,
      title: "洋菇為最高加權風險單一作物",
      body: "FRAC 1 (DMI 類) 集中度 98.9%，幾乎無替代選項。",
      severity: "high",
    },
    {
      id: 4,
      title: "16+ 鄉鎮最大作物占比 > 80%",
      body: "結構性單一化使病蟲害爆發時缺乏緩衝，需納入農業結構調整輔導範圍。",
      severity: "mid",
    },
    {
      id: 5,
      title: "85 種農情作物未能對應登記資料",
      body: "多為「其他葉菜」「其他雜糧」類別名，反映作物分類粒度根本性落差。",
      severity: "mid",
    },
  ],
};

// 縣市地理位置（SVG viewBox 400×560 內的近似中心點 — 仿真台灣外形）
window.COUNTY_GEO = {
  "基隆市":   { cx: 265, cy: 48,  size: 10 },
  "台北市":   { cx: 248, cy: 68,  size: 14 },
  "新北市":   { cx: 240, cy: 80,  size: 22 },
  "桃園市":   { cx: 210, cy: 92,  size: 20 },
  "新竹市":   { cx: 188, cy: 112, size: 10 },
  "新竹縣":   { cx: 200, cy: 118, size: 18 },
  "苗栗縣":   { cx: 188, cy: 146, size: 20 },
  "台中市":   { cx: 178, cy: 182, size: 24 },
  "彰化縣":   { cx: 150, cy: 212, size: 18 },
  "南投縣":   { cx: 200, cy: 232, size: 22 },
  "雲林縣":   { cx: 145, cy: 248, size: 20 },
  "嘉義市":   { cx: 144, cy: 276, size: 10 },
  "嘉義縣":   { cx: 160, cy: 282, size: 20 },
  "台南市":   { cx: 135, cy: 318, size: 22 },
  "高雄市":   { cx: 160, cy: 360, size: 24 },
  "屏東縣":   { cx: 180, cy: 406, size: 22 },
  "宜蘭縣":   { cx: 270, cy: 108, size: 18 },
  "花蓮縣":   { cx: 260, cy: 218, size: 24 },
  "台東縣":   { cx: 240, cy: 336, size: 22 },
  "澎湖縣":   { cx: 60,  cy: 310, size: 12 },
  "金門縣":   { cx: 40,  cy: 180, size: 12 },
  "連江縣":   { cx: 50,  cy: 80,  size: 10 },
};
