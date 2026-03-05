/* ============================================================
   Quantum Pesticide Fate Modeling — Application Logic
   SPA navigation · Backend API integration · Charts
   ============================================================ */

const API_BASE = "http://localhost:5000/api";

// ---- DOM helpers -----------------------------------------------

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

// ---- State -----------------------------------------------------

let substancesData = [];
let scenariosData = [];
let substanceClasses = [];
let currentSort = { col: null, asc: true };
let quantumPredictions = null;  // batch predictions cache

// ---- API helpers -----------------------------------------------

async function apiFetch(path) {
  try {
    const res = await fetch(API_BASE + path);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error(`API error (${path}):`, e);
    return null;
  }
}

async function apiPost(path, body) {
  try {
    const res = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error(`API error (${path}):`, e);
    return null;
  }
}

// ---- Navigation ------------------------------------------------

function initNavigation() {
  const navItems = $$('.nav-item[data-panel]');
  const panels = $$('.panel');
  const overlay = $('#sidebar-overlay');

  function closeSidebar() {
    $('.sidebar').classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
  }

  function activate(panelId) {
    navItems.forEach(n => n.classList.toggle('active', n.dataset.panel === panelId));
    panels.forEach(p => p.classList.toggle('active', p.id === panelId));
    closeSidebar();
  }

  navItems.forEach(n => n.addEventListener('click', () => activate(n.dataset.panel)));

  const burger = $('.mobile-burger');
  if (burger) {
    burger.addEventListener('click', () => {
      const isOpen = $('.sidebar').classList.toggle('open');
      if (overlay) overlay.classList.toggle('visible', isOpen);
    });
  }
  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  activate('panel-dashboard');
}

// ---- Dashboard -------------------------------------------------

async function renderDashboard() {
  // Fetch substance count
  const subData = await apiFetch('/substances');
  const scnData = await apiFetch('/scenarios');

  const subCount = subData?.count || 0;
  const scnCount = scnData?.count || 0;

  // Update stat cards with animated counters
  animateCounter($('#stat-substances'), 0, subCount, 1500);
  animateCounter($('#stat-scenarios'), 0, scnCount, 1500);
  animateCounter($('#stat-quantum'), 0, 6, 1500);
  animateCounter($('#stat-models'), 0, 11, 1500);

  // Update badge counts
  const subBadge = $('#nav-substances .nav-badge');
  if (subBadge) subBadge.textContent = subCount;
}

function animateCounter(el, start, end, duration) {
  if (!el) return;
  const startTime = performance.now();
  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(start + (end - start) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ---- Substances ------------------------------------------------

async function loadSubstances() {
  const data = await apiFetch('/substances');
  if (!data) return;
  substancesData = data.substances;
  substanceClasses = data.classes;

  // Populate class filter
  const select = $('#substance-class-filter');
  if (select) {
    select.innerHTML = '<option value="all">All Classes</option>' +
      substanceClasses.map(c => `<option value="${c}">${c}</option>`).join('');
  }

  renderSubstances();
}

async function loadQuantumPredictions() {
  const data = await apiFetch('/quantum/predict-all');
  if (data && data.predictions) {
    quantumPredictions = {};
    data.predictions.forEach(p => {
      quantumPredictions[p.name] = p;
    });
    renderSubstances();  // re-render with quantum columns
  }
}

function renderSubstances(filter = '', classFilter = 'all') {
  const tbody = $('#substance-tbody');
  if (!tbody) return;
  const query = filter.toLowerCase();

  let filtered = substancesData.filter(s => {
    const matchesText = !query ||
      s.name.toLowerCase().includes(query) ||
      s.cas.includes(query) ||
      s.cls.toLowerCase().includes(query);
    const matchesClass = classFilter === 'all' || s.cls === classFilter;
    return matchesText && matchesClass;
  });

  if (currentSort.col) {
    filtered.sort((a, b) => {
      let va = a[currentSort.col], vb = b[currentSort.col];
      if (typeof va === 'string') { va = va.toLowerCase(); vb = (vb || '').toLowerCase(); }
      if (va < vb) return currentSort.asc ? -1 : 1;
      if (va > vb) return currentSort.asc ? 1 : -1;
      return 0;
    });
  }

  tbody.innerHTML = filtered.map(s => {
    const qp = quantumPredictions ? quantumPredictions[s.name] : null;
    const degPred = qp ? `<span style="color:var(--accent-cyan)">${qp.degtl50_pred?.toFixed(1) || '—'}</span>` : '<span style="color:var(--text-muted)">…</span>';
    const kocPred = qp ? `<span style="color:var(--accent-cyan)">${qp.koc_pred?.toFixed(0) || '—'}</span>` : '<span style="color:var(--text-muted)">…</span>';

    return `
    <tr>
      <td class="substance-name">${s.name}</td>
      <td class="cas">${s.cas}</td>
      <td class="mono">${s.degT50_soil} d</td>
      <td class="mono">${degPred}</td>
      <td class="mono">${s.koc?.toLocaleString()}</td>
      <td class="mono">${kocPred}</td>
      <td class="mono">${s.vapor_pressure?.toExponential(1)}</td>
      <td class="mono">${s.solubility}</td>
      <td class="mono">${s.mw}</td>
      <td>${s.cls}</td>
      <td style="font-size:11px;color:${s.status?.includes('Not') ? 'var(--accent-red)' : 'var(--accent-green)'}">${s.status || '—'}</td>
    </tr>`;
  }).join('');

  const footer = $('#substance-count');
  if (footer) footer.textContent = `${filtered.length} of ${substancesData.length} substances`;
}

function initSubstanceSearch() {
  const input = $('#substance-search');
  const select = $('#substance-class-filter');
  if (!input) return;

  input.addEventListener('input', () => {
    renderSubstances(input.value, select ? select.value : 'all');
  });
  if (select) {
    select.addEventListener('change', () => {
      renderSubstances(input.value, select.value);
    });
  }

  $$('.data-table thead th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.sort;
      if (currentSort.col === col) {
        currentSort.asc = !currentSort.asc;
      } else {
        currentSort.col = col;
        currentSort.asc = true;
      }
      renderSubstances(input.value, select ? select.value : 'all');
    });
  });
}

