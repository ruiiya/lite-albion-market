// Main JavaScript for Albion Online Market Analyzer

// Wait for the page to load
document.addEventListener('DOMContentLoaded', async () => {
    // Create placeholder image for failed item loads
    createItemPlaceholder();
    
    try {
        // Load locations into dropdown
        const locations = await eel.get_locations()();
        populateLocations(locations);
        
        // Load current filter settings
        await loadCurrentFilters();
    } catch (error) {
        showNotification(`Error initializing: ${error}`, 'error');
    }
});

// Sort state to keep track of which column is sorted and in which direction
const sortState = {
    column: null,
    ascending: true
};

// Create a placeholder image in the DOM
function createItemPlaceholder() {
    // Create a small canvas element to generate a simple placeholder
    const canvas = document.createElement('canvas');
    canvas.width = 40;
    canvas.height = 40;
    const ctx = canvas.getContext('2d');
    
    // Draw background
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, 40, 40);
    
    // Draw question mark
    ctx.fillStyle = '#aaa';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('?', 20, 20);
    
    // Draw border
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, 40, 40);
    
    // Create image element
    const img = new Image();
    img.src = canvas.toDataURL('image/png');
    
    // Add it to DOM but hidden
    img.style.display = 'none';
    img.id = 'item-placeholder';
    document.body.appendChild(img);
}

// Populate locations dropdown
function populateLocations(locations) {
    const select = document.getElementById('locationSelect');
    select.innerHTML = '';
    
    // Sort locations alphabetically
    const sortedLocations = Object.entries(locations).sort((a, b) => {
        // Ensure BlackMarket is at the top
        if (a[1] === 'BlackMarket') return -1;
        if (b[1] === 'BlackMarket') return 1;
        return a[1].localeCompare(b[1]);
    });
    
    sortedLocations.forEach(([short, full]) => {
        const option = document.createElement('option');
        option.value = short;
        option.textContent = `${full} (${short})`;
        select.appendChild(option);
    });
}

// Load current filter settings
async function loadCurrentFilters() {
    try {
        const filters = await eel.get_current_filters()();
        document.getElementById('tierFilter').value = filters.tier;
        document.getElementById('qualityFilter').value = filters.quality;
        document.getElementById('diffFilter').value = filters.diff;
        
        document.getElementById('currentFilters').innerHTML = `
            <p>Current filters:</p>
            <ul>
                <li>Tier: ${filters.tier || 'None'}</li>
                <li>Quality: ${filters.quality || 'None'}</li>
                <li>Minimum Price Difference: ${filters.diff}</li>
            </ul>
        `;
    } catch (error) {
        showNotification(`Error loading filters: ${error}`, 'error');
    }
}

// Set tier filter
async function setTierFilter() {
    const tierFilter = document.getElementById('tierFilter').value;
    try {
        const result = await eel.set_tier_filter(tierFilter)();
        if (result.success) {
            showNotification(result.message, 'success');
            await loadCurrentFilters();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error setting tier filter: ${error}`, 'error');
    }
}

// Set quality filter
async function setQualityFilter() {
    const qualityFilter = document.getElementById('qualityFilter').value;
    try {
        const result = await eel.set_quality_filter(qualityFilter)();
        if (result.success) {
            showNotification(result.message, 'success');
            await loadCurrentFilters();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error setting quality filter: ${error}`, 'error');
    }
}

// Set diff filter
async function setDiffFilter() {
    const diffFilter = document.getElementById('diffFilter').value;
    try {
        const result = await eel.set_diff_filter(diffFilter)();
        if (result.success) {
            showNotification(result.message, 'success');
            await loadCurrentFilters();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error setting difference filter: ${error}`, 'error');
    }
}

// Get market data for a location
async function getMarketData() {
    const location = document.getElementById('locationSelect').value;
    if (!location) {
        showNotification('Please select a location first', 'error');
        return;
    }
    
    try {
        showNotification('Loading market data...', 'success');
        const result = await eel.get_market_data(location)();
        if (result.success) {
            displayMarketData(result.data);
            showTab('marketDataTab');
        } else {
            document.getElementById('marketDataContainer').innerHTML = `<p class="empty-message">${result.message}</p>`;
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error getting market data: ${error}`, 'error');
    }
}

