// MODIFICATION: Use backend data passed from the template
// This transforms the data from app.py into the format the frontend expects.
const domainsData = userDomains.map(d => ({
    domain: d.domain,
    // Convert status like "live. status code 200" to "up" or "down"
    status: d.status.startsWith('live') ? 'up' : 'down',
    // Uptime is not in backend data, so we use a placeholder
    uptime: 99.9,
    ssl: d.ssl_expiration,
    issuer: d.ssl_issuer,
    // Tags are not in backend data, placeholder
    tags: []
}));

// --- Utilities ---
const $ = sel => document.querySelector(sel);      
const $$ = sel => Array.from(document.querySelectorAll(sel));
const fmtPct = v => (Math.round(v*100)/100).toFixed(2);
const daysUntil = (iso) => { if(!iso || iso === 'N/A') return null; const d=(new Date(iso)-new Date())/(1000*60*60*24); return Math.floor(d); };

// --- Populate stats ---
function refreshStats(rows){
  const total = rows.length;
  const avg = rows.reduce((a,r)=>a+r.uptime,0)/Math.max(total,1);
  const expSoon = rows.filter(r => { const d = daysUntil(r.ssl); return d !== null && d <= 14; }).length;
  $('#statTotal').textContent = total;
  $('#statUptime').innerHTML = fmtPct(avg)+"<small>%</small>";
  $('#statSSL').textContent = expSoon;
}

// --- Table rendering ---
const tbody = document.querySelector('#domainsTable tbody');
let currentFilter = 'all';
let query = '';

function renderTable(){
  tbody.innerHTML = '';
  // MODIFICATION: Use 'domainsData' instead of 'sampleDomains'
  const rows = domainsData.filter(r => {
    const matchQuery = !query || (r.domain+" "+(r.registrar||'')+" "+(r.tags||[]).join(' ')).toLowerCase().includes(query);
    const matchFilter = (
      currentFilter==='all' ||
      (currentFilter==='up' && r.status==='up') || 
      (currentFilter==='down' && r.status==='down') ||
      (currentFilter==='warn' && (daysUntil(r.ssl) !== null && daysUntil(r.ssl) <= 14)) ||
      (currentFilter.startsWith('tag:') && (r.tags||[]).includes(currentFilter.split(':')[1]))        
    );
    return matchQuery && matchFilter;
  });
  rows.forEach(r => tbody.appendChild(rowEl(r)));  
  refreshStats(rows);
}

function rowEl(r){
  const tr = document.createElement('tr');
  const sslDays = daysUntil(r.ssl);
  let sslLabel, sslClass;

  if (sslDays === null) {
      sslLabel = '—';
      sslClass = '';
  } else {
      sslLabel = `${r.ssl} (${sslDays}d)`;
      sslClass = sslDays <= 14 ? 'warn' : 'up';
  }

  tr.innerHTML = `
    <td>
      <div style="display:flex; align-items:center; gap:10px">
        <i class="fas fa-globe" style="color:${r.status==='up'?'#6ee7b7':'#fca5a5'}"></i>
        <div style="font-weight:700">${r.domain}</div>
      </div>
    </td>
    <td><span class="status ${r.status}"><i class="fas fa-circle"></i>${r.status.toUpperCase()}</span></td>
    <td>${r.issuer || '—'}</td>
    <td><span class="status ${sslClass}">${sslLabel}</span></td>
  `;
  return tr;
}

// --- Drawer logic (optional) ---
const drawer = $('#drawer');
if (drawer) {
  $('#closeDrawer').addEventListener('click', ()=> drawer.classList.remove('open'));
}

tbody.addEventListener('click', (e)=>{
  const btn = e.target.closest('button[data-action]');
  if(!btn) return;
  const domain = btn.dataset.domain;
  // MODIFICATION: Use 'domainsData'
  const row = domainsData.find(x=>x.domain===domain);
  if(btn.dataset.action==='view') openDrawer(row); 
  if(btn.dataset.action==='refresh') simulateRefresh(btn, row);
});

