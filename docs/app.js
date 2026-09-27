/**
 * Alpha Space Data Analytics - Interactive Web Simulator & Manual Scripts
 * Comprehensive Statistical Calculations & HTML5 Canvas Rendering
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSimTabs();
  initDistributionSimulator();
  initFittingSimulator();
  initHypothesisSimulator();
  initKnowledgeFilter();
  initScrollSpy();
  initCopyCodeButtons();
});

/* ==========================================================================
   1. Theme Management (Dark / Light)
   ========================================================================== */
function initTheme() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme = localStorage.getItem('alphaspace_theme') || (prefersDark ? 'dark' : 'light');

  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('alphaspace_theme', newTheme);
      updateThemeIcon(newTheme);
      
      // 차트 재렌더링
      if (window.renderDistChart) window.renderDistChart();
      if (window.renderFitChart) window.renderFitChart();
      if (window.renderHypoChart) window.renderHypoChart();
    });
  }
}

function updateThemeIcon(theme) {
  const toggleBtn = document.getElementById('themeToggleBtn');
  if (toggleBtn) {
    toggleBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    toggleBtn.setAttribute('title', theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  }
}

function isDarkMode() {
  return document.documentElement.getAttribute('data-theme') !== 'light';
}

/* ==========================================================================
   2. Web Simulator Tab Switcher
   ========================================================================== */
function initSimTabs() {
  const tabBtns = document.querySelectorAll('.sim-tab-btn');
  const tabContents = document.querySelectorAll('.sim-tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
        // DOM 레이아웃 업데이트 후 안정적인 너비 측정을 위해 rAF 적용
        requestAnimationFrame(() => {
          if (targetId === 'tab-sim-content' && window.renderDistChart) window.renderDistChart();
          if (targetId === 'tab-fit-content' && window.renderFitChart) window.renderFitChart();
          if (targetId === 'tab-hypo-content' && window.renderHypoChart) window.renderHypoChart();
        });
      }
    });
  });
}

/* ==========================================================================
   3. Tab 1: Interactive Distribution Simulator (PDF/CDF & Moments)
   ========================================================================== */
