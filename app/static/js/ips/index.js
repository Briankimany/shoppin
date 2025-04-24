
document.addEventListener('DOMContentLoaded', function() {

    function getCsrfToken(){
        return document.querySelector('meta[name="csrf-token"]').content;
        }
    function getHeaders(get_content_type=true){
        if (!get_content_type){
            return {'X-CSRFToken': getCsrfToken()}
        }
         return {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
          };
    }

    // Elements
    const ipColumnsContainer = document.getElementById('ip-columns-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noResults = document.getElementById('no-results');
    const ipInput = document.getElementById('ip-input');
    const updateBtn = document.getElementById('update-btn');
    const searchInput = document.getElementById('search-input');
    const refreshBtn = document.getElementById('refresh-btn');
    const toastEl = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastEl);
    
    // State
    let allIPs = [];
    let filteredIPs = [];
    const columnsCount = 3;

    // Initialize
    loadIPs();
    
    // Event listeners
    updateBtn.addEventListener('click', handleAddIP);
    searchInput.addEventListener('input', handleSearch);
    refreshBtn.addEventListener('click', () => loadIPs());

    async function loadIPs() {
        try {
            showLoading();
            const response = await fetch('/ips/get-data', {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({})
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.message !== 'success') {
                throw new Error(data.message || 'Failed to load IP list');
            }

            allIPs = data.data;
            filteredIPs = [...allIPs];
            renderTables();
        } catch (error) {
            showError(error.message);
        }
    }

    function renderTables() {
        if (filteredIPs.length === 0) {
            ipColumnsContainer.style.display = 'none';
            noResults.style.display = 'block';
            loadingSpinner.style.display = 'none';
            return;
        }

        // Clear previous content
        ipColumnsContainer.innerHTML = '';
        
        // Calculate items per column
        const itemsPerColumn = Math.ceil(filteredIPs.length / columnsCount);
        
        // Create columns
        for (let col = 0; col < columnsCount; col++) {
            const columnDiv = document.createElement('div');
            columnDiv.className = 'ip-column';
            columnDiv.style.flex = '1';
            columnDiv.style.minWidth = '250px';
            
            const table = document.createElement('table');
            table.className = 'ip-table';
            
            // Create table header
            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th>IP Address</th>
                    <th>Last Seen</th>
                </tr>
            `;
            table.appendChild(thead);
            
            // Create table body
            const tbody = document.createElement('tbody');
            
            // Calculate start and end index for this column
            const start = col * itemsPerColumn;
            const end = Math.min(start + itemsPerColumn, filteredIPs.length);
            
            // Add rows to this column's table
            for (let i = start; i < end; i++) {
                const ip = filteredIPs[i];
                const row = document.createElement('tr');
                
                // Format timestamp to be more human readable
                const date = new Date(ip.accessed_at);
                const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                const day = date.getDate();
                const month = monthNames[date.getMonth()];
                const hours = date.getHours().toString().padStart(2, '0');
                const minutes = date.getMinutes().toString().padStart(2, '0');
                const timestamp = `${month} ${day}, ${hours}:${minutes}`;
                
                // Determine status indicator
                const statusClass = ip.proxy ? 'status-proxy' : 'status-online';
                
                row.innerHTML = `
                    <td>
                        <span class="status-badge ${statusClass}"></span>
                        ${ip.ip_address}
                    </td>
                    <td class="timestamp">${timestamp}</td>
                `;
                
                // Add click event to show details
                row.addEventListener('click', () => showIpDetails(ip));
                
                tbody.appendChild(row);
            }
            
            table.appendChild(tbody);
            columnDiv.appendChild(table);
            ipColumnsContainer.appendChild(columnDiv);
        }
        
        ipColumnsContainer.style.display = 'flex';
        noResults.style.display = 'none';
        loadingSpinner.style.display = 'none';
    }


    function showIpDetails(ip) {
        const date = new Date(ip.accessed_at);
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        };
        const formattedDate = date.toLocaleDateString('en-US', options);
        
        const location = [ip.city, ip.region, ip.country].filter(Boolean).join(', ') || 'Unknown';
        const details = `
            <div class="detail-row mb-2">
                <strong class="detail-label">IP Address:</strong>
                <span>${ip.ip_address}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">Location:</strong>
                <span>${location}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">Last Seen:</strong>
                <span>${formattedDate}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">Proxy:</strong>
                <span>${ip.proxy ? 'Yes' : 'No'}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">ISP:</strong>
                <span>${ip.isp || 'Unknown'}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">Device:</strong>
                <span>${ip.device || 'Unknown'}</span>
            </div>
            <div class="detail-row mb-2">
                <strong class="detail-label">Browser:</strong>
                <span>${ip.browser || 'Unknown'}</span>
            </div>
            <div class="detail-row">
                <strong class="detail-label">OS:</strong>
                <span>${ip.os || 'Unknown'}</span>
            </div>
        `;
        
        document.getElementById('ipDetailsContent').innerHTML = details;
        const modal = new bootstrap.Modal(document.getElementById('ipDetailsModal'));
        modal.show();
    }


    async function handleAddIP() {
        const ip = ipInput.value.trim();
        if (!ip) {
            showToast('Error', 'Please enter an IP address', 'danger');
            return;
        }

        try {
            updateBtn.disabled = true;
            updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';

            const response = await fetch('/ips/update', {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ ip: ip })
            });

            if (!response.ok) {
                showToast('errror',`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            showToast(data.message ,data.data);
            if (data.message !== 'success') {
                showToast('error' ,data.message || 'Failed to add IP');
            }

            showToast('Success', 'IP address added successfully', 'success');
            ipInput.value = '';
            await loadIPs();
        } catch (error) {
            showToast('Error', error.message, 'danger');
        } finally {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Add IP';
        }
    }

    function handleSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        if (searchTerm) {
            filteredIPs = allIPs.filter(ip => 
                ip.ip_address.toLowerCase().includes(searchTerm) ||
                (ip.city && ip.city.toLowerCase().includes(searchTerm)) ||
                (ip.region && ip.region.toLowerCase().includes(searchTerm)) ||
                (ip.country && ip.country.toLowerCase().includes(searchTerm)) ||
                (ip.isp && ip.isp.toLowerCase().includes(searchTerm))
            );
        } else {
            filteredIPs = [...allIPs];
        }
        renderTables();
    }

    function showLoading() {
        ipColumnsContainer.style.display = 'none';
        noResults.style.display = 'none';
        loadingSpinner.style.display = 'block';
    }

    function showError(message) {
        ipColumnsContainer.style.display = 'none';
        loadingSpinner.innerHTML = `
            <i class="bi bi-exclamation-triangle text-danger" style="font-size: 2rem;"></i>
            <p class="mt-2 mb-2">${message}</p>
            <button class="btn btn-sm btn-outline-primary" onclick="window.location.reload()">
                <i class="bi bi-arrow-clockwise"></i> Try Again
            </button>
        `;
    }

    function showToast(title, message, type = 'info') {
        const toastHeader = toastEl.querySelector('.toast-header');
        toastHeader.className = `toast-header text-white bg-${type}`;
        document.getElementById('toast-title').textContent = title;
        document.getElementById('toast-message').textContent = message;
        toast.show();
    }
});