// Get item image URL from the Albion Online Render API
function getItemImageUrl(itemId, quality = 1) {
    // Handle enchantments - they're shown in itemId as T4_SOMETHING@1
    let identifier = itemId;
    let enchantment = 0;
    
    if (itemId.includes('@')) {
        const parts = itemId.split('@');
        identifier = parts[0];
        enchantment = parseInt(parts[1]);
    }
    
    return `https://render.albiononline.com/v1/item/${identifier}.png?quality=${quality}`;
}

// Display market data in a table
function displayMarketData(data) {
    if (data.length === 0) {
        document.getElementById('marketDataContainer').innerHTML = '<p class="empty-message">No data available for this location</p>';
        return;
    }
    
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['Image', 'Item Name', 'Enchantment', 'Quality', 'Sell Price (Min)', 'Buy Price (Max)'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        
        // Don't add sorting to the Image column
        if (index > 0) {
            th.classList.add('sortable');
            th.addEventListener('click', () => sortTable('marketDataContainer', index, headerText));
        }
        
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add item image
        const imgCell = document.createElement('td');
        const img = document.createElement('img');
        img.src = getItemImageUrl(item.id, item.quality);
        img.alt = item.name;
        img.classList.add('item-image');
        img.width = 40;
        img.height = 40;
        img.onerror = function() {
            this.src = document.getElementById('item-placeholder').src;
        };
        imgCell.appendChild(img);
        row.appendChild(imgCell);
        
        const idCell = document.createElement('td');
        idCell.textContent = item.name;
        row.appendChild(idCell);
        
        const enchantCell = document.createElement('td');
        enchantCell.textContent = item.enchant;
        row.appendChild(enchantCell);
        
        const qualityCell = document.createElement('td');
        qualityCell.textContent = getQualityName(item.quality);
        row.appendChild(qualityCell);
        
        const sellMinCell = document.createElement('td');
        sellMinCell.textContent = item.sell_min ? formatPrice(item.sell_min) : 'N/A';
        row.appendChild(sellMinCell);
        
        const buyMaxCell = document.createElement('td');
        buyMaxCell.textContent = item.buy_max ? formatPrice(item.buy_max) : 'N/A';
        row.appendChild(buyMaxCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    document.getElementById('marketDataContainer').innerHTML = '';
    document.getElementById('marketDataContainer').appendChild(table);
}

// Display quick sell opportunities
function displayQuickSellData(data) {
    if (data.length === 0) {
        document.getElementById('quickSellContainer').innerHTML = '<p class="empty-message">No quick sell opportunities found</p>';
        return;
    }
    
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['Image', 'Item Name', 'Enchantment', 'Royal Sell Min', 'BM Buy Max', 'Profit Ratio', 'Desired Buy Price'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        
        // Don't add sorting to the Image column
        if (index > 0) {
            th.classList.add('sortable');
            th.addEventListener('click', () => sortTable('quickSellContainer', index, headerText));
        }
        
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add item image
        const imgCell = document.createElement('td');
        const img = document.createElement('img');
        
        // Attempt to extract item ID from the name (assuming format like "T4_ITEM_NAME")
        let itemId = item.name;
        if (item.name && item.name.includes('T')) {
            const match = item.name.match(/T\d+_[A-Z0-9_]+/);
            if (match) {
                itemId = match[0];
                if (item.enchant > 0) {
                    itemId += `@${item.enchant}`;
                }
            }
        }
        
        img.src = getItemImageUrl(itemId);
        img.alt = item.name;
        img.classList.add('item-image');
        img.width = 40;
        img.height = 40;
        img.onerror = function() {
            this.src = document.getElementById('item-placeholder').src;
        };
        imgCell.appendChild(img);
        row.appendChild(imgCell);
        
        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;
        row.appendChild(nameCell);
        
        const enchantCell = document.createElement('td');
        enchantCell.textContent = item.enchant;
        row.appendChild(enchantCell);
        
        const sellRlCell = document.createElement('td');
        sellRlCell.textContent = item.sell_min_rl ? formatPrice(item.sell_min_rl) : 'N/A';
        row.appendChild(sellRlCell);
        
        const buyBmCell = document.createElement('td');
        buyBmCell.textContent = item.buy_max_bm ? formatPrice(item.buy_max_bm) : 'N/A';
        row.appendChild(buyBmCell);
        
        const diffCell = document.createElement('td');
        diffCell.textContent = item.diff_quick_sell ? item.diff_quick_sell.toFixed(2) : 'N/A';
        diffCell.classList.add(item.diff_quick_sell > 1 ? 'profit-positive' : 'profit-negative');
        row.appendChild(diffCell);
        
        const desiredCell = document.createElement('td');
        desiredCell.textContent = item.quick_sell_desired ? formatPrice(item.quick_sell_desired) : 'N/A';
        row.appendChild(desiredCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    document.getElementById('quickSellContainer').innerHTML = '';
    document.getElementById('quickSellContainer').appendChild(table);
}

// Display sell order opportunities
function displaySellOrderData(data) {
    if (data.length === 0) {
        document.getElementById('sellOrderContainer').innerHTML = '<p class="empty-message">No sell order opportunities found</p>';
        return;
    }
    
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['Image', 'Item Name', 'Enchantment', 'Royal Sell Min', 'BM Sell Min', 'Profit Ratio', 'Desired Sell Price'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        
        // Don't add sorting to the Image column
        if (index > 0) {
            th.classList.add('sortable');
            th.addEventListener('click', () => sortTable('sellOrderContainer', index, headerText));
        }
        
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add item image
        const imgCell = document.createElement('td');
        const img = document.createElement('img');
        
        // Attempt to extract item ID from the name (assuming format like "T4_ITEM_NAME")
        let itemId = item.name;
        if (item.name && item.name.includes('T')) {
            const match = item.name.match(/T\d+_[A-Z0-9_]+/);
            if (match) {
                itemId = match[0];
                if (item.enchant > 0) {
                    itemId += `@${item.enchant}`;
                }
            }
        }
        
        img.src = getItemImageUrl(itemId);
        img.alt = item.name;
        img.classList.add('item-image');
        img.width = 40;
        img.height = 40;
        img.onerror = function() {
            this.src = document.getElementById('item-placeholder').src;
        };
        imgCell.appendChild(img);
        row.appendChild(imgCell);
        
        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;
        row.appendChild(nameCell);
        
        const enchantCell = document.createElement('td');
        enchantCell.textContent = item.enchant;
        row.appendChild(enchantCell);
        
        const sellRlCell = document.createElement('td');
        sellRlCell.textContent = item.sell_min_rl ? formatPrice(item.sell_min_rl) : 'N/A';
        row.appendChild(sellRlCell);
        
        const sellBmCell = document.createElement('td');
        sellBmCell.textContent = item.sell_min_bm ? formatPrice(item.sell_min_bm) : 'N/A';
        row.appendChild(sellBmCell);
        
        const diffCell = document.createElement('td');
        diffCell.textContent = item.diff_sell_order ? item.diff_sell_order.toFixed(2) : 'N/A';
        diffCell.classList.add(item.diff_sell_order > 1 ? 'profit-positive' : 'profit-negative');
        row.appendChild(diffCell);
        
        const desiredCell = document.createElement('td');
        desiredCell.textContent = item.sell_order_desired ? formatPrice(item.sell_order_desired) : 'N/A';
        row.appendChild(desiredCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    document.getElementById('sellOrderContainer').innerHTML = '';
    document.getElementById('sellOrderContainer').appendChild(table);
}

// Get quality name from quality number
function getQualityName(quality) {
    switch (parseInt(quality)) {
        case 1: return 'Normal';
        case 2: return 'Good';
        case 3: return 'Outstanding';
        case 4: return 'Excellent';
        case 5: return 'Masterpiece';
        default: return 'Unknown';
    }
}

// Format price with commas
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Compare with Black Market
async function compareWithBlackMarket() {
    const location = document.getElementById('locationSelect').value;
    if (!location) {
        showNotification('Please select a location first', 'error');
        return;
    }
    
    if (location === 'bm') {
        showNotification('Cannot compare Black Market with itself', 'error');
        return;
    }
    
    try {
        showNotification('Comparing markets...', 'success');
        const result = await eel.compare_markets(location)();
        
        if (result.success) {
            displayQuickSellData(result.quick_sell);
            displaySellOrderData(result.sell_order);
            showTab('quickSellTab');
        } else {
            document.getElementById('quickSellContainer').innerHTML = `<p class="empty-message">${result.message}</p>`;
            document.getElementById('sellOrderContainer').innerHTML = `<p class="empty-message">${result.message}</p>`;
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error comparing markets: ${error}`, 'error');
    }
}

// Display quick sell opportunities
function displayQuickSellData(data) {
    if (data.length === 0) {
        document.getElementById('quickSellContainer').innerHTML = '<p class="empty-message">No quick sell opportunities found</p>';
        return;
    }
    
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['Image', 'Item Name', 'Enchantment', 'Royal Sell Min', 'BM Buy Max', 'Profit Ratio', 'Desired Buy Price'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        
        // Don't add sorting to the Image column
        if (index > 0) {
            th.classList.add('sortable');
            th.addEventListener('click', () => sortTable('quickSellContainer', index, headerText));
        }
        
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add item image
        const imgCell = document.createElement('td');
        const img = document.createElement('img');
        
        // Attempt to extract item ID from the name (assuming format like "T4_ITEM_NAME")
        let itemId = item.name;
        if (item.name && item.name.includes('T')) {
            const match = item.name.match(/T\d+_[A-Z0-9_]+/);
            if (match) {
                itemId = match[0];
                if (item.enchant > 0) {
                    itemId += `@${item.enchant}`;
                }
            }
        }
        
        img.src = getItemImageUrl(itemId);
        img.alt = item.name;
        img.classList.add('item-image');
        img.width = 40;
        img.height = 40;
        img.onerror = function() {
            this.src = document.getElementById('item-placeholder').src;
        };
        imgCell.appendChild(img);
        row.appendChild(imgCell);
        
        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;
        row.appendChild(nameCell);
        
        const enchantCell = document.createElement('td');
        enchantCell.textContent = item.enchant;
        row.appendChild(enchantCell);
        
        const sellRlCell = document.createElement('td');
        sellRlCell.textContent = item.sell_min_rl ? formatPrice(item.sell_min_rl) : 'N/A';
        row.appendChild(sellRlCell);
        
        const buyBmCell = document.createElement('td');
        buyBmCell.textContent = item.buy_max_bm ? formatPrice(item.buy_max_bm) : 'N/A';
        row.appendChild(buyBmCell);
        
        const diffCell = document.createElement('td');
        diffCell.textContent = item.diff_quick_sell ? item.diff_quick_sell.toFixed(2) : 'N/A';
        diffCell.classList.add(item.diff_quick_sell > 1 ? 'profit-positive' : 'profit-negative');
        row.appendChild(diffCell);
        
        const desiredCell = document.createElement('td');
        desiredCell.textContent = item.quick_sell_desired ? formatPrice(item.quick_sell_desired) : 'N/A';
        row.appendChild(desiredCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    document.getElementById('quickSellContainer').innerHTML = '';
    document.getElementById('quickSellContainer').appendChild(table);
}

// Display sell order opportunities
function displaySellOrderData(data) {
    if (data.length === 0) {
        document.getElementById('sellOrderContainer').innerHTML = '<p class="empty-message">No sell order opportunities found</p>';
        return;
    }
    
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['Image', 'Item Name', 'Enchantment', 'Royal Sell Min', 'BM Sell Min', 'Profit Ratio', 'Desired Sell Price'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        
        // Don't add sorting to the Image column
        if (index > 0) {
            th.classList.add('sortable');
            th.addEventListener('click', () => sortTable('sellOrderContainer', index, headerText));
        }
        
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add item image
        const imgCell = document.createElement('td');
        const img = document.createElement('img');
        
        // Attempt to extract item ID from the name (assuming format like "T4_ITEM_NAME")
        let itemId = item.name;
        if (item.name && item.name.includes('T')) {
            const match = item.name.match(/T\d+_[A-Z0-9_]+/);
            if (match) {
                itemId = match[0];
                if (item.enchant > 0) {
                    itemId += `@${item.enchant}`;
                }
            }
        }
        
        img.src = getItemImageUrl(itemId);
        img.alt = item.name;
        img.classList.add('item-image');
        img.width = 40;
        img.height = 40;
        img.onerror = function() {
            this.src = document.getElementById('item-placeholder').src;
        };
        imgCell.appendChild(img);
        row.appendChild(imgCell);
        
        const nameCell = document.createElement('td');
        nameCell.textContent = item.name;
        row.appendChild(nameCell);
        
        const enchantCell = document.createElement('td');
        enchantCell.textContent = item.enchant;
        row.appendChild(enchantCell);
        
        const sellRlCell = document.createElement('td');
        sellRlCell.textContent = item.sell_min_rl ? formatPrice(item.sell_min_rl) : 'N/A';
        row.appendChild(sellRlCell);
        
        const sellBmCell = document.createElement('td');
        sellBmCell.textContent = item.sell_min_bm ? formatPrice(item.sell_min_bm) : 'N/A';
        row.appendChild(sellBmCell);
        
        const diffCell = document.createElement('td');
        diffCell.textContent = item.diff_sell_order ? item.diff_sell_order.toFixed(2) : 'N/A';
        diffCell.classList.add(item.diff_sell_order > 1 ? 'profit-positive' : 'profit-negative');
        row.appendChild(diffCell);
        
        const desiredCell = document.createElement('td');
        desiredCell.textContent = item.sell_order_desired ? formatPrice(item.sell_order_desired) : 'N/A';
        row.appendChild(desiredCell);
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    document.getElementById('sellOrderContainer').innerHTML = '';
    document.getElementById('sellOrderContainer').appendChild(table);
}

// Function to sort table by column
function sortTable(containerId, columnIndex, headerText) {
    const container = document.getElementById(containerId);
    const table = container.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Toggle sorting direction if clicking the same column again
    if (sortState.column === headerText) {
        sortState.ascending = !sortState.ascending;
    } else {
        sortState.column = headerText;
        sortState.ascending = true;
    }
    
    // Update sort indicators in table headers
    const headers = table.querySelectorAll('th');
    headers.forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add sort indicator to the current header
    const currentHeader = headers[columnIndex];
    currentHeader.classList.add(sortState.ascending ? 'sort-asc' : 'sort-desc');
    
    // Sort rows
    rows.sort((rowA, rowB) => {
        // Get cell content, skip the image cell if it exists
        const cellA = rowA.cells[columnIndex].textContent.trim();
        const cellB = rowB.cells[columnIndex].textContent.trim();
        
        // Handle numeric values (like prices and profit ratios)
        if (!isNaN(parseFloat(cellA)) && !isNaN(parseFloat(cellB))) {
            const numA = parseFloat(cellA.replace(/,/g, ''));
            const numB = parseFloat(cellB.replace(/,/g, ''));
            
            return sortState.ascending ? numA - numB : numB - numA;
        }
        
        // Handle N/A values
        if (cellA === 'N/A' && cellB !== 'N/A') return sortState.ascending ? 1 : -1;
        if (cellA !== 'N/A' && cellB === 'N/A') return sortState.ascending ? -1 : 1;
        if (cellA === 'N/A' && cellB === 'N/A') return 0;
        
        // Default to string comparison
        return sortState.ascending ? 
            cellA.localeCompare(cellB) : 
            cellB.localeCompare(cellA);
    });
    
    // Remove all existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Add sorted rows back to the table
    rows.forEach(row => tbody.appendChild(row));
    
    // Show notification about sorting
    showNotification(`Sorted by ${headerText} ${sortState.ascending ? 'ascending' : 'descending'}`, 'success');
}

// Export to CSV
async function exportToCsv() {
    const location = document.getElementById('locationSelect').value;
    if (!location) {
        showNotification('Please select a location first', 'error');
        return;
    }
    
    try {
        const result = await eel.export_to_csv(location)();
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error exporting to CSV: ${error}`, 'error');
    }
}

// Clear location data
async function clearLocationData() {
    const location = document.getElementById('locationSelect').value;
    if (!location) {
        showNotification('Please select a location first', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to clear all data for ${location}?`)) {
        return;
    }
    
    try {
        const result = await eel.clear_location_data(location)();
        if (result.success) {
            document.getElementById('marketDataContainer').innerHTML = '<p class="empty-message">Select a location and click "Show Market Data"</p>';
            document.getElementById('quickSellContainer').innerHTML = '<p class="empty-message">Select a location and click "Compare with Black Market"</p>';
            document.getElementById('sellOrderContainer').innerHTML = '<p class="empty-message">Select a location and click "Compare with Black Market"</p>';
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification(`Error clearing data: ${error}`, 'error');
    }
}

// Show tab content
function showTab(tabId) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Show the selected tab content
    document.getElementById(tabId).classList.add('active');
    
    // Update tab button active state
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));
    
    // Find and activate the button that corresponds to this tab
    const activeButton = Array.from(tabButtons).find(button => {
        return button.onclick.toString().includes(tabId);
    });
    
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification';
    notification.classList.add(type);
    
    // Clear any existing timeout
    if (notification.timeout) {
        clearTimeout(notification.timeout);
    }
    
    // Set timeout to hide notification after 3 seconds
    notification.timeout = setTimeout(() => {
        notification.classList.remove(type);
    }, 3000);
}