// ---- FOCUS Scenarios -------------------------------------------

async function renderScenarios() {
  const data = await apiFetch('/scenarios');
  if (!data) return;
  scenariosData = data.scenarios;

  const grid = $('#scenario-grid');
  if (!grid) return;

  grid.innerHTML = scenariosData.map(s => {
    const tierClass = s.tier === 'both' ? 'tier-both' : s.tier === 'gw' ? 'tier-gw' : 'tier-sw';
    const tierLabel = s.tier === 'both' ? 'GW + SW' : s.tier === 'gw' ? 'Groundwater' : 'Surface Water';
    return `
    <div class="scenario-card glass">
      <div class="sc-header">
        <span class="sc-name">${s.name}</span>
        <span class="sc-country">${s.flag}</span>
      </div>
      <div class="sc-meta">
        <div class="sc-meta-item">
          <div class="meta-label">Climate</div>
          <div class="meta-value">${s.climate}</div>
        </div>
        <div class="sc-meta-item">
          <div class="meta-label">Soil</div>
          <div class="meta-value">pH ${s.ph}, OC ${s.oc_pct}%</div>
        </div>
        <div class="sc-meta-item">
          <div class="meta-label">Crop</div>
          <div class="meta-value">${s.crop}</div>
        </div>
        <div class="sc-meta-item">
          <div class="meta-label">Rainfall</div>
          <div class="meta-value mono">${s.annual_rainfall_mm} mm/yr</div>
        </div>
        <div class="sc-meta-item">
          <div class="meta-label">Mean Temp</div>
          <div class="meta-value mono">${s.mean_temp_c} °C</div>
        </div>
        <div class="sc-meta-item">
          <div class="meta-label">Profile Depth</div>
          <div class="meta-value mono">${s.profile_depth_cm} cm</div>
        </div>
      </div>
      <span class="sc-tier ${tierClass}">${tierLabel}</span>
    </div>`;
  }).join('');
}

// ---- Quantum Status --------------------------------------------

const QUANTUM_APPROACHES = [
  {
    id: "vqe", abbr: "VQE", full: "Variational Quantum Eigensolver", icon: "◆",
    desc: "Ground state energy calculations for pesticide molecules — predict binding energies and sorption coefficients.",
    readiness: 65, qubits: "100–200", timeline: "2026–2028", status: "NISQ ready",
    hardware: "IonQ Aria (Azure)", app: "Koc prediction"
  },
  {
    id: "qpe", abbr: "QPE", full: "Quantum Phase Estimation", icon: "◇",
    desc: "Reaction pathway barriers for transition state calculations — predict DegT50 without wet-lab experiments.",
    readiness: 35, qubits: "200–500", timeline: "2027–2029", status: "Early research",
    hardware: "Quantinuum H1 (Azure)", app: "DegT50 prediction"
  },
  {
    id: "qml", abbr: "QML", full: "Quantum Machine Learning", icon: "◈",
    desc: "QSAR-style models with quantum feature maps — exponential feature space for fate parameter prediction. ▸ ACTIVE in this tool.",
    readiness: 50, qubits: "50–100", timeline: "2026–2027", status: "ACTIVE",
    hardware: "PennyLane sim", app: "DegT50 + Koc QSAR"
  },
  {
    id: "hhl", abbr: "HHL", full: "Harrow-Hassidim-Lloyd Algorithm", icon: "▤",
    desc: "Exponential speedup for linear systems from discretized Richards equation — accelerate soil transport simulations.",
    readiness: 12, qubits: "1000+", timeline: "2030+", status: "Fault-tolerant req.",
    hardware: "Future FT", app: "PDE acceleration"
  },
  {
    id: "qaoa", abbr: "QAOA", full: "Quantum Approx. Optimization Algorithm", icon: "⬢",
    desc: "Combinatorial optimization for parameter fitting — find better optima for model calibration across FOCUS scenarios.",
    readiness: 40, qubits: "50–200", timeline: "2027–2029", status: "Active research",
    hardware: "NISQ", app: "Model calibration"
  },
  {
    id: "qmc", abbr: "QMC", full: "Quantum Monte Carlo", icon: "◌",
    desc: "Quadratic speedup for probabilistic exposure assessment — uncertainty propagation across parameter space.",
    readiness: 25, qubits: "200–500", timeline: "2028–2030", status: "Theoretical",
    hardware: "Early FT", app: "Uncertainty analysis"
  },
];

