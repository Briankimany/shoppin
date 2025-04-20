
document.addEventListener("DOMContentLoaded", function() {
    // Elements
    const statusFilter = document.getElementById("status-filter");
    const modal = document.getElementById("order-modal");
    const closeBtns = document.querySelectorAll(".close-modal, .close-btn");
    const orderItemsBody = document.getElementById("order-items-body");
    const modalOrderId = document.getElementById("modal-order-id");
    const orderDate = document.getElementById("order-date");
    const orderStatus = document.getElementById("order-status");
    const orderPayment = document.getElementById("order-payment");
    const orderTotal = document.getElementById("order-total");
    const printBtn = document.getElementById("print-order");

    // Filter functionality
    if (statusFilter) {
        statusFilter.addEventListener("change", function() {
            const status = this.value;
            document.querySelectorAll(".order-row").forEach(row => {
                row.style.display = (status === "all" || row.dataset.status === status) ? "" : "none";
            });
        });
    }

    // Format date
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Open modal with order details
    async function openOrderModal(orderId) {
        // Show loading state
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";
        orderItemsBody.innerHTML = '<tr><td colspan="4" class="loading-text">Loading order details...</td></tr>';

        try {
            // Fetch order details
            const response = await fetch(`/user/orders/${orderId}/items`);
            if (!response.ok) throw new Error('Failed to fetch order details');
            
            const data = await response.json();
            
            // Update modal with order data
            modalOrderId.textContent = orderId;
            orderDate.textContent = formatDate(data.order_date || new Date().toISOString());
            orderTotal.textContent = `Ksh ${parseFloat(data.total_amount).toFixed(2)}`;
            
            // Set status
            orderStatus.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            orderStatus.className = "summary-value status-badge " + data.status;
            
            // Set payment type
            const paymentType = data.payment_type || "pre-delivery";
            orderPayment.textContent = paymentType === "pre-delivery" ? "Pre-Paid" : "On Delivery";
            orderPayment.className = "summary-value payment-badge " + paymentType;
            
            // Clear and populate order items
            orderItemsBody.innerHTML = "";
            data.items.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>
                        <div class="product-link">
                            <img src="${item.image_url || '/static/images/default-product.jpg'}" 
                                 class="product-img" alt="${item['product-name']}"
                                 onerror="this.src='/static/images/default-product.jpg'">
                            ${item.product_name}
                        </div>
                    </td>
                    <td>${item.quantity}</td>
                    <td>Ksh ${parseFloat(item.price_at_purchase).toFixed(2)}</td>
                    <td>Ksh ${(parseFloat(item.price_at_purchase) * parseInt(item.quantity)).toFixed(2)}</td>
                `;
                orderItemsBody.appendChild(row);
            });
            
        } catch (error) {
            console.error("Error:", error);
            orderItemsBody.innerHTML = '<tr><td colspan="4" class="error-text">Failed to load order details. Please try again.</td></tr>';
        }
    }

    // Attach click handlers to inspect buttons
    document.querySelectorAll(".inspect-btn").forEach(button => {
        const hiddenEl = document.getElementById("4567montye");
        const orderId = button.dataset.orderId;
        console.log("Order ID:", orderId);

        button.addEventListener("click", () => openOrderModal(orderId));
    });

    // Close modal handlers
    closeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modal.style.display = "none";
            document.body.style.overflow = "";
        });
    });

    // Close modal when clicking outside
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
            document.body.style.overflow = "";
        }
    });

// Print functionality
if (printBtn) {
    printBtn.addEventListener("click", function() {
        // Create a clean table structure for printing
        const itemsHtml = Array.from(orderItemsBody.querySelectorAll("tr")).map(row => {
            const cells = Array.from(row.querySelectorAll("td")).map(cell => {
                // Handle product cell separately to maintain image and text
                if (cell.querySelector('.product-link')) {
                    const link = cell.querySelector('.product-link');
                    const img = link.querySelector('img');
                    const text = link.textContent.trim();
                    return `<td>${img ? `<img src="${img.src}" style="max-width:50px;max-height:50px;margin-right:10px;vertical-align:middle;">` : ''}${text}</td>`;
                }
                return `<td>${cell.textContent}</td>`;
            }).join('');
            return `<tr>${cells}</tr>`;
        }).join('');

        const printContent = `
            <h2 style="margin-bottom: 15px;">Order #${modalOrderId.textContent}</h2>
            <div style="margin-bottom: 20px;">
                <p><strong>Date:</strong> ${orderDate.textContent}</p>
                <p><strong>Status:</strong> ${orderStatus.textContent}</p>
                <p><strong>Payment:</strong> ${orderPayment.textContent}</p>
                <p><strong>Total:</strong> ${orderTotal.textContent}</p>
            </div>
            <table border="1" style="width:100%;border-collapse:collapse;margin-top:20px;">
                <thead>
                    <tr>
                        <th style="padding:8px;text-align:left;">Product</th>
                        <th style="padding:8px;text-align:left;">Quantity</th>
                        <th style="padding:8px;text-align:left;">Unit Price</th>
                        <th style="padding:8px;text-align:left;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>
        `;
        
        const printWindow = window.open('', '', 'width=800,height=600');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Order Receipt #${modalOrderId.textContent}</title>
                    <style>
                        body { 
                            font-family: Arial, sans-serif; 
                            padding: 20px; 
                            line-height: 1.5;
                        }
                        h2 { 
                            color: #333; 
                            margin-top: 0;
                        }
                        table { 
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 15px;
                        }
                        th { 
                            background: #f5f5f5; 
                            text-align: left; 
                            padding: 8px;
                            border: 1px solid #ddd;
                        }
                        td { 
                            padding: 8px;
                            border: 1px solid #ddd;
                            vertical-align: top;
                        }
                        .product-img { 
                            max-width: 50px; 
                            max-height: 50px; 
                            margin-right: 10px; 
                            vertical-align: middle; 
                        }
                    </style>
                </head>
                <body>
                    ${printContent}
                    <script>
                        window.onload = function() {
                            setTimeout(function() {
                                window.print();
                                setTimeout(function() {
                                    window.close();
                                }, 500);
                            }, 200);
                        };
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    });
}
});
