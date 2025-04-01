document.addEventListener("DOMContentLoaded", function() {
    // Filter functionality
    const statusFilter = document.getElementById("status-filter");
    if (statusFilter) {
        statusFilter.addEventListener("change", function() {
            const status = this.value;
            const rows = document.querySelectorAll(".order-row");
            rows.forEach(row => {
                row.style.display = (status === "all" || row.dataset.status === status) ? "" : "none";
            });
        });
    }

    // Modal elements
    const modal = document.getElementById("order-modal");
    const closeBtns = document.querySelectorAll(".close-modal, .close-btn");
    const orderItemsBody = document.getElementById("order-items-body");
    const modalOrderId = document.getElementById("modal-order-id");
    const orderDate = document.getElementById("order-date");
    const orderStatus = document.getElementById("order-status");
    const orderPayment = document.getElementById("order-payment");
    const orderTotal = document.getElementById("order-total");

    // Function to format date
    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // Function to open modal with order details
    function openOrderModal(orderId) {
        orderItemsBody.innerHTML = '<tr><td colspan="4" class="loading-text">Loading order details...</td></tr>';
        modal.style.display = "block";
        document.body.style.overflow = "hidden";

        fetch(`/user/orders/${orderId}/items`)
            .then(response => response.json())
            .then(data => {
                modalOrderId.textContent = orderId;
                orderDate.textContent = formatDate(data.order_date);
                orderTotal.textContent = `$${parseFloat(data.total_amount).toFixed(2)}`;
                orderStatus.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
                orderStatus.className = "summary-value status-badge " + data.status;
                const paymentType = data.payment_type === "pre-delivery" ? "pre-delivery" : "post-delivery";
                orderPayment.textContent = data.payment_type === "pre-delivery" ? "Pre-Paid" : "On Delivery";
                orderPayment.className = "summary-value payment-badge " + paymentType;
                
                orderItemsBody.innerHTML = "";
                data.items.forEach(item => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>
                            <a href="/shop/product/${item.product_id}" class="product-link" target="_blank">
                                <img src="${item.image_url}" class="product-img" alt="${item.product_name}" 
                                     onerror="this.src='/static/images/default-product.jpg'">
                                ${item.product_name}
                            </a>
                        </td>
                        <td>${item.quantity}</td>
                        <td>$${parseFloat(item.price_at_purchase).toFixed(2)}</td>
                        <td>$${(parseFloat(item.price_at_purchase) * parseInt(item.quantity)).toFixed(2)}</td>
                    `;
                    orderItemsBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error("Error fetching order details:", error);
                orderItemsBody.innerHTML = '<tr><td colspan="4" class="error-text">Failed to load order details. Please try again.</td></tr>';
            });
    }

    // Attach click handlers to inspect buttons
    document.querySelectorAll(".inspect-btn").forEach(button => {
        button.addEventListener("click", function() {
            openOrderModal(this.getAttribute("data-order-id"));
        });
    });

    // Close modal handlers
    closeBtns.forEach(btn => {
        btn.addEventListener("click", function() {
            modal.style.display = "none";
            document.body.style.overflow = "";
        });
    });

    // Close modal when clicking outside
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
            document.body.style.overflow = "";
        }
    });

    // Print functionality
    const printBtn = document.getElementById("print-order");
    if (printBtn) {
        printBtn.addEventListener("click", function() {
            const printContent = `
                <h2>Order #${modalOrderId.textContent}</h2>
                <p><strong>Date:</strong> ${orderDate.textContent}</p>
                <p><strong>Status:</strong> ${orderStatus.textContent}</p>
                <p><strong>Payment:</strong> ${orderPayment.textContent}</p>
                <p><strong>Total:</strong> ${orderTotal.textContent}</p>
                <table border="1" style="width:100%;border-collapse:collapse;margin-top:20px;">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Array.from(orderItemsBody.querySelectorAll("tr")).map(row => row.innerHTML).join("")}
                    </tbody>
                </table>
            `;
            
            const printWindow = window.open('', '', 'width=800,height=600');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Order Receipt #${modalOrderId.textContent}</title>
                        <style>
                            body { font-family: Arial, sans-serif; padding: 20px; }
                            h2 { color: #333; }
                            table { margin-top: 15px; }
                            th { background: #f5f5f5; text-align: left; padding: 8px; }
                            td { padding: 8px; border-top: 1px solid #ddd; }
                            .product-img { max-width: 50px; max-height: 50px; margin-right: 10px; vertical-align: middle; }
                        </style>
                    </head>
                    <body>
                        ${printContent}
                        <script>
                            window.onload = function() {
                                window.print();
                                setTimeout(function() {
                                    window.close();
                                }, 1000);
                            };
                        </script>
                    </body>
                </html>
            `);
            printWindow.document.close();
        });
    }
});