async function renderQuantumStatus() {
  // Try to fetch live circuit info
  let circuitInfo = null;
  try {
    circuitInfo = await apiFetch('/quantum/status');
  } catch (e) { /* backend may not be running */ }

  const grid = $('#quantum-grid');
  if (!grid) return;

  grid.innerHTML = QUANTUM_APPROACHES.map(q => {
    const isQML = q.id === 'qml';
    const liveInfo = isQML && circuitInfo ? `
      <div style="margin-top:12px;padding:10px;background:rgba(0,240,255,0.06);border-radius:var(--radius-sm);border:1px solid rgba(0,240,255,0.15);font-size:12px;">
        <div style="font-weight:600;color:var(--accent-cyan);margin-bottom:6px;">▸ Live Circuit</div>
        <div style="color:var(--text-secondary)">
          ${circuitInfo.n_qubits} qubits · ${circuitInfo.n_layers} layers · ${circuitInfo.n_parameters} params<br>
          PennyLane ${circuitInfo.framework?.split(' ')[1] || ''} · ${circuitInfo.device?.split('(')[0] || ''}<br>
          Training loss: DegT50=${circuitInfo.training_loss_degtl50?.toFixed(3) || '—'}, Koc=${circuitInfo.training_loss_koc?.toFixed(3) || '—'}
        </div>
      </div>` : '';

    return `
    <div class="quantum-card glass qc-${q.id}">
      <div class="qc-header">
        <div class="qc-icon">${q.icon}</div>
        <div>
          <div class="qc-name">${q.abbr}</div>
          <div class="qc-full">${q.full}</div>
        </div>
      </div>
      <p style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">${q.desc}</p>
      <div class="qc-progress-bar">
        <div class="qc-progress-fill" data-width="${q.readiness}"></div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="font-size:12px;color:var(--text-muted);">Readiness</span>
        <span style="font-family:var(--font-mono);font-size:13px;font-weight:600;">${q.readiness}%</span>
      </div>
      <div class="qc-stats">
        <div class="qc-stat">
          <div class="qs-label">Qubits</div>
          <div class="qs-value">${q.qubits}</div>
        </div>
        <div class="qc-stat">
          <div class="qs-label">Hardware</div>
          <div class="qs-value" style="font-size:11px;">${q.hardware}</div>
        </div>
        <div class="qc-stat">
          <div class="qs-label">Application</div>
          <div class="qs-value" style="font-size:11px;">${q.app}</div>
        </div>
      </div>
      <span class="qc-timeline">${q.timeline} · ${q.status}</span>
      ${liveInfo}
    </div>`;
  }).join('');

  setTimeout(() => {
    $$('.qc-progress-fill').forEach(bar => {
      bar.style.width = bar.dataset.width + '%';
    });
  }, 200);
}

// ---- Run Configuration -----------------------------------------

async function initRunConfig() {
  const form = $('#run-form');
  const results = $('#result-chart-area');
  const running = $('#running-indicator');
  if (!form) return;

  // Populate substance dropdown from API
  const subData = await apiFetch('/substances');
  const subSelect = $('#run-substance');
  if (subSelect && subData) {
    subSelect.innerHTML = '<option value="">Select substance…</option>' +
      subData.substances.map(s => `<option value="${s.name}">${s.name} (${s.cas})</option>`).join('');
  }

  // Populate scenario dropdown from API
  const scnData = await apiFetch('/scenarios');
  const scnSelect = $('#run-scenario');
  if (scnSelect && scnData) {
    scnSelect.innerHTML = '<option value="">Select scenario…</option>' +
      scnData.scenarios.map(s => `<option value="${s.name}">${s.name} — ${s.country}</option>`).join('');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const substance = subSelect?.value;
    const scenario = scnSelect?.value;
    const years = parseInt($('#run-years')?.value || '20');
    const quantum = $('#run-quantum')?.checked ?? true;

    if (!substance || !scenario) {
      alert('Please select both a substance and a scenario.');
      return;
    }

    // Show running indicator
    if (running) running.classList.add('visible');
    if (results) results.classList.remove('visible');
    $('#results-placeholder').style.display = 'none';

    // Call backend API
    const data = await apiPost('/run', { substance, scenario, years, quantum });

    if (running) running.classList.remove('visible');

    if (data && !data.error) {
      renderResults(data);
    } else {
      alert('Simulation failed: ' + (data?.error || 'Backend not available. Start it with: .venv/bin/python backend/server.py'));
    }
  });
}

