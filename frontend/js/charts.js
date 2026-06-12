const COLORS = {
    blue: { bg: 'rgba(59, 130, 246, 0.2)', border: 'rgba(59, 130, 246, 1)' },
    purple: { bg: 'rgba(168, 85, 247, 0.2)', border: 'rgba(168, 85, 247, 1)' },
    yellow: { bg: 'rgba(234, 179, 8, 0.2)', border: 'rgba(234, 179, 8, 1)' },
    green: { bg: 'rgba(34, 197, 94, 0.2)', border: 'rgba(34, 197, 94, 1)' },
    red: { bg: 'rgba(239, 68, 68, 0.2)', border: 'rgba(239, 68, 68, 1)' },
    cyan: { bg: 'rgba(6, 182, 212, 0.2)', border: 'rgba(6, 182, 212, 1)' },
    orange: { bg: 'rgba(249, 115, 22, 0.2)', border: 'rgba(249, 115, 22, 1)' },
};

const ALGO_COLORS = {
    redaccion: COLORS.blue,
    hashing: COLORS.purple,
    encriptacion: COLORS.yellow,
    fpe: COLORS.red,
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#9ca3af', font: { family: 'Inter' } } },
    },
    scales: {
        x: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(55, 65, 81, 0.5)' } },
        y: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(55, 65, 81, 0.5)' } },
    },
};

function createBarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: { ...CHART_DEFAULTS, plugins: { ...CHART_DEFAULTS.plugins } },
    });
}

function createLineChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: { ...CHART_DEFAULTS, elements: { line: { tension: 0.3 } } },
    });
}

function createRadarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'radar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#9ca3af' } } },
            scales: {
                r: {
                    ticks: { color: '#6b7280', backdropColor: 'transparent' },
                    grid: { color: 'rgba(55, 65, 81, 0.5)' },
                    pointLabels: { color: '#9ca3af' },
                },
            },
        },
    });
}

function destroyChart(chartInstance) {
    if (chartInstance) chartInstance.destroy();
}

function generateHeatmapHTML(data, rowLabels, colLabels, title) {
    let html = '<table class="w-full text-xs"><thead><tr><th class="p-2 text-gray-400"></th>';
    colLabels.forEach(col => { html += `<th class="p-2 text-gray-400 font-medium">${col}</th>`; });
    html += '</tr></thead><tbody>';

    rowLabels.forEach((row, ri) => {
        html += `<tr><td class="p-2 text-gray-400 font-medium">${row}</td>`;
        colLabels.forEach((col, ci) => {
            const val = data[ri]?.[ci] || 0;
            const intensity = Math.min(val / 100, 1);
            const r = Math.round(59 + intensity * 180);
            const g = Math.round(130 - intensity * 100);
            const b = Math.round(246 - intensity * 200);
            html += `<td class="p-2 text-center font-mono" style="background:rgba(${r},${g},${b},0.3);color:rgb(${r},${g},${b})">${val.toFixed(1)}%</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}
