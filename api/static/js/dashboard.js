let protocolChart = null;
let latencyChart = null;
let allProxies = [];

async function fetchProxies() {
    try {
        const response = await fetch('/api/v1/proxies?limit=1000');
        const data = await response.json();
        allProxies = data.proxies || [];
        return data;
    } catch (error) {
        console.error('Erro ao buscar proxies:', error);
        return { proxies: [], total: 0 };
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/v1/stats');
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar stats:', error);
        return { total_alive: 0, by_protocol: {} };
    }
}

function updateStats(stats, proxies) {
    document.getElementById('totalProxies').textContent = stats.total_alive;
    
    const byProtocol = stats.by_protocol || {};
    document.getElementById('socks5Count').textContent = byProtocol.socks5 || 0;
    document.getElementById('httpCount').textContent = (byProtocol.http || 0) + (byProtocol.https || 0);
    document.getElementById('socks4Count').textContent = byProtocol.socks4 || 0;
}

function updateCharts(proxies) {
    const byProtocol = { socks5: 0, http: 0, socks4: 0 };
    const latencyRanges = { '<100ms': 0, '100-500ms': 0, '>500ms': 0 };
    
    proxies.forEach(p => {
        const proto = p.protocol || 'http';
        if (byProtocol.hasOwnProperty(proto)) {
            byProtocol[proto]++;
        }
        
        const lat = p.latency || 0;
        if (lat < 100) latencyRanges['<100ms']++;
        else if (lat < 500) latencyRanges['100-500ms']++;
        else latencyRanges['>500ms']++;
    });
    
    if (protocolChart) protocolChart.destroy();
    if (latencyChart) latencyChart.destroy();
    
    protocolChart = new Chart(document.getElementById('protocolChart'), {
        type: 'doughnut',
        data: {
            labels: ['SOCKS5', 'HTTP/HTTPS', 'SOCKS4'],
            datasets: [{
                data: [byProtocol.socks5, byProtocol.http, byProtocol.socks4],
                backgroundColor: ['#ff6b6b', '#51cf66', '#ffd43b']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } }
        }
    });
    
    latencyChart = new Chart(document.getElementById('latencyChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(latencyRanges),
            datasets: [{
                label: 'Proxies',
                data: Object.values(latencyRanges),
                backgroundColor: ['#00d9ff', '#ffd43b', '#ff6b6b']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }, x: { ticks: { color: '#fff' }, grid: { display: false } } }
        }
    });
}

function updateTable(proxies) {
    const tbody = document.getElementById('proxiesBody');
    tbody.innerHTML = '';
    
    proxies.forEach(p => {
        const row = document.createElement('tr');
        const lat = p.latency ? `${p.latency}ms` : '--';
        row.innerHTML = `
            <td>${p.ip}</td>
            <td>${p.port}</td>
            <td><span class="protocol-badge ${p.protocol}">${p.protocol.toUpperCase()}</span></td>
            <td>${lat}</td>
            <td>Agora</td>
        `;
        tbody.appendChild(row);
    });
}

function filterProxies() {
    const protocolFilter = document.getElementById('protocolFilter').value;
    const search = document.getElementById('searchProxy').value.toLowerCase();
    
    let filtered = allProxies;
    
    if (protocolFilter) {
        filtered = filtered.filter(p => p.protocol === protocolFilter);
    }
    
    if (search) {
        filtered = filtered.filter(p => p.ip.includes(search));
    }
    
    updateTable(filtered);
}

async function refreshData() {
    const stats = await fetchStats();
    const data = await fetchProxies();
    
    updateStats(stats, data.proxies);
    updateCharts(data.proxies);
    updateTable(data.proxies);
    
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString('pt-BR');
}

document.getElementById('protocolFilter').addEventListener('change', filterProxies);
document.getElementById('searchProxy').addEventListener('input', filterProxies);

setInterval(refreshData, 30000);
refreshData();