function renderResults(data) {
  const results = $('#result-chart-area');
  if (results) results.classList.add('visible');

  const months = data.months || [];
  const classical = data.classical;
  const quantum = data.quantum;

  // Draw chart
  const canvas = $('#result-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.parentElement.clientWidth;
  const h = 280;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  ctx.scale(dpr, dpr);

  const classicalPEC = classical.pec_gw_monthly;
  const quantumPEC = quantum ? quantum.pec_gw_monthly : null;
  const allVals = [...classicalPEC, ...(quantumPEC || [])];
  const maxPec = Math.max(...allVals, 1e-6);
  const nPoints = classicalPEC.length;

  // Background
  ctx.fillStyle = 'rgba(10,14,39,0.5)';
  ctx.fillRect(0, 0, w, h);

  const padL = 60, padR = 20, padT = 25, padB = 35;

  // Grid lines
  ctx.strokeStyle = 'rgba(79,140,255,0.08)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = padT + (h - padT - padB) * i / 5;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(w - padR, y); ctx.stroke();
    ctx.fillStyle = 'rgba(136,146,176,0.6)';
    ctx.font = '10px "JetBrains Mono"';
    ctx.textAlign = 'right';
    ctx.fillText((maxPec * (1 - i / 5)).toExponential(1), padL - 4, y + 3);
  }

  // X-axis labels
  ctx.fillStyle = 'rgba(136,146,176,0.6)';
  ctx.textAlign = 'center';
  const years = data.years || 20;
  for (let yr = 0; yr <= years; yr += 5) {
    const x = padL + (w - padL - padR) * (yr * 12) / nPoints;
    ctx.fillText(`Yr ${yr}`, x, h - 8);
  }

  // Draw classical PEC line
  drawLine(ctx, classicalPEC, w, h, nPoints, maxPec, padL, padR, padT, padB, 'rgba(79,140,255,0.9)', 'rgba(79,140,255,0.08)');
  // Draw quantum PEC line
  if (quantumPEC) {
    drawLine(ctx, quantumPEC, w, h, nPoints, maxPec, padL, padR, padT, padB, 'rgba(0,240,255,0.9)', 'rgba(0,240,255,0.06)');
  }

  // Legend — top-left with background
  const legendX = padL + 8;
  let legendY = padT + 4;
  const legendH = quantum ? 34 : 18;

  // Legend background
  ctx.fillStyle = 'rgba(10,14,39,0.75)';
  ctx.fillRect(legendX - 4, legendY - 4, 280, legendH + 8);

  ctx.font = '10px "JetBrains Mono", monospace';
  ctx.textAlign = 'left';

  // Classical entry
  ctx.fillStyle = 'rgba(79,140,255,0.9)';
  ctx.fillRect(legendX, legendY, 8, 8);
  ctx.fillStyle = '#aab4cc';
  ctx.fillText(`Classical (DegT50=${classical.degT50_used}d, Koc=${Math.round(classical.koc_used).toLocaleString()})`, legendX + 12, legendY + 8);

  // Quantum entry
  if (quantum) {
    legendY += 16;
    ctx.fillStyle = 'rgba(0,240,255,0.9)';
    ctx.fillRect(legendX, legendY, 8, 8);
    ctx.fillStyle = '#aab4cc';
    ctx.fillText(`QML (DegT50=${quantum.degT50_used?.toFixed(1)}d, Koc=${Math.round(quantum.koc_used)?.toLocaleString()})`, legendX + 12, legendY + 8);
  }

  // Format PEC for display (avoid showing 1e-61 underflow artefacts)
  function fmtPEC(v) {
    if (v == null || isNaN(v)) return '—';
    if (Math.abs(v) < 1e-10) return '< 0.001 µg/L';
    if (Math.abs(v) < 0.01) return v.toExponential(2) + ' µg/L';
    return v.toFixed(3) + ' µg/L';
  }
  function fmtLeached(v) {
    if (v == null || isNaN(v)) return '—';
    if (Math.abs(v) < 1e-10) return '< 0.0001 g/ha';
    return v.toFixed(4) + ' g/ha';
  }

  // Update summary stats
  setText('#rs-peak-classical', fmtPEC(classical.pec_80th));
  setText('#rs-avg-classical', fmtLeached(classical.total_leached));
  setText('#rs-label-peak-c', 'PEC 80th (Classical)');
  setText('#rs-label-avg-c', 'Total Leached (Classical)');

  if (quantum) {
    setText('#rs-peak-quantum', fmtPEC(quantum.pec_80th));
    setText('#rs-avg-quantum', fmtLeached(quantum.total_leached));
    const peakQEl = $('#rs-peak-quantum');
    const avgQEl = $('#rs-avg-quantum');
    if (peakQEl) peakQEl.style.color = 'var(--accent-cyan)';
    if (avgQEl) avgQEl.style.color = 'var(--accent-cyan)';
  } else {
    setText('#rs-peak-quantum', '—');
    setText('#rs-avg-quantum', '—');
  }

  // Show quantum prediction metadata if available
  if (data.quantum_predictions) {
    const qp = data.quantum_predictions;
    const metaEl = $('#quantum-meta');
    if (metaEl) {
      metaEl.style.display = 'block';
      const degErr = Math.abs(qp.degT50_predicted - qp.degT50_experimental) / Math.max(qp.degT50_experimental, 0.1) * 100;
      const kocErr = Math.abs(qp.koc_predicted - qp.koc_experimental) / Math.max(qp.koc_experimental, 0.1) * 100;
      metaEl.innerHTML = `
        <div style="font-size:12px;font-weight:600;color:var(--accent-cyan);margin-bottom:6px;">▸ Quantum ML Predictions Used</div>
        <div style="font-size:12px;color:var(--text-secondary);">
          DegT50: ${qp.degT50_predicted?.toFixed(1)} d <span style="color:var(--text-muted)">(exp: ${qp.degT50_experimental} d, err: ${degErr.toFixed(0)}%)</span><br>
          Koc: ${qp.koc_predicted?.toFixed(0)} mL/g <span style="color:var(--text-muted)">(exp: ${qp.koc_experimental?.toLocaleString()}, err: ${kocErr.toFixed(0)}%)</span>
        </div>
        <div style="font-size:11px;margin-top:6px;color:var(--text-muted);font-style:italic;">
          Note: QML circuit (10 qubits, 8 layers) trained on 51 substances. Predictions improve with more qubits and training data.
        </div>`;

      // Add interpretive note if both PECs are near zero
      const cPec = classical.pec_80th || 0;
      const qPec = quantum?.pec_80th || 0;
      if (cPec < 1e-10 && qPec < 1e-10) {
        metaEl.innerHTML += `
          <div style="margin-top:10px;padding:10px;background:rgba(255,200,50,0.06);border:1px solid rgba(255,200,50,0.15);border-radius:6px;font-size:12px;color:var(--text-secondary);">
            ▸ <strong>No significant leaching predicted.</strong> This substance has very high Koc (>${Math.min(classical.koc_used, quantum?.koc_used || Infinity).toLocaleString()} mL/g), 
            indicating strong soil sorption in both classical and quantum-predicted scenarios. 
            <em>Try <strong>Atrazine</strong>, <strong>Metribuzin</strong>, or <strong>Isoproturon</strong> for substances that show meaningful leaching differences.</em>
          </div>`;
      }
    }
  }
}

