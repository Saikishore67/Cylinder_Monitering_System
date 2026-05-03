
  // ---- INIT ----
  window.addEventListener('load', () => {
    setTimeout(() => {
      document.getElementById('pageLoading').classList.add('hidden');
      // animate progress bar
      setTimeout(() => {
        document.getElementById('progressFill').style.width = '68%';
      }, 200);
    }, 900);
  });

  // ---- DARK MODE ----
  let dark = false;
  function toggleDark() {
    dark = !dark;
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : '');
    document.getElementById('darkBtn').textContent = dark ? '☀️' : '🌙';
    if (chartInstance) {
      updateChartTheme();
    }
  }

  // ---- SIDEBAR ----
  function toggleSidebar() {
    const s = document.getElementById('sidebar');
    const o = document.getElementById('sidebarOverlay');
    s.classList.toggle('open');
    o.classList.toggle('open');
  }
  function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('open');
  }

  function setActiveMenu(el) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    el.classList.add('active');
    closeSidebar();
  }

  // ---- TABS ----
  function setActiveTab(el) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
  }

  // ---- CHART ----
  const ctx = document.getElementById('weightChart').getContext('2d');
  let chartInstance;

  function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      line: isDark ? '#4a9eff' : '#1d3557',
      fill1: isDark ? 'rgba(74,158,255,0.18)' : 'rgba(29,53,87,0.12)',
      fill2: isDark ? 'rgba(74,158,255,0)' : 'rgba(29,53,87,0)',
      grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)',
      tick: isDark ? '#9ca3af' : '#9ca3af',
    };
  }

  function generateData(hours) {
    const pts = hours === 24 ? 9 : hours === 12 ? 7 : hours === 6 ? 6 : 5;
    const base = [30, 28.5, 27.2, 26.8, 26.1, 25.5, 25.2, 24.9, 24.5];
    const data = base.slice(0, pts);
    const labels = [];
    for (let i = 0; i < pts; i++) {
      if (i === pts - 1) { labels.push('Current'); continue; }
      const h = Math.round((hours / (pts - 1)) * i);
      labels.push(h.toString().padStart(2,'0') + ':00');
    }
    return { labels, data };
  }

  function buildChart(hours = 24) {
    const { labels, data } = generateData(hours);
    const c = getChartColors();

    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data,
          borderColor: c.line,
          borderWidth: 2.5,
          tension: 0.45,
          fill: true,
          backgroundColor: (ctx) => {
            const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 180);
            g.addColorStop(0, c.fill1);
            g.addColorStop(1, c.fill2);
            return g;
          },
          pointRadius: 4,
          pointBackgroundColor: c.line,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: dark ? '#1c2030' : '#1a1d2e',
            titleColor: '#fff',
            bodyColor: 'rgba(255,255,255,0.7)',
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => ` ${ctx.parsed.y} kg`
            }
          }
        },
        scales: {
          x: {
            grid: { color: c.grid, drawBorder: false },
            ticks: { color: c.tick, font: { family: 'DM Sans', size: 11 } }
          },
          y: {
            grid: { color: c.grid, drawBorder: false },
            ticks: { color: c.tick, font: { family: 'DM Sans', size: 11 }, callback: v => v + ' kg' },
            min: 20, max: 36
          }
        }
      }
    });
  }

  function updateChart() {
    const hrs = parseInt(document.getElementById('timeRange').value);
    buildChart(hrs);
  }

  function updateChartTheme() {
    const hrs = parseInt(document.getElementById('timeRange').value);
    buildChart(hrs);
  }

  buildChart();

  // ---- LIVE WEIGHT SIMULATION ----
  let currentWeight = 24.5;
  let updateCount = 0;

  setInterval(() => {
    const delta = (Math.random() - 0.6) * 0.08;
    currentWeight = Math.max(18, Math.min(36, currentWeight + delta));
    const display = currentWeight.toFixed(1);
    document.getElementById('weightVal').textContent = display;
    const fillPct = Math.round((currentWeight / 36) * 100);
    document.getElementById('fillLabel').textContent = `Fill Level (${fillPct}%)`;
    document.getElementById('progressFill').style.width = fillPct + '%';
    updateCount++;
    const mins = updateCount < 2 ? '< 1 minute ago' : `${updateCount} minutes ago`;
    document.getElementById('lastUpdated').textContent = `Last updated: ${mins}`;
  }, 8000);

  // ---- MODAL ----
  function openModal() {
    document.getElementById('modalOverlay').classList.add('open');
    document.getElementById('newWeight').value = '';
  }
  function closeModal() {
    document.getElementById('modalOverlay').classList.remove('open');
  }
  function closeModalOnBg(e) {
    if (e.target === document.getElementById('modalOverlay')) closeModal();
  }

  function addEntry() {
    const w = parseFloat(document.getElementById('newWeight').value);
    if (!w || w <= 0 || w > 36) {
      alert('Please enter a valid weight between 0 and 36 kg.');
      return;
    }
    const status = document.getElementById('newStatus').value;
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const prev = currentWeight;
    const change = (w - prev).toFixed(1);
    const changeStr = (change > 0 ? '+' : '') + change;
    const tbody = document.getElementById('activityTable');
    const row = document.createElement('tr');
    row.style.background = 'rgba(29,53,87,0.04)';
    row.innerHTML = `
      <td class="ts-cell">Today, ${time}</td>
      <td class="weight-cell">${w.toFixed(1)}</td>
      <td class="change-cell">${changeStr}</td>
      <td><span class="stable-badge">${status.charAt(0).toUpperCase() + status.slice(1)}</span></td>
      <td><button class="details-btn" onclick="showDetails('${time}', ${w}, ${change})">Details</button></td>
    `;
    tbody.insertBefore(row, tbody.firstChild);
    setTimeout(() => row.style.background = '', 1200);
    closeModal();
  }

  // ---- DETAILS ----
  function showDetails(time, weight, change) {
    console.log(`[Details] Time: ${time} | Weight: ${weight} kg | Change: ${change} kg`);
    alert(`📊 Reading Details\n\nTime: ${time}\nWeight: ${weight} kg\nChange: ${change > 0 ? '+' : ''}${change} kg\nStatus: Stable\nTank: Main Supply Tank A`);
  }

  // ---- BUTTON ACTIONS ----
  function viewThresholds() {
    alert('📏 Current Thresholds\n\nMin Safe Weight: 5.0 kg\nMax Capacity: 36.0 kg\nWarning Level: 9.0 kg (25%)\nCritical Level: 5.4 kg (15%)\n\nAll parameters normal for H001.');
  }

  function showNotif() {
    alert('🔔 Notifications\n\n✅ All systems operational\n📊 Daily report ready\n🔧 Maintenance scheduled: Jun 12');
  }

  function showHelp() {
    alert('❓ Help & Support\n\nDocumentation: docs.cylindermonitor.io\nSupport: support@cylindermonitor.io\nVersion: 2.4.1\n\nFor emergencies, use the sidebar button.');
  }

  function handleEmergency() {
    if (confirm('⚠️ Emergency Support\n\nThis will alert the on-call engineer immediately.\n\nContinue?')) {
      alert('🚨 Emergency alert sent!\n\nOn-call engineer has been notified.\nEstimated response: 10–15 minutes.\nRef: EMG-' + Math.floor(Math.random()*9000+1000));
    }
  }

  function handleLogout() {
    if (confirm('Log out of the system?')) {
      alert('Logged out. Goodbye, Operator 04.');
    }
  }
