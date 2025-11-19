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

    // --- Elements ---
    const stationSelect = document.getElementById('station-select');
    const timeSelect = document.getElementById('time-select');
    const queueContainer = document.getElementById('queue-container');
    const craftsTableBody = document.querySelector('#crafts-table tbody');
    const topProfitList = document.getElementById('top-profit-list');
    const totalTimeEl = document.getElementById('total-time');
    const totalProfitEl = document.getElementById('total-profit');

    // Barter Elements
    const bartersTableBody = document.querySelector('#barters-table tbody');
    const showFlippableCheckbox = document.getElementById('show-flippable-only');

    // Settings Elements
    const settingsContainer = document.getElementById('settings-container');
    const saveSettingsBtn = document.getElementById('save-settings-btn');

    // Navigation
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- State ---
    let userSettings = JSON.parse(localStorage.getItem('tarkovSettings')) || {};

    // --- Initialization ---

    // 1. Setup Navigation
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // 2. Populate Stations (Crafts)
    const stations = Object.keys(data.schedules).sort();
    stations.forEach(station => {
        const option = document.createElement('option');
        option.value = station;
        option.textContent = station;
        if (station === 'Workbench') option.selected = true;
        stationSelect.appendChild(option);
    });

    // 3. Render Functions
    const renderQueue = () => {
        const station = stationSelect.value;
        const timeKey = timeSelect.value;

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

    const renderCraftsTable = () => {
        const crafts = data.crafts;
        craftsTableBody.innerHTML = '';

        // Filter based on settings (TODO: Implement full filtering logic)
        // For now, show top 100
        crafts.slice(0, 100).forEach(craft => {
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

    const renderBartersTable = () => {
        let barters = data.barters || [];

        if (showFlippableCheckbox.checked) {
            barters = barters.filter(b => b.flip_profit > 0);
            // Sort by flip profit if filtering for it
            barters.sort((a, b) => b.flip_profit - a.flip_profit);
        } else {
            // Default sort by savings
            barters.sort((a, b) => b.savings - a.savings);
        }

        bartersTableBody.innerHTML = '';

        // Limit to 100 for performance
        barters.slice(0, 100).forEach(barter => {
            const row = document.createElement('tr');

            const savingsClass = barter.savings > 0 ? 'positive' : 'negative';
            const flipClass = barter.flip_profit > 0 ? 'positive' : 'text-muted';

            // Format ingredients tooltip
            const ingredientsList = barter.ingredients.map(i => `${i.count}x ${i.name}`).join(', ');

            row.innerHTML = `
                <td title="${ingredientsList}">${barter.reward_name}</td>
                <td>${barter.trader} (LL${barter.level})</td>
                <td class="money">${formatMoney(barter.cost)}</td>
                <td class="money">${formatMoney(barter.flea_value)}</td>
                <td class="money profit-cell" style="color: var(--${savingsClass})">${formatMoney(barter.savings)}</td>
                <td class="money">${formatMoney(barter.flea_value + barter.flip_profit - barter.savings)}</td> <!-- Trader Sell Price approx -->
                <td class="money profit-cell" style="color: var(--${flipClass})">${formatMoney(barter.flip_profit)}</td>
            `;
            bartersTableBody.appendChild(row);
        });
    };

    const renderSettings = () => {
        // Generate settings UI based on available stations
        // This is a placeholder for the robust settings implementation
        settingsContainer.innerHTML = '';

        stations.forEach(station => {
            const div = document.createElement('div');
            div.className = 'station-config';
            div.innerHTML = `<h3>${station}</h3>`;

            [1, 2, 3].forEach(lvl => {
                const label = document.createElement('label');
                const isChecked = userSettings[`${station}_${lvl}`] !== false; // Default true
                label.innerHTML = `
                    <input type="checkbox" ${isChecked ? 'checked' : ''} data-key="${station}_${lvl}">
                    Level ${lvl}
                `;
                div.appendChild(label);
            });

            settingsContainer.appendChild(div);
        });
    };

    // 4. Event Listeners
    stationSelect.addEventListener('change', renderQueue);
    timeSelect.addEventListener('change', renderQueue);
    showFlippableCheckbox.addEventListener('change', renderBartersTable);

    saveSettingsBtn.addEventListener('click', () => {
        const checkboxes = settingsContainer.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            userSettings[cb.dataset.key] = cb.checked;
        });
        localStorage.setItem('tarkovSettings', JSON.stringify(userSettings));
        alert('Settings Saved! (Filtering logic coming soon)');
    });

    // 5. Initial Render
    renderQueue();
    renderCraftsTable();
    renderTopList();
    renderBartersTable();
    renderSettings();
});
