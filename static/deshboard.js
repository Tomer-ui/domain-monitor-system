// --- Sample data (replace with your API)
const sampleDomains = [
  { domain:"example.com", status:"up", uptime:99.98, ssl:"2025-10-20", issuer:"Let's Encrypt R3", dns:["93.184.216.34"], registrar:"IANA", tags:["prod"] },
  { domain:"desta-interfaces.net", status:"up", uptime:99.91, ssl:"2025-09-25", issuer:"ZeroSSL", dns:["203.0.113.52","203.0.113.53"], registrar:"Namecheap", tags:["prod","edge"] },
  { domain:"lab.local", status:"down", uptime:96.12, ssl:null, issuer:"—", dns:["192.0.2.44"], registrar:"—", tags:["lab"] },
  { domain:"api.domainmonitor.io", status:"up", uptime:99.73, ssl:"2025-09-18", issuer:"DigiCert TLS RSA", dns:["198.51.100.17"], registrar:"Google", tags:["prod","api"] },
  { domain:"staging.domainmonitor.io", status:"up", uptime:98.66, ssl:"2025-11-12", issuer:"Let's Encrypt R3", dns:["198.51.100.77"], registrar:"Cloudflare", tags:["staging"] },
  { domain:"myshop.example", status:"up", uptime:99.22, ssl:"2025-09-29", issuer:"Sectigo", dns:["203.0.113.90"], registrar:"GoDaddy", tags:["prod","ecom"] }
];

// --- Utilities ---
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));
const fmtPct = v => (Math.round(v*100)/100).toFixed(2);
const daysUntil = (iso) => { if(!iso) return null; const d=(new Date(iso)-new Date())/(1000*60*60*24); return Math.floor(d); };

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
  const rows = sampleDomains.filter(r => {
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
  const sslLabel = r.ssl ? `${r.ssl} (${sslDays}d)` : '—';
  const sslClass = r.ssl ? (sslDays<=14 ? 'warn' : 'up') : '';
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
  const row = sampleDomains.find(x=>x.domain===domain);
  if(btn.dataset.action==='view') openDrawer(row);
  if(btn.dataset.action==='refresh') simulateRefresh(btn, row);
});

function openDrawer(row){
  $('#drawerTitle').textContent = row.domain;
  $('#dUptime').textContent = fmtPct(row.uptime)+"%";
  $('#dStatus').textContent = row.status.toUpperCase();
  $('#dSSL').textContent = row.ssl ? `${row.ssl}  (in ${daysUntil(row.ssl)} days)` : '—';
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

$('#addBtn').addEventListener('click', ()=>{
  const d = prompt('Add domain (e.g., mydomain.com)');
  if(!d) return;
  sampleDomains.push({ domain:d, status:'up', uptime:99.9, ssl:null, issuer:'—', dns:['203.0.113.10'], registrar:'—', tags:['new'] });
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