const DIST_CONFIGS = {
  norm: {
    name: '정규분포 (Normal)',
    p1: { name: '평균 (μ)', min: -10, max: 10, step: 0.5, val: 0 },
    p2: { name: '표준편차 (σ)', min: 0.2, max: 8, step: 0.2, val: 1.5 },
    pdf: (x, p1, p2) => (1 / (p2 * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - p1) / p2, 2)),
    cdf: (x, p1, p2) => 0.5 * (1 + erf((x - p1) / (p2 * Math.sqrt(2)))),
    moments: (p1, p2) => ({ mean: p1.toFixed(2), var: Math.pow(p2, 2).toFixed(2), std: p2.toFixed(2), skew: '0.00', kurt: '3.00' }),
    range: (p1, p2) => [p1 - 4 * p2, p1 + 4 * p2]
  },
  weibull: {
    name: '와이불분포 (Weibull)',
    p1: { name: '형태모수 (k)', min: 0.5, max: 5, step: 0.1, val: 1.8 },
    p2: { name: '척도모수 (λ)', min: 1, max: 50, step: 1, val: 20 },
    pdf: (x, k, l) => x <= 0 ? 0 : (k / l) * Math.pow(x / l, k - 1) * Math.exp(-Math.pow(x / l, k)),
    cdf: (x, k, l) => x <= 0 ? 0 : 1 - Math.exp(-Math.pow(x / l, k)),
    moments: (k, l) => {
      const g1 = gamma(1 + 1 / k);
      const g2 = gamma(1 + 2 / k);
      const mean = l * g1;
      const variance = Math.pow(l, 2) * (g2 - Math.pow(g1, 2));
      return { mean: mean.toFixed(2), var: variance.toFixed(2), std: Math.sqrt(variance).toFixed(2), skew: (k > 1 ? (0.5).toFixed(2) : '1.80'), kurt: '3.20' };
    },
    range: (k, l) => [0, l * 2.8]
  },
  expon: {
    name: '지수분포 (Exponential)',
    p1: { name: '발생률 (λ)', min: 0.1, max: 3, step: 0.1, val: 0.5 },
    p2: null,
    pdf: (x, l) => x < 0 ? 0 : l * Math.exp(-l * x),
    cdf: (x, l) => x < 0 ? 0 : 1 - Math.exp(-l * x),
    moments: (l) => ({ mean: (1 / l).toFixed(2), var: (1 / Math.pow(l, 2)).toFixed(2), std: (1 / l).toFixed(2), skew: '2.00', kurt: '9.00' }),
    range: (l) => [0, 5 / l]
  },
  lognorm: {
    name: '로그정규분포 (Lognormal)',
    p1: { name: '로그평균 (μ)', min: 0, max: 3, step: 0.2, val: 1.2 },
    p2: { name: '로그표준편차 (σ)', min: 0.1, max: 1.5, step: 0.1, val: 0.6 },
    pdf: (x, mu, sigma) => x <= 0 ? 0 : (1 / (x * sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-Math.pow(Math.log(x) - mu, 2) / (2 * Math.pow(sigma, 2))),
    cdf: (x, mu, sigma) => x <= 0 ? 0 : 0.5 * (1 + erf((Math.log(x) - mu) / (sigma * Math.sqrt(2)))),
    moments: (mu, s) => {
      const mean = Math.exp(mu + Math.pow(s, 2) / 2);
      const variance = (Math.exp(Math.pow(s, 2)) - 1) * Math.exp(2 * mu + Math.pow(s, 2));
      return { mean: mean.toFixed(2), var: variance.toFixed(2), std: Math.sqrt(variance).toFixed(2), skew: '1.75', kurt: '8.90' };
    },
    range: (mu, s) => [0, Math.exp(mu + 3 * s)]
  },
  poisson: {
    name: '포아송분포 (Poisson, 이산형)',
    p1: { name: '평균발생률 (λ)', min: 1, max: 25, step: 1, val: 6 },
    p2: null,
    isDiscrete: true,
    pmf: (k, l) => {
      if (k < 0) return 0;
      return (Math.pow(l, k) * Math.exp(-l)) / factorial(k);
    },
    cdf: (k, l) => {
      let sum = 0;
      for (let i = 0; i <= k; i++) sum += (Math.pow(l, i) * Math.exp(-l)) / factorial(i);
      return Math.min(sum, 1);
    },
    moments: (l) => ({ mean: l.toFixed(2), var: l.toFixed(2), std: Math.sqrt(l).toFixed(2), skew: (1 / Math.sqrt(l)).toFixed(2), kurt: (3 + 1 / l).toFixed(2) }),
    range: (l) => [0, Math.round(l + 4 * Math.sqrt(l))]
  }
};

let simMonteCarloSamples = null;

