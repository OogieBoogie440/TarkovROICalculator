// Format currency
const formatMoney = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'RUB',
        maximumFractionDigits: 0
    }).format(amount).replace('RUB', '₽');
};

// Format time
const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
};

document.addEventListener('DOMContentLoaded', () => {
    const data = window.dashboardData;
    
    if (!data) {
        console.error("No dashboard data found!");
        return;
    }

    const stationSelect = document.getElementById('station-select');
    const timeSelect = document.getElementById('time-select');
    const queueContainer = document.getElementById('queue-container');
    const craftsTableBody = document.querySelector('#crafts-table tbody');
    const topProfitList = document.getElementById('top-profit-list');
    const totalTimeEl = document.getElementById('total-time');
    const totalProfitEl = document.getElementById('total-profit');

    // 1. Populate Stations
    const stations = Object.keys(data.schedules).sort();
    stations.forEach(station => {
        const option = document.createElement('option');
        option.value = station;
        option.textContent = station;
        if (station === 'Workbench') option.selected = true; // Default
        stationSelect.appendChild(option);
    });

    // 2. Render Functions
    const renderQueue = () => {
        const station = stationSelect.value;
        const timeKey = timeSelect.value; // '2h', '4h', '8h'
        
        const queue = data.schedules[station][timeKey];
        queueContainer.innerHTML = '';
        
        let totalProfit = 0;
        let totalSeconds = 0;

        if (!queue || queue.length === 0) {
            queueContainer.innerHTML = '<div class="empty-state">No profitable crafts found for this duration.</div>';
            totalTimeEl.textContent = '0h 0m';
            totalProfitEl.textContent = formatMoney(0);
            return;
        }

        queue.forEach((craft, index) => {
            totalProfit += craft.profit;
            totalSeconds += craft.duration;

            const item = document.createElement('div');
            item.className = `queue-item ${craft.duration > 14400 ? 'long-craft' : ''}`;
            item.innerHTML = `
                <span class="name" title="${craft.reward_name}">${craft.reward_name}</span>
                <span class="time"><i class="far fa-clock"></i> ${formatTime(craft.duration)}</span>
                <span class="profit">${formatMoney(craft.profit)}</span>
            `;
            queueContainer.appendChild(item);

            if (index < queue.length - 1) {
                const arrow = document.createElement('div');
                arrow.className = 'arrow';
                arrow.innerHTML = '→';
                queueContainer.appendChild(arrow);
            }
        });

        totalTimeEl.textContent = formatTime(totalSeconds);
        totalProfitEl.textContent = formatMoney(totalProfit);
        
        if (totalProfit > 0) {
            totalProfitEl.className = 'value positive';
        } else {
            totalProfitEl.className = 'value negative';
        }
    };

    const renderTable = () => {
        const crafts = data.crafts;
        craftsTableBody.innerHTML = '';
        
        // Show top 50 to avoid lag
        crafts.slice(0, 50).forEach(craft => {
            const row = document.createElement('tr');
            const profitClass = craft.profit > 0 ? 'positive' : 'negative';
            
            row.innerHTML = `
                <td>${craft.reward_name}</td>
                <td>${craft.station} (Lvl ${craft.level})</td>
                <td>${formatTime(craft.duration)}</td>
                <td class="money">${formatMoney(craft.cost)}</td>
                <td class="money">${formatMoney(craft.revenue)}</td>
                <td class="money profit-cell" style="color: var(--${profitClass})">${formatMoney(craft.profit)}</td>
                <td class="money" style="color: var(--${profitClass})">${formatMoney(craft.profit_per_hour)}/hr</td>
            `;
            craftsTableBody.appendChild(row);
        });
    };

    const renderTopList = () => {
        const top5 = data.crafts.slice(0, 5);
        topProfitList.innerHTML = '';
        top5.forEach(craft => {
            const div = document.createElement('div');
            div.className = 'top-item';
            div.innerHTML = `
                <span>${craft.reward_name}</span>
                <span>${formatMoney(craft.profit_per_hour)}/hr</span>
            `;
            topProfitList.appendChild(div);
        });
    };

    // 3. Event Listeners
    stationSelect.addEventListener('change', renderQueue);
    timeSelect.addEventListener('change', renderQueue);

    // 4. Initial Render
    renderQueue();
    renderTable();
    renderTopList();
});