function openDrawer(row){
  $('#drawerTitle').textContent = row.domain;
  $('#dUptime').textContent = fmtPct(row.uptime)+"%";
  $('#dStatus').textContent = row.status.toUpperCase();
  $('#dSSL').textContent = row.ssl && row.ssl !== 'N/A' ? `${row.ssl}  (in ${daysUntil(row.ssl)} days)` : '—';
  $('#dIssuer').textContent = row.issuer || '—'; 
  $('#dDNS').textContent = (row.dns||[]).join(', ');
  const checks = [
    {t:'HTTP 200', when:'2m ago'},
    {t:'SSL valid', when:'2m ago'},
    {t:'DNS A resolves', when:'2m ago'},
  ];
  const ul = $('#dChecks');
  ul.innerHTML = '';
  checks.forEach(c=>{
    const li = document.createElement('li');       
    li.innerHTML = `<div style="display:flex; justify-content:space-between; background:var(--card); border:1px solid var(--border); border-radius:10px; padding:10px"><span>${c.t}</span><span style="color:var(--muted)">${c.when}</span></div>`;
    ul.appendChild(li);
  })
  drawer.classList.add('open');
}

// --- Toolbar interactions ---
$$('.chip').forEach(chip=> chip.addEventListener('click', ()=>{
  $$('.chip').forEach(c=>c.classList.remove('active'));
  chip.classList.add('active');
  currentFilter = chip.dataset.filter;
  renderTable();
}));

$('#searchInput').addEventListener('input', (e)=>{ query = e.target.value.trim().toLowerCase(); renderTable(); });

// NOTE: This "Add Domain" button only adds to the frontend view.
// For a persistent add, it should be a form that POSTs to your '/add_domain' route.
$('#addBtn').addEventListener('click', ()=>{       
  const d = prompt('Add domain (e.g., mydomain.com)');
  if(!d) return;
  // MODIFICATION: Use 'domainsData'
  domainsData.push({ domain:d, status:'up', uptime:99.9, ssl:'N/A', issuer:'—', dns:[], tags:['new'] });
  renderTable();
});

// --- Theme + RTL toggles ---
const darkBtn = $('#darkBtn');
const rtlBtn = $('#rtlBtn');
let dark = true; let rtl = false;

darkBtn.addEventListener('click', ()=>{
  dark = !dark;
  document.body.style.background = dark ? 'linear-gradient(180deg,#070b18 0%, #0b1020 100%)' : '#f6f7fb';
  document.querySelectorAll('.card, .sidebar, header').forEach(el=> el.style.background = dark ? '' : '#fff');
});

rtlBtn.addEventListener('click', ()=>{ rtl = !rtl; document.documentElement.setAttribute('dir', rtl ? 'rtl' : 'ltr'); });

// --- Chart (optional) ---
const ctx = document.getElementById('uptimeChart');
if (ctx && window.Chart) {
  const labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const dataPoints = [99.96, 99.99, 99.87, 99.92, 99.99, 99.80, 99.95];
  new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ label: 'Fleet Uptime % (last 7d)', data: dataPoints, tension:.35, fill:false }]},
    options: { responsive:true, scales:{ y:{ suggestedMin: 99.5, max:100, ticks:{ callback:(v)=> v+"%" } } }, plugins:{ legend:{ labels:{ color: getComputedStyle(document.documentElement).getPropertyValue('--text') } } } }
  });
}

// --- Simulate a refresh ---
function simulateRefresh(btn, row){
  const old = btn.innerHTML; btn.disabled=true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
  setTimeout(()=>{ row.uptime = Math.max(96, Math.min(99.99, row.uptime + (Math.random()-.5)*0.2)); renderTable(); btn.disabled=false; btn.innerHTML = old; }, 800);
}

// --- Init ---
(function init(){
  const yearEl = document.getElementById('year');  
  if (yearEl) yearEl.textContent = new Date().getFullYear();
  renderTable();
})();