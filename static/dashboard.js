// Global variables to hold the application state
let domainsData = []; 
const tbody = document.querySelector('#domainsTable tbody');
let currentFilter = 'all';
let query = '';

// Utility functions for selecting elements and calculating dates
const $ = sel => document.querySelector(sel);      
const $$ = sel => Array.from(document.querySelectorAll(sel));
const daysUntil = (iso) => { 
    if(!iso || typeof iso !== 'string' || !iso.match(/^\d{4}-\d{2}-\d{2}$/)) return null; 
    const d = (new Date(iso) - new Date()) / (1000 * 60 * 60 * 24); 
    return Math.floor(d); 
};

// =================================================================
// API Functions
// =================================================================

async function fetchDomains() {
    try {
        const response = await fetch('/api/domains');
        if (!response.ok) {
            // If session expired or is invalid, redirect to login page
            if (response.status === 401) window.location.href = '/login';
            throw new Error('Failed to fetch domains');
        }
        const data = await response.json();
        // Transform the raw API data into the format the frontend uses
        domainsData = data.map(d => ({
            domain: d.domain,
            status: d.status.startsWith('Live') ? 'up' : 'down',
            ssl: d.ssl_expiration,
            issuer: d.ssl_issuer,
        }));
        renderTable();
    } catch (error) {
        console.error("Error fetching domains:", error);
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--danger);">Could not load domain data.</td></tr>`;
    }
}

async function removeDomain(domain) {
    if (!confirm(`Are you sure you want to remove ${domain}?`)) return;
    try {
        const response = await fetch('/api/remove_domain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain })
        });
        const result = await response.json();
        if (response.ok) {
            fetchDomains(); // Refresh the table on success
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error("Failed to remove domain:", error);
        alert("An error occurred while removing the domain.");
    }
}

// =================================================================
// Table and UI Rendering
// =================================================================

function renderTable(){
    tbody.innerHTML = '';
    // Filter the global data based on current search query and filter chips
    const rows = domainsData.filter(r => {
        const matchQuery = !query || (r.domain).toLowerCase().includes(query);
        const matchFilter = (
            currentFilter === 'all' ||
            (currentFilter === 'up' && r.status === 'up') || 
            (currentFilter === 'down' && r.status === 'down') ||
            (currentFilter === 'warn' && (daysUntil(r.ssl) !== null && daysUntil(r.ssl) <= 14))
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
      // If days can't be calculated, it's likely an error message from the backend
      sslLabel = r.ssl; 
      sslClass = 'down';
    } else {
      sslLabel = `${r.ssl} (${sslDays}d)`;
      sslClass = sslDays <= 14 ? 'warn' : 'up';
    }
    
    // Provide clearer text if the issuer couldn't be fetched due to an error
    const issuerDisplay = r.issuer === 'N/A' && sslClass === 'down' ? 'Check Failed' : r.issuer;

    tr.innerHTML = `
      <td>
        <div style="display:flex; align-items:center; gap:10px">
          <i class="fas fa-globe" style="color:${r.status==='up'?'#6ee7b7':'#fca5a5'}"></i>
          <div style="font-weight:700">${r.domain}</div>
        </div>
      </td>
      <td><span class="status ${r.status}"><i class="fas fa-circle"></i>${r.status.toUpperCase()}</span></td>
      <td>${issuerDisplay}</td>
      <td><span class="status ${sslClass}">${sslLabel}</span></td>
      <td><button class="btn secondary sm remove-btn" data-domain="${r.domain}"><i class="fas fa-trash"></i> Remove</button></td>
    `;
    return tr;
}

function refreshStats(rows){
  const total = rows.length;
  $('#statTotal').textContent = total;
}

// =================================================================
// Event Listeners Setup
// =================================================================

function setupEventListeners() {
    $('#searchInput').addEventListener('input', (e) => {
        query = e.target.value.trim().toLowerCase();
        renderTable();
    });

    $('#logoutBtn').addEventListener('click', async () => {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    });

    $('#addDomainForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = e.target.elements.domain;
        const domain = input.value.trim();
        if (!domain) return;
        
        try {
            const response = await fetch('/api/add_domain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ domain })
            });
            const result = await response.json();
            if (response.ok) {
                input.value = ''; // Clear input on success
                fetchDomains(); // Refresh table with new domain
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Failed to add domain:", error);
            alert("An error occurred while adding the domain.");
        }
    });

    $('#bulkBtn').addEventListener('click', () => $('#fileInput').click());
    $('#fileInput').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/bulk_upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            alert(result.message);
            if(response.ok) fetchDomains();
        } catch (error) {
            console.error("Bulk upload failed:", error);
            alert("An error occurred during bulk upload.");
        } finally {
            e.target.value = null; // Reset file input
        }
    });

    // Use event delegation for remove buttons inside the table body
    tbody.addEventListener('click', (e) => {
        const removeButton = e.target.closest('.remove-btn');
        if (removeButton) {
            removeDomain(removeButton.dataset.domain);
        }
    });
}

// =================================================================
// Initializer
// =================================================================

(function init(){
  fetchDomains(); // Load initial data as soon as the page loads
  setupEventListeners(); // Activate all the interactive elements
})();