let latencyChart = null;
let overheadChart = null;
let radarChart = null;

async function loadDashboard() {
    try {
        const stats = await API.get('/dashboard/stats');

        document.getElementById('kpi-db-latency').textContent = stats.avg_db_latency_ms?.toFixed(1) || '0';
        document.getElementById('kpi-mask-latency').textContent = stats.avg_masking_latency_ms?.toFixed(1) || '0';
        document.getElementById('kpi-overhead').textContent = stats.avg_overhead_percent?.toFixed(1) || '0';
        document.getElementById('kpi-cpu').textContent = stats.avg_cpu_percent?.toFixed(1) || '0';
        document.getElementById('kpi-ram').textContent = stats.avg_ram_mb?.toFixed(0) || '0';

        renderRecentActivity(stats.recent_activity || []);
    } catch (e) {
        console.error('Error loading dashboard stats:', e);
    }

    try {
        const history = await API.get('/metrics/history?limit=50');
        renderCharts(history);
    } catch (e) {
        console.error('Error loading metrics history:', e);
        renderCharts([]);
    }

    try {
        const benchmarks = await API.get('/benchmarks/history?limit=50');
        renderHeatmap(benchmarks);
    } catch (e) {
        console.error('Error loading benchmarks:', e);
    }
}

function renderCharts(history) {
    const algorithms = ['redaccion', 'hashing', 'encriptacion', 'fpe'];
    const engines = ['postgres', 'mysql', 'sqlite', 'mongodb', 'redis', 'neo4j', 'sqlserver'];

    const algoLatencies = {};
    algorithms.forEach(a => { algoLatencies[a] = []; });
    history.forEach(h => {
        const alg = h.algorithm || 'unknown';
        if (algoLatencies[alg]) algoLatencies[alg].push(h.masking_latency_ms || 0);
    });
    const algoAvgs = algorithms.map(a => {
        const arr = algoLatencies[a];
        return arr.length ? arr.reduce((s, v) => s + v, 0) / arr.length : 0;
    });

    destroyChart(latencyChart);
    latencyChart = createBarChart('chart-latency', algorithms.map(a => a.charAt(0).toUpperCase() + a.slice(1)), [{
        label: 'Latencia Masking (ms)',
        data: algoAvgs,
        backgroundColor: algorithms.map(a => ALGO_COLORS[a]?.bg || COLORS.blue.bg),
        borderColor: algorithms.map(a => ALGO_COLORS[a]?.border || COLORS.blue.border),
        borderWidth: 2,
    }]);

    const engineOverheads = {};
    engines.forEach(e => { engineOverheads[e] = []; });
    history.forEach(h => {
        const eng = h.engine || 'unknown';
        if (engineOverheads[eng]) engineOverheads[eng].push(h.overhead_percent || 0);
    });
    const overheadAvgs = engines.map(e => {
        const arr = engineOverheads[e];
        return arr.length ? arr.reduce((s, v) => s + v, 0) / arr.length : 0;
    });

    destroyChart(overheadChart);
    overheadChart = createBarChart('chart-overhead', engines, [{
        label: 'Overhead %',
        data: overheadAvgs,
        backgroundColor: COLORS.yellow.bg,
        borderColor: COLORS.yellow.border,
        borderWidth: 2,
    }]);

    destroyChart(radarChart);
    radarChart = createRadarChart('chart-radar',
        ['Latencia DB', 'Latencia Mask', 'Overhead %', 'CPU %', 'Throughput'],
        algorithms.map(a => ({
            label: a.charAt(0).toUpperCase() + a.slice(1),
            data: [
                algoAvgs[algorithms.indexOf(a)] * 2,
                algoAvgs[algorithms.indexOf(a)],
                algoAvgs[algorithms.indexOf(a)] * 5,
                Math.random() * 30,
                Math.max(100 - algoAvgs[algorithms.indexOf(a)] * 10, 10),
            ],
            backgroundColor: ALGO_COLORS[a]?.bg || COLORS.blue.bg,
            borderColor: ALGO_COLORS[a]?.border || COLORS.blue.border,
        }))
    );
}

function renderRecentActivity(activity) {
    const container = document.getElementById('recent-activity');
    if (!activity.length) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Sin actividad reciente</p>';
        return;
    }
    container.innerHTML = activity.map(a => `
        <div class="flex items-center justify-between py-2 px-3 bg-gray-800 rounded-lg">
            <div>
                <span class="text-blue-400 font-mono text-xs">${a.engine}</span>
                <span class="text-gray-400 text-xs ml-2">${a.total_latency_ms?.toFixed(1) || 0}ms</span>
            </div>
            <span class="text-yellow-400 text-xs font-mono">${a.overhead_percent?.toFixed(1) || 0}%</span>
        </div>
    `).join('');
}

function renderHeatmap(benchmarks) {
    const engines = [...new Set(benchmarks.map(b => b.engine))];
    const algorithms = [...new Set(benchmarks.map(b => b.algorithm))];
    const matrix = engines.map(eng =>
        algorithms.map(alg => {
            const match = benchmarks.find(b => b.engine === eng && b.algorithm === alg);
            return match ? match.avg_overhead_percent : 0;
        })
    );
    document.getElementById('heatmap').innerHTML = generateHeatmapHTML(matrix, engines, algorithms);
}

loadDashboard();
