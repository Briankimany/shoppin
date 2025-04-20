
document.addEventListener('DOMContentLoaded', function() {
    const ordersContainer = document.querySelector('.orders-grid');
    const limitSelect = document.querySelector('.limit-select');
    const exportBtn = document.querySelector('.export-btn');
    let ordersData = [];
    let isLoading = false;
    
    // Initial load
    loadOrders();
    
    // Handle limit change
    limitSelect.addEventListener('change', loadOrders);
    
    // Export to CSV
    exportBtn.addEventListener('click', exportToCSV);
    
    async function loadOrders() {
        if (isLoading) return;
        
        isLoading = true;
        showLoading();
        
        try {
            const limit = limitSelect.value;
            const response = await fetch(`/vendor/orders?limit=${limit}`,{method:"POST"});
            const data = await response.json();
            
            if (response.ok) {
                ordersData = data.data;
                renderOrders(ordersData);
            } else {
                throw new Error(data.message || 'Failed to load orders');
            }
        } catch (error) {
            console.error('Error loading orders:', error);
            showError(error.message);
        } finally {
            isLoading = false;
        }
    }
    
    function showLoading() {
        ordersContainer.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
            </div>
        `;
    }
    
    function showError(message) {
        ordersContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle" style="font-size: 40px; color: #ef4444; margin-bottom: 15px;"></i>
                <p>${message}</p>
                <button onclick="loadOrders()" class="btn btn-primary" style="margin-top: 15px;">
                    <i class="fas fa-sync-alt"></i> Try Again
                </button>
            </div>
        `;
    }
    
    function renderOrders(orders) {
        if (orders.length === 0) {
            ordersContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clipboard-list" style="font-size: 40px; color: #666; margin-bottom: 15px;"></i>
                    <p>No orders found</p>
                </div>
            `;
            return;
        }
        
        ordersContainer.innerHTML = orders.map(order => `
            <div class="order-card ${order.status}">
                <div class="order-header">
                    <div class="order-id">${order.id}</div>
                    <div class="order-status ${order.status}">${order.status}</div>
                </div>
                
                <div class="order-details">
                    <div class="order-detail">
                        <span class="order-detail-label">Customer:</span>
                        <span class="order-detail-value">${order.customer}</span>
                    </div>
                    <div class="order-detail">
                        <span class="order-detail-label">Placed:</span>
                        <span class="order-detail-value">${order.time_ago}</span>
                    </div>
                    <div class="order-detail">
                        <span class="order-detail-label">Total:</span>
                        <span class="order-detail-value order-total">Ksh ${order.total.toFixed(2)}</span>
                    </div>
                </div>
                
                <button class="view-details-btn" data-order-id="${order.id}">
                    <i class="fas fa-eye"></i> View Details
                </button>
            </div>
        `).join('');
        
        // Add event listeners to detail buttons
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const orderId = this.getAttribute('data-order-id');
                showOrderDetails(orderId);
            });
        });
    }

    async function showOrderDetails(orderId) {
        try {
            // Extract numeric ID from "ORD-12" format
            const numericId = orderId.split('-')[1];
            
            // Show loading state in modal
            const modal = document.createElement('div');
            modal.className = 'order-details-modal active';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title">Loading Order Details...</h3>
                    </div>
                    <div style="padding: 40px; text-align: center;">
                        <div class="spinner"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
    
            // Fetch order details from API
            const response = await fetch(`/vendor/orderd/${numericId}`);
            if (!response.ok) throw new Error('Failed to fetch order details');
            
            const orderDetails = await response.json();
            const order = ordersData.find(o => o.id === orderId);
            if (!order) throw new Error('Order not found');
    
            // Update modal with real data
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title">Order Details: ${orderId}</h3>
                        <button class="close-modal">&times;</button>
                    </div>
                    
                    <div class="order-info">
                        <p><strong>Customer:</strong> ${order.customer}</p>
                        <p><strong>Status:</strong> <span class="order-status ${order.status}">${order.status}</span></p>
                        <p><strong>Date:</strong> ${order.time_ago}</p>
                    </div>
                    
                    <h4 style="margin: 20px 0 10px 0;">Order Items</h4>
                    <table class="order-items">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Stock Left</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${orderDetails.map(item => `
                                <tr>
                                    <td>${item['product-name']}</td>
                                    <td>Ksh ${item.price}</td>
                                    <td>${item.quantity}</td>
                                    <td>${item.stock}</td>
                                    <td>Ksh ${(parseFloat(item.price) * item.quantity).toFixed(2)}</td>
                                </tr>
                            `).join('')}
                            <tr class="total-row">
                                <td colspan="4" style="text-align: right;">Total:</td>
                                <td>Ksh ${order.total.toFixed(2)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
    
            // Add close functionality
            modal.querySelector('.close-modal').addEventListener('click', () => {
                modal.classList.remove('active');
                setTimeout(() => modal.remove(), 300);
            });
    
        } catch (error) {
            console.error('Error showing order details:', error);
            
            // Update modal to show error
            if (modal) {
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3 class="modal-title">Error Loading Order</h3>
                            <button class="close-modal">&times;</button>
                        </div>
                        <div style="padding: 20px; color: #ef4444;">
                            <i class="fas fa-exclamation-circle"></i> ${error.message}
                        </div>
                        <div style="text-align: center; padding: 20px;">
                            <button class="btn btn-primary" onclick="showOrderDetails('${orderId}')">
                                <i class="fas fa-sync-alt"></i> Try Again
                            </button>
                        </div>
                    </div>
                `;
                
                modal.querySelector('.close-modal').addEventListener('click', () => {
                    modal.classList.remove('active');
                    setTimeout(() => modal.remove(), 300);
                });
            }
        }
    }
    
    function exportToCSV() {
        if (ordersData.length === 0) {
            alert('No orders to export');
            return;
        }
        
        try {
            // CSV header
            let csv = 'Order ID,Customer,Status,Date,Total\n';
            
            // Add each order
            ordersData.forEach(order => {
                csv += `"${order.id}","${order.customer}","${order.status}","${order.time_ago}",${order.total.toFixed(2)}\n`;
            });
            
            // Create download link
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `orders_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting CSV:', error);
            alert('Failed to export CSV: ' + error.message);
        }
    }
});
