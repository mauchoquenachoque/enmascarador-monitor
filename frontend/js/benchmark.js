let benchLatencyChart = null;
let benchPercentilesChart = null;

document.getElementById('btn-run-bench').addEventListener('click', async () => {
    const engine = document.getElementById('bench-engine').value;
    const table = document.getElementById('bench-table').value;
    const iterations = parseInt(document.getElementById('bench-iters').value) || 10;
    const algorithms = [...document.querySelectorAll('.bench-alg:checked')].map(cb => cb.value);

    if (!table) {
        alert('Ingresa el nombre de la tabla/colección');
        return;
    }
    if (!algorithms.length) {
        alert('Selecciona al menos un algoritmo');
        return;
    }

    const progressDiv = document.getElementById('bench-progress');
    const resultsDiv = document.getElementById('bench-results');
    const progressBar = document.getElementById('progress-bar');

    progressDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    progressBar.style.width = '10%';

    try {
        const connectionId = await getOrCreateConnection(engine, table);
        progressBar.style.width = '30%';

        const data = await API.post('/benchmarks/run', {
            connection_id: connectionId,
            table: table,
            algorithms: algorithms,
            iterations: iterations,
        });

        progressBar.style.width = '100%';
        setTimeout(() => {
            progressDiv.classList.add('hidden');
            resultsDiv.classList.remove('hidden');
            renderBenchmarkResults(data);
        }, 500);
    } catch (e) {
        progressDiv.classList.add('hidden');
        alert('Error ejecutando benchmark: ' + e.message);
    }
});

async function getOrCreateConnection(engine, table) {
    try {
        const connections = await API.get('/databases/engines');
        const testResult = await API.post('/databases/test', {
            engine: engine,
            credentials: getDefaultCredentials(engine),
        });
        if (testResult.success) {
            return engine + '-default';
        }
    } catch (e) {
        console.warn('Using mock connection:', e);
    }
    return engine + '-local';
}

function getDefaultCredentials(engine) {
    const creds = {
        postgres: { host: 'localhost', port: 5432, user: 'postgres', password: 'postgres', database: 'postgres' },
        mysql: { host: 'localhost', port: 3306, user: 'root', password: 'root', database: 'mysql' },
        sqlite: { database: 'local_monitor.db' },
        mongodb: { host: 'mongodb://localhost:27017/', database: 'admin' },
        redis: { host: 'localhost', port: 6379, database: 0 },
        neo4j: { host: 'bolt://localhost:7687', user: 'neo4j', password: 'password' },
        sqlserver: { host: 'localhost', port: 1433, user: 'sa', password: 'StrongPassword123!', database: 'master' },
    };
    return creds[engine] || {};
}

function renderBenchmarkResults(data) {
    const summary = data.summary || [];

    destroyChart(benchLatencyChart);
    benchLatencyChart = createBarChart('chart-bench-latency',
        summary.map(s => s.algorithm),
        [
            {
                label: 'DB Latency (ms)',
                data: summary.map(s => s.avg_db_latency_ms),
                backgroundColor: COLORS.blue.bg,
                borderColor: COLORS.blue.border,
                borderWidth: 2,
            },
            {
                label: 'Masking Latency (ms)',
                data: summary.map(s => s.avg_masking_latency_ms),
                backgroundColor: COLORS.purple.bg,
                borderColor: COLORS.purple.border,
                borderWidth: 2,
            },
        ]
    );

    destroyChart(benchPercentilesChart);
    benchPercentilesChart = createBarChart('chart-bench-percentiles',
        summary.map(s => s.algorithm),
        [
            { label: 'P50 (ms)', data: summary.map(s => s.p50_ms), backgroundColor: COLORS.green.bg, borderColor: COLORS.green.border, borderWidth: 2 },
            { label: 'P95 (ms)', data: summary.map(s => s.p95_ms), backgroundColor: COLORS.yellow.bg, borderColor: COLORS.yellow.border, borderWidth: 2 },
            { label: 'P99 (ms)', data: summary.map(s => s.p99_ms), backgroundColor: COLORS.red.bg, borderColor: COLORS.red.border, borderWidth: 2 },
        ]
    );

    const tbody = document.getElementById('bench-table-body');
    tbody.innerHTML = summary.map(s => `
        <tr class="border-b border-gray-800 hover:bg-gray-800/50">
            <td class="py-3 px-4 font-medium text-blue-400">${s.algorithm}</td>
            <td class="py-3 px-4 font-mono">${s.avg_db_latency_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono">${s.avg_masking_latency_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono">${s.avg_total_latency_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono text-yellow-400">${s.avg_overhead_percent?.toFixed(2)}%</td>
            <td class="py-3 px-4 font-mono">${s.p50_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono">${s.p95_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono">${s.p99_ms?.toFixed(3)}</td>
            <td class="py-3 px-4 font-mono text-green-400">${s.throughput_qps?.toFixed(1)}</td>
        </tr>
    `).join('');
}
