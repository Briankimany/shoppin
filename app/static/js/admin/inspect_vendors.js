
function toggleVendor(vendorId, element) {
    const content = document.getElementById("vendor-" + vendorId);
    const isHidden = content.style.display === "none" || content.style.display === "";
    
    // Toggle display
    content.style.display = isHidden ? "block" : "none";
    
    // Toggle active class
    element.classList.toggle("active", isHidden);
    
    // Close all orders when closing vendor
    if (!isHidden) {
        const orderContents = content.querySelectorAll(".order-content");
        orderContents.forEach(orderContent => {
            orderContent.style.display = "none";
            const header = orderContent.previousElementSibling;
            if (header) header.classList.remove("active");
        });
    }
}

function toggleOrder(orderId, element) {
    const content = document.getElementById("order-" + orderId);
    const isHidden = content.style.display === "none" || content.style.display === "";
    
    // Toggle display
    content.style.display = isHidden ? "block" : "none";
    
    // Toggle active class
    element.classList.toggle("active", isHidden);
}

// Optional: Auto-expand if there's only one vendor
document.addEventListener('DOMContentLoaded', function() {
    const vendors = document.querySelectorAll('.vendor-container');
    if (vendors.length === 1) {
        const firstVendor = vendors[0];
        const header = firstVendor.querySelector('.vendor-header');
        toggleVendor(header.getAttribute('onclick').match(/'([^']+)'/)[1], header);
    }
});
