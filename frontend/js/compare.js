let compareLatencyChart = null;
let compareResourcesChart = null;

document.getElementById('btn-add-rule').addEventListener('click', () => {
    const container = document.getElementById('rules-container');
    const div = document.createElement('div');
    div.className = 'flex gap-2';
    div.innerHTML = `
        <input type="text" placeholder="columna" class="rule-col flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
        <select class="rule-alg bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
            <option value="redaccion">Redacción</option>
            <option value="hashing">SHA-256</option>
            <option value="encriptacion">AES/Fernet</option>
            <option value="fpe">FPE</option>
        </select>
    `;
    container.appendChild(div);
});

document.getElementById('btn-compare').addEventListener('click', async () => {
    const dataInput = document.getElementById('input-data').value;
    let data;
    try {
        data = JSON.parse(dataInput);
    } catch (e) {
        alert('JSON inválido en los datos de prueba');
        return;
    }

    const rules = {};
    document.querySelectorAll('#rules-container .flex').forEach(row => {
        const col = row.querySelector('.rule-col')?.value;
        const alg = row.querySelector('.rule-alg')?.value;
        if (col && alg) rules[col] = alg;
    });

    if (Object.keys(rules).length === 0) {
        alert('Agrega al menos una regla de enmascaramiento');
        return;
    }

    const algorithms = [...new Set(Object.values(rules))];
    const results = [];

    for (const alg of algorithms) {
        const algRules = {};
        Object.entries(rules).forEach(([col, a]) => { if (a === alg) algRules[col] = a; });
        try {
            const res = await API.post('/masking/apply', { data, rules: algRules });
            results.push({ algorithm: alg, ...res });
        } catch (e) {
            console.error(`Error con ${alg}:`, e);
        }
    }

    renderComparison(results);
});

function renderComparison(results) {
    destroyChart(compareLatencyChart);
    compareLatencyChart = createBarChart('chart-compare-latency',
        results.map(r => r.algorithm),
        [{
            label: 'Latencia Masking (ms)',
            data: results.map(r => r.masking_latency_ms),
            backgroundColor: results.map(r => ALGO_COLORS[r.algorithm]?.bg || COLORS.blue.bg),
            borderColor: results.map(r => ALGO_COLORS[r.algorithm]?.border || COLORS.blue.border),
            borderWidth: 2,
        }]
    );

    destroyChart(compareResourcesChart);
    compareResourcesChart = createBarChart('chart-compare-resources',
        results.map(r => r.algorithm),
        [
            {
                label: 'CPU %',
                data: results.map(r => r.cpu_percent),
                backgroundColor: COLORS.green.bg,
                borderColor: COLORS.green.border,
                borderWidth: 2,
            },
            {
                label: 'RAM MB',
                data: results.map(r => r.ram_mb),
                backgroundColor: COLORS.cyan.bg,
                borderColor: COLORS.cyan.border,
                borderWidth: 2,
            },
        ]
    );

    const tbody = document.getElementById('compare-table-body');
    const perfLabels = { redaccion: 'Muy rápido', hashing: 'Rápido', encriptacion: 'Moderado', fpe: 'Lento' };
    const revLabels = { redaccion: 'No', hashing: 'No', encriptacion: 'Sí', fpe: 'No' };

    tbody.innerHTML = results.map(r => `
        <tr class="border-b border-gray-800 hover:bg-gray-800/50">
            <td class="py-3 px-4 font-medium text-blue-400">${r.algorithm}</td>
            <td class="py-3 px-4 font-mono">${r.masking_latency_ms?.toFixed(3) || 0}</td>
            <td class="py-3 px-4 font-mono">${r.cpu_percent?.toFixed(2) || 0}</td>
            <td class="py-3 px-4 font-mono">${r.ram_mb?.toFixed(2) || 0}</td>
            <td class="py-3 px-4">${revLabels[r.algorithm] || '-'}</td>
            <td class="py-3 px-4">${perfLabels[r.algorithm] || '-'}</td>
        </tr>
    `).join('');
}