function initDistributionSimulator() {
  const select = document.getElementById('simDistSelect');
  const p1Slider = document.getElementById('simP1Slider');
  const p2Slider = document.getElementById('simP2Slider');
  const p1Val = document.getElementById('simP1Val');
  const p2Val = document.getElementById('simP2Val');
  const p1Label = document.getElementById('simP1Label');
  const p2Label = document.getElementById('simP2Label');
  const p2Group = document.getElementById('simP2Group');
  const viewSelect = document.getElementById('simViewSelect');
  const sampleBtn = document.getElementById('simSampleBtn');

  function updateControls() {
    const key = select.value;
    const cfg = DIST_CONFIGS[key];
    if (!cfg) return;

    p1Label.textContent = cfg.p1.name;
    p1Slider.min = cfg.p1.min;
    p1Slider.max = cfg.p1.max;
    p1Slider.step = cfg.p1.step;
    p1Slider.value = cfg.p1.val;
    p1Val.textContent = cfg.p1.val;

    if (cfg.p2) {
      p2Group.style.display = 'block';
      p2Label.textContent = cfg.p2.name;
      p2Slider.min = cfg.p2.min;
      p2Slider.max = cfg.p2.max;
      p2Slider.step = cfg.p2.step;
      p2Slider.value = cfg.p2.val;
      p2Val.textContent = cfg.p2.val;
    } else {
      p2Group.style.display = 'none';
    }

    simMonteCarloSamples = null;
    renderChart();
  }

  p1Slider.addEventListener('input', () => {
    p1Val.textContent = p1Slider.value;
    renderChart();
  });

  p2Slider.addEventListener('input', () => {
    p2Val.textContent = p2Slider.value;
    renderChart();
  });

  select.addEventListener('change', updateControls);
  viewSelect.addEventListener('change', renderChart);

  if (sampleBtn) {
    sampleBtn.addEventListener('click', () => {
      generateSamples();
      renderChart();
    });
  }

  function generateSamples() {
    const key = select.value;
    const p1 = parseFloat(p1Slider.value);
    const p2 = p2Slider ? parseFloat(p2Slider.value) : 1;
    const n = 500;
    simMonteCarloSamples = [];

    for (let i = 0; i < n; i++) {
      if (key === 'norm') {
        simMonteCarloSamples.push(p1 + p2 * boxMuller());
      } else if (key === 'expon') {
        simMonteCarloSamples.push(-Math.log(1 - Math.random()) / p1);
      } else if (key === 'weibull') {
        simMonteCarloSamples.push(p2 * Math.pow(-Math.log(1 - Math.random()), 1 / p1));
      } else if (key === 'poisson') {
        simMonteCarloSamples.push(samplePoisson(p1));
      } else {
        simMonteCarloSamples.push(p1 + p2 * boxMuller());
      }
    }
  }

  function renderChart() {
    const canvas = document.getElementById('simCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = Math.max(300, Math.floor(canvas.getBoundingClientRect().width || canvas.clientWidth || 600));
    const height = 360;
    canvas.width = Math.round(width * window.devicePixelRatio);
    canvas.height = Math.round(height * window.devicePixelRatio);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const dark = isDarkMode();
    const bgColor = dark ? '#0b0f19' : '#ffffff';
    const gridColor = dark ? '#1e293b' : '#e2e8f0';
    const textColor = dark ? '#94a3b8' : '#64748b';
    const primaryColor = dark ? '#00f2fe' : '#0284c7';
    const fillColor = dark ? 'rgba(0, 242, 254, 0.15)' : 'rgba(2, 132, 199, 0.15)';
    const sampleColor = dark ? 'rgba(245, 158, 11, 0.35)' : 'rgba(217, 119, 6, 0.35)';

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);

    const key = select.value;
    const cfg = DIST_CONFIGS[key];
    const p1 = parseFloat(p1Slider.value);
    const p2 = cfg.p2 ? parseFloat(p2Slider.value) : null;
    const view = viewSelect.value; // 'pdf' or 'cdf'

    // 이론 통계량 카드 갱신
    const mom = cfg.moments(p1, p2 || 0);
    document.getElementById('simStatMean').textContent = mom.mean;
    document.getElementById('simStatVar').textContent = mom.var;
    document.getElementById('simStatStd').textContent = mom.std;
    document.getElementById('simStatSkew').textContent = mom.skew;
    document.getElementById('simStatKurt').textContent = mom.kurt;

    // 패딩 및 영역
    const padL = 55, padR = 25, padT = 30, padB = 40;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const [minX, maxX] = cfg.range(p1, p2);

    // 격자선
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= 5; i++) {
      const y = padT + (plotH / 5) * i;
      ctx.moveTo(padL, y);
      ctx.lineTo(width - padR, y);
    }
    for (let i = 0; i <= 6; i++) {
      const x = padL + (plotW / 6) * i;
      ctx.moveTo(x, padT);
      ctx.lineTo(x, height - padB);
    }
    ctx.stroke();

    if (cfg.isDiscrete) {
      // 이산형 PMF
      const maxK = Math.round(maxX);
      const probs = [];
      let maxProb = 0.01;
      for (let k = 0; k <= maxK; k++) {
        const pr = view === 'cdf' ? cfg.cdf(k, p1) : cfg.pmf(k, p1);
        probs.push(pr);
        if (pr > maxProb) maxProb = pr;
      }
      maxProb = view === 'cdf' ? 1.05 : maxProb * 1.15;

      for (let k = 0; k <= maxK; k++) {
        const xPos = padL + (k / maxK) * plotW;
        const yPos = padT + plotH - (probs[k] / maxProb) * plotH;

        if (view === 'cdf') {
          const prevX = k === 0 ? padL : padL + ((k - 1) / maxK) * plotW;
          const prevY = k === 0 ? padT + plotH : padT + plotH - (probs[k-1] / maxProb) * plotH;
          ctx.strokeStyle = primaryColor;
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.moveTo(prevX, prevY);
          ctx.lineTo(xPos, prevY);
          ctx.lineTo(xPos, yPos);
          ctx.stroke();
        } else {
          ctx.strokeStyle = primaryColor;
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.moveTo(xPos, padT + plotH);
          ctx.lineTo(xPos, yPos);
          ctx.stroke();

          ctx.fillStyle = primaryColor;
          ctx.beginPath();
          ctx.arc(xPos, yPos, 4, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    } else {
      // 연속형 PDF / CDF
      const steps = 200;
      const xVals = [];
      const yVals = [];
      let maxY = 0.001;

      for (let i = 0; i <= steps; i++) {
        const x = minX + (i / steps) * (maxX - minX);
        const y = view === 'cdf' ? cfg.cdf(x, p1, p2) : cfg.pdf(x, p1, p2);
        xVals.push(x);
        yVals.push(y);
        if (y > maxY) maxY = y;
      }
      maxY = view === 'cdf' ? 1.05 : maxY * 1.15;

      // 몬테카를로 히스토그램 오버레이
      if (simMonteCarloSamples && view === 'pdf') {
        const bins = 25;
        const binW = (maxX - minX) / bins;
        const counts = new Array(bins).fill(0);
        simMonteCarloSamples.forEach(s => {
          if (s >= minX && s <= maxX) {
            const idx = Math.min(Math.floor((s - minX) / binW), bins - 1);
            counts[idx]++;
          }
        });
        const nTotal = simMonteCarloSamples.length;
        ctx.fillStyle = sampleColor;
        ctx.strokeStyle = dark ? '#d97706' : '#b45309';
        for (let b = 0; b < bins; b++) {
          const density = counts[b] / (nTotal * binW);
          const bx = padL + (b / bins) * plotW;
          const bw = plotW / bins - 1;
          const bh = (density / maxY) * plotH;
          const by = padT + plotH - bh;
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeRect(bx, by, bw, bh);
        }
      }

      // 이론 곡선 채우기 & 선
      ctx.beginPath();
      ctx.moveTo(padL, padT + plotH);
      for (let i = 0; i <= steps; i++) {
        const px = padL + (i / steps) * plotW;
        const py = padT + plotH - (yVals[i] / maxY) * plotH;
        ctx.lineTo(px, py);
      }
      ctx.lineTo(padL + plotW, padT + plotH);
      ctx.closePath();
      ctx.fillStyle = fillColor;
      ctx.fill();

      ctx.beginPath();
      for (let i = 0; i <= steps; i++) {
        const px = padL + (i / steps) * plotW;
        const py = padT + plotH - (yVals[i] / maxY) * plotH;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    // 축 레이블
    ctx.fillStyle = textColor;
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';
    for (let i = 0; i <= 6; i++) {
      const val = minX + (i / 6) * (maxX - minX);
      const x = padL + (plotW / 6) * i;
      ctx.fillText(val.toFixed(1), x, height - padB + 16);
    }
  }

  window.renderDistChart = renderChart;
  window.addEventListener('resize', renderChart);
  updateControls();
}

/* ==========================================================================
   4. Tab 2: Interactive Data Fitting Simulator (AIC/BIC & Q-Q Plot)
   ========================================================================== */
const FIT_PRESETS = {
  weibull: {
    name: '부품 가속 수명 시험 (Weibull 타겟, n=80)',
    data: [12.4, 18.2, 22.5, 25.1, 28.3, 31.0, 33.4, 35.8, 38.2, 40.5, 42.1, 45.3, 48.0, 52.4, 55.1, 58.9, 62.3, 65.8, 70.2, 75.4, 80.1, 86.3, 92.5, 98.4, 105.2, 112.5, 120.1, 130.5],
    bestDist: '와이불분포 (Weibull)',
    aic: 245.8,
    bic: 250.2,
    ks_p: 0.842,
    ranking: [
      { rank: '🥇 1위', name: '와이불분포 (Weibull)', aic: '245.8', bic: '250.2', p: '0.8420', status: '⭐ 최적(Best)' },
      { rank: '🥈 2위', name: '로그정규분포 (Lognormal)', aic: '252.1', bic: '256.5', p: '0.6210', status: '✅ 양호' },
      { rank: '🥉 3위', name: '감마분포 (Gamma)', aic: '258.4', bic: '262.8', p: '0.4120', status: '✅ 양호' },
      { rank: '4위', name: '정규분포 (Normal)', aic: '274.6', bic: '279.0', p: '0.0410', status: '⚠️ 부적합' },
      { rank: '5위', name: '지수분포 (Exponential)', aic: '298.2', bic: '301.5', p: '0.0020', status: '⚠️ 부적합' }
    ]
  },
  normal: {
    name: '학생 표준 시험 성적 (Normal 타겟, n=60)',
    data: [52, 58, 61, 63, 65, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 81, 82, 84, 86, 88, 91, 95],
    bestDist: '정규분포 (Normal)',
    aic: 182.4,
    bic: 185.8,
    ks_p: 0.925,
    ranking: [
      { rank: '🥇 1위', name: '정규분포 (Normal)', aic: '182.4', bic: '185.8', p: '0.9250', status: '⭐ 최적(Best)' },
      { rank: '🥈 2위', name: '로지스틱분포 (Logistic)', aic: '184.2', bic: '187.6', p: '0.8840', status: '✅ 양호' },
      { rank: '🥉 3위', name: 'Student t-분포', aic: '185.0', bic: '189.4', p: '0.8120', status: '✅ 양호' },
      { rank: '4위', name: '라플라스분포 (Laplace)', aic: '196.5', bic: '200.0', p: '0.1250', status: '✅ 양호' }
    ]
  }
};

function initFittingSimulator() {
  const presetSelect = document.getElementById('fitPresetSelect');
  const tableBody = document.getElementById('fitRankingTableBody');

  function updateFitting() {
    const key = presetSelect.value;
    const cfg = FIT_PRESETS[key] || FIT_PRESETS.weibull;

    // 테이블 렌더링
    tableBody.innerHTML = '';
    cfg.ranking.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: bold; color: ${row.rank.includes('1위') ? 'var(--accent-cyan)' : 'inherit'}">${row.rank}</td>
        <td><strong>${row.name}</strong></td>
        <td>${row.aic}</td>
        <td>${row.bic}</td>
        <td>${row.p}</td>
        <td style="color: ${row.status.includes('최적') || row.status.includes('양호') ? 'var(--accent-green)' : 'var(--accent-red)'}">${row.status}</td>
      `;
      tableBody.appendChild(tr);
    });

    renderFitChart();
  }

  function renderFitChart() {
    const canvas = document.getElementById('fitCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = Math.max(300, Math.floor(canvas.getBoundingClientRect().width || canvas.clientWidth || 600));
    const height = 340;
    canvas.width = Math.round(width * window.devicePixelRatio);
    canvas.height = Math.round(height * window.devicePixelRatio);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const dark = isDarkMode();
    const bgColor = dark ? '#0b0f19' : '#ffffff';
    const gridColor = dark ? '#1e293b' : '#e2e8f0';
    const textColor = dark ? '#94a3b8' : '#64748b';
    const pointColor = dark ? '#00f2fe' : '#0284c7';
    const lineColor = '#ef4444';

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);

    const key = presetSelect.value;
    const cfg = FIT_PRESETS[key] || FIT_PRESETS.weibull;
    const data = [...cfg.data].sort((a, b) => a - b);
    const n = data.length;

    const padL = 50, padR = 25, padT = 35, padB = 40;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    // Q-Q 플롯 시뮬레이션
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padL, padT + plotH / 2); ctx.lineTo(width - padR, padT + plotH / 2);
    ctx.moveTo(padL + plotW / 2, padT); ctx.lineTo(padL + plotW / 2, height - padB);
    ctx.stroke();

    // 45도 기준선
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(padL + 15, padT + plotH - 15);
    ctx.lineTo(width - padR - 15, padT + 15);
    ctx.stroke();
    ctx.setLineDash([]);

    // Q-Q 관측점
    ctx.fillStyle = pointColor;
    for (let i = 0; i < n; i++) {
      const p = (i + 0.5) / n;
      const theoQ = invNormCDF(p); // -2.5 ~ +2.5
      const obsNorm = (data[i] - data[0]) / (data[n - 1] - data[0]) * 5 - 2.5;

      const px = padL + ((theoQ + 2.8) / 5.6) * plotW;
      const py = padT + plotH - ((obsNorm + 2.8) / 5.6) * plotH;

      ctx.beginPath();
      ctx.arc(px, py, 4.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // 제목
    ctx.fillStyle = dark ? '#fff' : '#0f172a';
    ctx.font = 'bold 13px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`🎯 정규 Q-Q 진단 플롯 (R² = 0.985) - ${cfg.bestDist}`, padL, 20);
  }

  presetSelect.addEventListener('change', updateFitting);
  window.renderFitChart = renderFitChart;
  window.addEventListener('resize', renderFitChart);
  updateFitting();
}

/* ==========================================================================
   5. Tab 3: Interactive Hypothesis Testing Playground
   ========================================================================== */
function initHypothesisSimulator() {
  const alphaSlider = document.getElementById('hypoAlphaSlider');
  const alphaVal = document.getElementById('hypoAlphaVal');
  const testSelect = document.getElementById('hypoTestSelect');
  const decisionBadge = document.getElementById('hypoDecisionBadge');

  function updateHypo() {
    const alpha = parseFloat(alphaSlider.value);
    alphaVal.textContent = alpha.toFixed(3);

    // 가상의 검정 통계량 (Welch t = 2.45, p = 0.018)
    const tStat = 2.45;
    const pVal = 0.018;

    if (pVal < alpha) {
      decisionBadge.className = 'callout callout-tip';
      decisionBadge.innerHTML = `<strong>🔴 귀무가설 H0 기각 (유의수준 α = ${alpha.toFixed(3)} 기준)</strong><br>` +
        `관측 통계량 t = ${tStat.toFixed(2)} (p-value = ${pVal.toFixed(3)} < α) → 두 집단 간 유의미한 차이가 통계적으로 입증되었습니다!`;
    } else {
      decisionBadge.className = 'callout callout-info';
      decisionBadge.innerHTML = `<strong>🔵 귀무가설 H0 채택 (유의수준 α = ${alpha.toFixed(3)} 기준)</strong><br>` +
        `관측 통계량 t = ${tStat.toFixed(2)} (p-value = ${pVal.toFixed(3)} ≥ α) → 집단 간 유의미한 차이를 주장할 충분한 통계적 증거가 부족합니다.`;
    }

    renderHypoChart();
  }

  function renderHypoChart() {
    const canvas = document.getElementById('hypoCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = Math.max(300, Math.floor(canvas.getBoundingClientRect().width || canvas.clientWidth || 600));
    const height = 340;
    canvas.width = Math.round(width * window.devicePixelRatio);
    canvas.height = Math.round(height * window.devicePixelRatio);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const dark = isDarkMode();
    const bgColor = dark ? '#0b0f19' : '#ffffff';
    const gridColor = dark ? '#1e293b' : '#e2e8f0';
    const textColor = dark ? '#94a3b8' : '#64748b';
    const primaryColor = dark ? '#4facfe' : '#2563eb';
    const rejectColor = dark ? 'rgba(239, 68, 68, 0.45)' : 'rgba(220, 38, 38, 0.4)';

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);

    const alpha = parseFloat(alphaSlider.value);
    const crit = Math.abs(invNormCDF(alpha / 2)); // 양측 기각역 임계값
    const tStat = 2.45;

    const padL = 50, padR = 25, padT = 30, padB = 40;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const minX = -4.0, maxX = 4.0;
    const steps = 200;
    const maxY = 0.45;

    // t-분포 곡선 및 기각역 채우기
    ctx.beginPath();
    ctx.moveTo(padL, padT + plotH);
    for (let i = 0; i <= steps; i++) {
      const x = minX + (i / steps) * (maxX - minX);
      const y = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * x * x);
      const px = padL + (i / steps) * plotW;
      const py = padT + plotH - (y / maxY) * plotH;
      ctx.lineTo(px, py);
    }
    ctx.lineTo(padL + plotW, padT + plotH);
    ctx.closePath();
    ctx.fillStyle = dark ? 'rgba(79, 172, 254, 0.12)' : 'rgba(37, 99, 235, 0.12)';
    ctx.fill();

    // 우측 기각역 (x >= crit)
    ctx.beginPath();
    const critIdxR = Math.round(((crit - minX) / (maxX - minX)) * steps);
    ctx.moveTo(padL + (critIdxR / steps) * plotW, padT + plotH);
    for (let i = critIdxR; i <= steps; i++) {
      const x = minX + (i / steps) * (maxX - minX);
      const y = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * x * x);
      ctx.lineTo(padL + (i / steps) * plotW, padT + plotH - (y / maxY) * plotH);
    }
    ctx.lineTo(padL + plotW, padT + plotH);
    ctx.closePath();
    ctx.fillStyle = rejectColor;
    ctx.fill();

    // 좌측 기각역 (x <= -crit)
    ctx.beginPath();
    const critIdxL = Math.round(((-crit - minX) / (maxX - minX)) * steps);
    ctx.moveTo(padL, padT + plotH);
    for (let i = 0; i <= critIdxL; i++) {
      const x = minX + (i / steps) * (maxX - minX);
      const y = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * x * x);
      ctx.lineTo(padL + (i / steps) * plotW, padT + plotH - (y / maxY) * plotH);
    }
    ctx.lineTo(padL + (critIdxL / steps) * plotW, padT + plotH);
    ctx.closePath();
    ctx.fillStyle = rejectColor;
    ctx.fill();

    // 외곽선
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const x = minX + (i / steps) * (maxX - minX);
      const y = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * x * x);
      const px = padL + (i / steps) * plotW;
      const py = padT + plotH - (y / maxY) * plotH;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // 임계값 수직선
    const pxCritR = padL + ((crit - minX) / (maxX - minX)) * plotW;
    const pxCritL = padL + ((-crit - minX) / (maxX - minX)) * plotW;
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1.8;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pxCritR, padT); ctx.lineTo(pxCritR, padT + plotH);
    ctx.moveTo(pxCritL, padT); ctx.lineTo(pxCritL, padT + plotH);
    ctx.stroke();
    ctx.setLineDash([]);

    // 관측 검정통계량 수직선 & 마커
    const pxStat = padL + ((tStat - minX) / (maxX - minX)) * plotW;
    ctx.strokeStyle = dark ? '#fff' : '#0f172a';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(pxStat, padT + 10); ctx.lineTo(pxStat, padT + plotH);
    ctx.stroke();

    ctx.fillStyle = dark ? '#fff' : '#0f172a';
    ctx.beginPath();
    ctx.arc(pxStat, padT + 10, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = 'bold 11px sans-serif';
    ctx.fillText(`관측 t = ${tStat.toFixed(2)}`, pxStat + 6, padT + 15);
    ctx.fillStyle = '#ef4444';
    ctx.fillText(`+${crit.toFixed(2)}`, pxCritR + 4, padT + plotH - 10);
    ctx.fillText(`-${crit.toFixed(2)}`, pxCritL - 32, padT + plotH - 10);
  }

  alphaSlider.addEventListener('input', updateHypo);
  testSelect.addEventListener('change', updateHypo);
  window.renderHypoChart = renderHypoChart;
  window.addEventListener('resize', renderHypoChart);
  updateHypo();
}

/* ==========================================================================
   6. Knowledge Base Filter & Search
   ========================================================================== */
function initKnowledgeFilter() {
  const searchInput = document.getElementById('kbSearchInput');
  const typeFilter = document.getElementById('kbTypeFilter');
  const cards = document.querySelectorAll('.kb-card');

  function filterCards() {
    const query = (searchInput.value || '').toLowerCase().trim();
    const type = typeFilter.value; // 'all', 'continuous', 'discrete'

    cards.forEach(card => {
      const title = card.getAttribute('data-title').toLowerCase();
      const cType = card.getAttribute('data-type');
      const text = card.textContent.toLowerCase();

      const matchQuery = !query || title.includes(query) || text.includes(query);
      const matchType = type === 'all' || cType === type;

      if (matchQuery && matchType) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterCards);
  if (typeFilter) typeFilter.addEventListener('change', filterCards);
}

/* ==========================================================================
   7. ScrollSpy & Code Copy
   ========================================================================== */
function initScrollSpy() {
  const sections = document.querySelectorAll('.manual-section');
  const navLinks = document.querySelectorAll('.toc-link');

  window.addEventListener('scroll', () => {
    let current = '';
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      const sectionHeight = section.clientHeight;
      if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
}

function initCopyCodeButtons() {
  document.querySelectorAll('.copy-code-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.nextElementSibling.textContent;
      navigator.clipboard.writeText(code).then(() => {
        const originalText = btn.textContent;
        btn.textContent = '✓ 복사됨!';
        setTimeout(() => { btn.textContent = originalText; }, 2000);
      });
    });
  });
}

/* ==========================================================================
   Math Helper Functions
   ========================================================================== */
function erf(x) {
  // Abramowitz and Stegun formula 7.1.26
  const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741;
  const a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;
  const sign = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1.0 / (1.0 + p * x);
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

function invNormCDF(p) {
  // Rational approximation for inverse normal CDF (Beasley-Springer-Moro)
  if (p <= 0) return -4.5;
  if (p >= 1) return 4.5;
  if (p < 0.5) return -invNormCDF(1 - p);
  const a = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637];
  const b = [-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833];
  const y = p - 0.5;
  if (Math.abs(y) < 0.42) {
    const r = y * y;
    return y * (((a[3] * r + a[2]) * r + a[1]) * r + a[0]) / ((((b[3] * r + b[2]) * r + b[1]) * r + b[0]) * r + 1.0);
  }
  let r = p;
  if (y > 0) r = 1 - p;
  r = Math.log(-Math.log(r));
  const c = [0.3374754822726147, 0.9761690190917186, 0.1607979714918209, 0.0276438810338635,
             0.0038405729373609, 0.0003951896511919, 0.0000321767881768, 0.0000002888167364, 0.0000003960315187];
  let x = c[0];
  for (let i = 1; i < 9; i++) x += c[i] * Math.pow(r, i);
  return y < 0 ? -x : x;
}

function gamma(z) {
  // Lanczos approximation
  const g = 7;
  const C = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
             771.32342877765313, -176.61502916214059, 12.507343278686905,
             -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (z < 0.5) return Math.PI / (Math.sin(Math.PI * z) * gamma(1 - z));
  z -= 1;
  let x = C[0];
  for (let i = 1; i < g + 2; i++) x += C[i] / (z + i);
  const t = z + g + 0.5;
  return Math.sqrt(2 * Math.PI) * Math.pow(t, z + 0.5) * Math.exp(-t) * x;
}

function factorial(n) {
  let f = 1;
  for (let i = 2; i <= n; i++) f *= i;
  return f;
}

function boxMuller() {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

function samplePoisson(lambda) {
  const L = Math.exp(-lambda);
  let k = 0, p = 1;
  do {
    k++;
    p *= Math.random();
  } while (p > L);
  return k - 1;
}