function drawLine(ctx, data, w, h, n, maxY, padL, padR, padT, padB, color, fillColor) {
  const cw = w - padL - padR;
  const ch = h - padT - padB;

  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  data.forEach((v, i) => {
    const x = padL + cw * i / (n - 1);
    const y = padT + ch * (1 - v / maxY);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.lineTo(padL + cw, padT + ch);
  ctx.lineTo(padL, padT + ch);
  ctx.closePath();
  ctx.fillStyle = fillColor;
  ctx.fill();
}

function setText(sel, text) {
  const el = $(sel);
  if (el) el.textContent = text;
}

// ---- Validation page ----

async function renderValidation() {
  const content = $('#validation-content');
  const loading = $('#validation-loading');
  if (!content) return;

  loading.style.display = 'block';
  content.innerHTML = '';

  try {
    const res = await fetch(API_BASE + '/validation');
    const data = await res.json();
    loading.style.display = 'none';

    if (!data.comparisons || data.comparisons.length === 0) {
      content.innerHTML = '<div style="padding:20px;color:var(--text-muted);">No validation data available. Start the backend first.</div>';
      return;
    }

    // Overall performance summary
    let within2 = 0, within5 = 0, total = 0;
    data.comparisons.forEach(c => {
      if (c.classical.within_factor_2 !== null) { total++; if (c.classical.within_factor_2) within2++; if (c.classical.within_factor_5) within5++; }
    });
    let qWithin2 = 0, qWithin5 = 0;
    data.comparisons.forEach(c => {
      if (c.quantum.within_factor_2 !== null) { if (c.quantum.within_factor_2) qWithin2++; if (c.quantum.within_factor_5) qWithin5++; }
    });

    let html = `<div class="glass" style="padding:20px;margin-bottom:20px;">
      <div class="section-title"><span class="st-icon">▣</span> Model Performance Summary</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">
        <div style="text-align:center;padding:12px;background:rgba(79,140,255,0.06);border-radius:8px;border:1px solid rgba(79,140,255,0.15);">
          <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Classical</div>
          <div style="font-size:20px;font-weight:700;color:var(--accent-blue);margin:4px 0;">${within2}/${total}</div>
          <div style="font-size:11px;color:var(--text-secondary);">within factor-of-2 of field</div>
          <div style="font-size:13px;color:var(--text-muted);margin-top:4px;">${within5}/${total} within factor-of-5</div>
        </div>
        <div style="text-align:center;padding:12px;background:rgba(0,240,255,0.06);border-radius:8px;border:1px solid rgba(0,240,255,0.15);">
          <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;">Quantum ML</div>
          <div style="font-size:20px;font-weight:700;color:var(--accent-cyan);margin:4px 0;">${qWithin2}/${total}</div>
          <div style="font-size:11px;color:var(--text-secondary);">within factor-of-2 of field</div>
          <div style="font-size:13px;color:var(--text-muted);margin-top:4px;">${qWithin5}/${total} within factor-of-5</div>
        </div>
      </div>
    </div>`;

    // Per-substance cards
    data.comparisons.forEach(c => {
      const fmtPec = v => (v != null && v > 0.001) ? v.toFixed(3) : '< 0.001';
      const fmtLch = v => (v != null && v > 0.0001) ? v.toFixed(4) : '< 0.0001';
      const ratioColor = r => {
        if (!r) return 'var(--text-muted)';
        if (r >= 0.5 && r <= 2.0) return 'var(--accent-green)';
        if (r >= 0.2 && r <= 5.0) return '#f0c040';
        return '#f06060';
      };

      html += `<div class="glass" style="padding:20px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <div>
            <div style="font-size:16px;font-weight:700;color:var(--text-primary);">
              ${c.substance}
            </div>
            <div style="font-size:12px;color:var(--text-muted);">${c.scenario} · ${c.region} · ${c.monitoring_years}</div>
          </div>
        </div>

        <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px;">
          <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
            <th style="text-align:left;padding:8px;color:var(--text-muted);font-size:11px;text-transform:uppercase;">Metric</th>
            <th style="text-align:center;padding:8px;color:var(--accent-blue);font-size:11px;">Classical</th>
            <th style="text-align:center;padding:8px;color:var(--accent-cyan);font-size:11px;">Quantum ML</th>
            <th style="text-align:center;padding:8px;color:var(--accent-green);font-size:11px;">Field Obs</th>
          </tr>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
            <td style="padding:8px;color:var(--text-secondary);">PEC 80th (µg/L)</td>
            <td style="text-align:center;padding:8px;font-weight:600;color:var(--accent-blue);">${fmtPec(c.classical.pec_80th)}</td>
            <td style="text-align:center;padding:8px;font-weight:600;color:var(--accent-cyan);">${fmtPec(c.quantum.pec_80th)}</td>
            <td style="text-align:center;padding:8px;font-weight:600;color:var(--accent-green);">${c.field.pec_p80}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
            <td style="padding:8px;color:var(--text-secondary);">PEC Mean (µg/L)</td>
            <td style="text-align:center;padding:8px;color:var(--text-muted);">—</td>
            <td style="text-align:center;padding:8px;color:var(--text-muted);">—</td>
            <td style="text-align:center;padding:8px;color:var(--accent-green);">${c.field.pec_mean}</td>
          </tr>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
            <td style="padding:8px;color:var(--text-secondary);">Leached (g/ha)</td>
            <td style="text-align:center;padding:8px;color:var(--accent-blue);">${fmtLch(c.classical.leached)}</td>
            <td style="text-align:center;padding:8px;color:var(--accent-cyan);">${fmtLch(c.quantum.leached)}</td>
            <td style="text-align:center;padding:8px;color:var(--accent-green);">${c.field.leached_g_ha || '—'}</td>
          </tr>
          <tr>
            <td style="padding:8px;color:var(--text-secondary);">Model/Field ratio</td>
            <td style="text-align:center;padding:8px;font-weight:600;color:${ratioColor(c.classical.pec_ratio_to_field)};">${c.classical.pec_ratio_to_field || '—'}×</td>
            <td style="text-align:center;padding:8px;font-weight:600;color:${ratioColor(c.quantum.pec_ratio_to_field)};">${c.quantum.pec_ratio_to_field || '—'}×</td>
            <td style="text-align:center;padding:8px;color:var(--text-muted);">1.0×</td>
          </tr>
        </table>

        <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;font-style:italic;">${c.notes}</div>
        <div style="font-size:10px;color:var(--text-muted);">
          <strong>Sources:</strong> ${c.sources.map(s => s.name + ' (' + s.ref + ')').join(' · ')}
        </div>
      </div>`;
    });

    content.innerHTML = html;
  } catch (e) {
    loading.style.display = 'none';
    content.innerHTML = `<div style="padding:20px;color:#f06060;">Error loading validation: ${e.message}</div>`;
  }
}

// ---- QML vs Classical Comparison page ----

async function renderComparison() {
  const content = $('#comparison-content');
  const loading = $('#comparison-loading');
  loading.style.display = 'block';

  try {
    const data = await apiFetch('/classical-baseline');
    loading.style.display = 'none';

    // Build the comparison table
    const rf_loo = data.models.RandomForest.loo;
    const rf_5f = data.models.RandomForest['5fold'];
    const gb_loo = data.models.GradientBoosting.loo;
    const gb_5f = data.models.GradientBoosting['5fold'];

    // Try to load QML CV results from cache
    let qml_5f = null;
    let qml_loo = null;
    try {
      const qmlCV = await apiFetch('/quantum/cv-results');
      if (qmlCV && qmlCV['5fold']) {
        qml_5f = qmlCV['5fold'];
      }
      if (qmlCV && qmlCV['loo']) {
        qml_loo = qmlCV['loo'];
      }
    } catch (e) { /* QML CV not available yet */ }

    function fmtR2(v) {
      if (v === null || v === undefined) return '—';
      const color = v > 0.5 ? '#0ff' : v > 0.2 ? '#6f6' : v > 0 ? '#fa0' : '#f44';
      return `<span style="color:${color};font-weight:700">${v.toFixed(3)}</span>`;
    }
    function fmtMAE(v) {
      if (v === null || v === undefined) return '—';
      return v.toFixed(3);
    }
    function fmtRMSE(v) {
      if (v === null || v === undefined) return '—';
      return v.toFixed(3);
    }

    // Determine quantum advantage verdict for each property
    function verdict(qml_r2, best_classical_r2, prop) {
      if (!qml_r2 || qml_r2 === null) return '<span style="color:var(--text-muted)">Awaiting QML CV</span>';
      const diff = qml_r2 - best_classical_r2;
      if (diff > 0.05) return `<span style="color:#0ff;font-weight:700">+ QML wins (${prop} +${(diff * 100).toFixed(0)}%)</span>`;
      if (diff > -0.05) return `<span style="color:#fa0">≡ Comparable</span>`;
      return `<span style="color:#f44">– Classical wins</span>`;
    }

    const degVerdict = verdict(qml_5f?.deg_r2, Math.max(rf_5f.deg_r2, gb_5f.deg_r2), 'DegT50');
    const kocVerdict = verdict(qml_5f?.koc_r2, Math.max(rf_5f.koc_r2, gb_5f.koc_r2), 'Koc');

    // Feature importances (from RF)
    const degImp = Object.entries(data.feature_importances.deg).sort((a, b) => b[1] - a[1]);
    const kocImp = Object.entries(data.feature_importances.koc).sort((a, b) => b[1] - a[1]);
    const maxDegImp = degImp[0][1];
    const maxKocImp = kocImp[0][1];

    function impBar(name, val, max) {
      const pct = Math.round(val / max * 100);
      return `<div style="display:flex;align-items:center;margin:4px 0;font-size:13px;">
        <span style="width:140px;color:var(--text-muted)">${name}</span>
        <div style="flex:1;background:var(--glass-border);border-radius:4px;height:18px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#0ff,#6f0);border-radius:4px;transition:width 0.6s;"></div>
        </div>
        <span style="width:50px;text-align:right;color:var(--text-dim)">${(val * 100).toFixed(1)}%</span>
      </div>`;
    }

    content.innerHTML = `
      <!-- Model Performance Comparison -->
      <div class="glass" style="padding:24px;margin-bottom:24px;">
        <div class="section-title"><span class="st-icon">▣</span> Model Performance (5-Fold CV, ${data.n_substances} substances)</div>
        <table style="width:100%;border-collapse:collapse;margin-top:16px;">
          <thead>
            <tr style="border-bottom:1px solid var(--glass-border);">
              <th style="text-align:left;padding:10px 8px;color:var(--text-muted);font-size:11px;text-transform:uppercase;">Model</th>
              <th style="text-align:center;padding:10px 8px;color:var(--text-muted);font-size:11px;">DegT50 R²</th>
              <th style="text-align:center;padding:10px 8px;color:var(--text-muted);font-size:11px;">DegT50 MAE</th>
              <th style="text-align:center;padding:10px 8px;color:var(--text-muted);font-size:11px;">Koc R²</th>
              <th style="text-align:center;padding:10px 8px;color:var(--text-muted);font-size:11px;">Koc MAE</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid var(--glass-border);background:rgba(0,255,255,0.05);">
              <td style="padding:10px 8px;font-weight:700;color:#0ff;">◆ QML 12-Qubit VQC</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(qml_5f?.deg_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(qml_5f?.deg_mae)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(qml_5f?.koc_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(qml_5f?.koc_mae)}</td>
            </tr>
            <tr style="border-bottom:1px solid var(--glass-border);">
              <td style="padding:10px 8px;font-weight:600;color:var(--text-bright);">▲ Random Forest</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(rf_5f.deg_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(rf_5f.deg_mae)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(rf_5f.koc_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(rf_5f.koc_mae)}</td>
            </tr>
            <tr style="border-bottom:1px solid var(--glass-border);">
              <td style="padding:10px 8px;font-weight:600;color:var(--text-bright);">▼ Gradient Boosting</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(gb_5f.deg_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(gb_5f.deg_mae)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtR2(gb_5f.koc_r2)}</td>
              <td style="text-align:center;padding:10px 8px;">${fmtMAE(gb_5f.koc_mae)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Verdict -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
        <div class="glass" style="padding:20px;text-align:center;">
          <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;">DegT50 (Half-Life)</div>
          <div style="font-size:16px;">${degVerdict}</div>
          <div style="font-size:12px;color:var(--text-dim);margin-top:8px;">
            QML: ${qml_5f?.deg_r2?.toFixed(3) || '—'} vs RF: ${rf_5f.deg_r2.toFixed(3)} vs GBM: ${gb_5f.deg_r2.toFixed(3)}
          </div>
        </div>
        <div class="glass" style="padding:20px;text-align:center;">
          <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;">Koc (Adsorption)</div>
          <div style="font-size:16px;">${kocVerdict}</div>
          <div style="font-size:12px;color:var(--text-dim);margin-top:8px;">
            QML: ${qml_5f?.koc_r2?.toFixed(3) || '—'} vs RF: ${rf_5f.koc_r2.toFixed(3)} vs GBM: ${gb_5f.koc_r2.toFixed(3)}
          </div>
        </div>
      </div>

      <!-- Feature Importances -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
        <div class="glass" style="padding:20px;">
          <div class="section-title" style="font-size:14px;"><span class="st-icon">◇</span> Feature Importance — DegT50</div>
          <div style="margin-top:12px;">
            ${degImp.map(([n, v]) => impBar(n, v, maxDegImp)).join('')}
          </div>
        </div>
        <div class="glass" style="padding:20px;">
          <div class="section-title" style="font-size:14px;"><span class="st-icon">◇</span> Feature Importance — Koc</div>
          <div style="margin-top:12px;">
            ${kocImp.map(([n, v]) => impBar(n, v, maxKocImp)).join('')}
          </div>
        </div>
      </div>

      <!-- Interpretation -->
      <div class="glass" style="padding:20px;">
        <div class="section-title"><span class="st-icon">▸</span> Interpretation</div>
        <div style="font-size:14px;color:var(--text-dim);line-height:1.7;margin-top:12px;">
          <p><strong style="color:#0ff">DegT50 (soil degradation half-life)</strong> is the harder prediction task.
          Classical models (RF R²=${rf_5f.deg_r2.toFixed(2)}, GBM R²=${gb_5f.deg_r2.toFixed(2)}) struggle because
          degradation depends on microbial pathways not captured by molecular descriptors alone.
          The quantum circuit may be learning non-linear correlations in 4096-dimensional Hilbert space
          that classical models cannot efficiently represent.</p>
          <p style="margin-top:8px;"><strong style="color:#6f6">Koc (organic carbon adsorption)</strong> is well-predicted by logP and solubility.
          RF feature importance confirms these two features account for ${((kocImp.find(x => x[0] === 'logP')?.[1] || 0) * 100 + (kocImp.find(x => x[0] === 'solubility_log')?.[1] || 0) * 100).toFixed(0)}%
          of the variance. Tree-based models excel at learning simple feature-target relationships.</p>
          <p style="margin-top:8px;color:var(--text-muted);">
            <em>Note: QML results are from 5-fold CV on 102 substances. LOO CV is running on laptop32.
            Classical results are from ${data.n_substances} substances with ${data.n_features} molecular descriptors.</em>
          </p>
        </div>
      </div>
    `;

    // Fetch error analysis and append
    try {
      const errData = await apiFetch('/error-analysis');
      const degClasses = errData.deg_by_class.slice(0, 15);
      const kocClasses = errData.koc_by_class.slice(0, 15);

      function errColor(e) {
        if (e > 0.8) return '#f44';
        if (e > 0.5) return '#fa0';
        if (e > 0.3) return '#ff0';
        return '#6f6';
      }

      function errRow(d) {
        return `<tr style="border-bottom:1px solid var(--glass-border);">
          <td style="padding:6px 8px;font-size:13px;">${d.cls}</td>
          <td style="text-align:center;padding:6px;font-size:13px;">${d.n}</td>
          <td style="text-align:center;padding:6px;font-weight:700;color:${errColor(d.mean_error)}">${d.mean_error.toFixed(2)}</td>
          <td style="text-align:center;padding:6px;font-size:12px;color:var(--text-dim)">${d.max_error.toFixed(2)}</td>
        </tr>`;
      }

      content.innerHTML += `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;">
          <div class="glass" style="padding:20px;">
            <div class="section-title" style="font-size:14px;"><span class="st-icon">●</span> DegT50 Error by Class (RF LOO)</div>
            <table style="width:100%;border-collapse:collapse;margin-top:12px;">
              <thead><tr style="border-bottom:1px solid var(--glass-border);">
                <th style="text-align:left;padding:6px 8px;font-size:11px;color:var(--text-muted);text-transform:uppercase">Class</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">N</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">Mean Err</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">Max</th>
              </tr></thead>
              <tbody>${degClasses.map(errRow).join('')}</tbody>
            </table>
          </div>
          <div class="glass" style="padding:20px;">
            <div class="section-title" style="font-size:14px;"><span class="st-icon">○</span> Koc Error by Class (RF LOO)</div>
            <table style="width:100%;border-collapse:collapse;margin-top:12px;">
              <thead><tr style="border-bottom:1px solid var(--glass-border);">
                <th style="text-align:left;padding:6px 8px;font-size:11px;color:var(--text-muted);text-transform:uppercase">Class</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">N</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">Mean Err</th>
                <th style="text-align:center;padding:6px;font-size:11px;color:var(--text-muted)">Max</th>
              </tr></thead>
              <tbody>${kocClasses.map(errRow).join('')}</tbody>
            </table>
          </div>
        </div>
      `;
    } catch (e) {
      // Error analysis not critical — silently skip
    }

  } catch (e) {
    loading.style.display = 'none';
    content.innerHTML = `<div style="padding:20px;color:#f06060;">Error loading comparison: ${e.message}</div>`;
  }
}

// ---- Backend readiness & training banner -----------------------

let backendReady = false;
let quantumReady = false;

function updateTrainingBanner(status, done = false) {
  let banner = $('#backend-status-banner');
  if (!banner) {
    // Insert at top of main content area — visible from any panel
    const main = $('.main-content');
    if (!main) return;
    banner = document.createElement('div');
    banner.id = 'backend-status-banner';
    banner.style.cssText = `
      margin:0 0 16px 0; padding:14px 18px;
      background:rgba(0,240,255,0.06); border:1px solid rgba(0,240,255,0.2);
      border-radius:var(--radius-sm); font-size:13px;
      display:flex; align-items:center; gap:12px;
      color:var(--text-secondary); transition: opacity 0.5s;
    `;
    main.insertBefore(banner, main.firstChild);
  }

  if (done) {
    banner.innerHTML = `
      <span style="font-size:18px;color:var(--accent-green);">\u2713</span>
      <div>
        <div style="font-weight:600;color:var(--accent-green);">${status}</div>
      </div>`;
    setTimeout(() => {
      banner.style.opacity = '0';
      setTimeout(() => banner.remove(), 500);
    }, 5000);
  } else {
    banner.innerHTML = `
      <div class="spinner" style="width:18px;height:18px;border-width:2px;flex-shrink:0;"></div>
      <div>
        <div style="font-weight:600;color:var(--accent-cyan);">${status}</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">Simulation results require trained quantum circuits</div>
      </div>`;
  }
}

function setSimButtonEnabled(enabled) {
  const btn = $('#run-form button[type="submit"]');
  if (btn) {
    btn.disabled = !enabled;
    btn.style.opacity = enabled ? '1' : '0.4';
    btn.style.pointerEvents = enabled ? 'auto' : 'none';
  }
}

// ---- Initialize ------------------------------------------------

document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  initSubstanceSearch();

  // Show training banner and disable sim button
  updateTrainingBanner('Connecting to backend…');
  setSimButtonEnabled(false);

  // Poll backend until it's ready (training blocks server startup)
  let elapsed = 0;
  let backendUp = false;
  while (!backendUp) {
    try {
      const res = await fetch(API_BASE + '/health', { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        backendUp = true;
      }
    } catch (e) { /* not ready yet */ }

    if (!backendUp) {
      elapsed += 3;
      const dots = '.'.repeat((Math.floor(elapsed / 3) % 3) + 1);
      updateTrainingBanner(`Training quantum circuits on 51 substances${dots} (${elapsed}s elapsed)`);
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  updateTrainingBanner('Backend ready! Loading data…');

  // Now load all data — await each to ensure it completes
  await renderDashboard();
  await loadSubstances();
  await renderScenarios();
  await renderQuantumStatus();
  await renderValidation();
  await renderComparison();
  await initRunConfig();

  // Load quantum predictions
  updateTrainingBanner('Loading quantum ML predictions for all substances…');
  await loadQuantumPredictions();

  // Done!
  if (quantumPredictions && Object.keys(quantumPredictions).length > 0) {
    const count = Object.keys(quantumPredictions).length;
    updateTrainingBanner(`Quantum circuits ready — ${count} substances predicted (10 qubits, 8 layers)`, true);
  } else {
    updateTrainingBanner('Backend ready — quantum predictions available', true);
  }
  setSimButtonEnabled(true);
});
