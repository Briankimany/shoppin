
document.addEventListener("DOMContentLoaded", function() {
    const cartButtons = document.querySelectorAll(".add-to-cart:not(:disabled)");

    cartButtons.forEach(button => {
        button.addEventListener("click", function() {
            const productId = this.getAttribute("data-product-id");
            const quantityInput = document.getElementById("quantity-" + productId);
            const quantity = parseInt(quantityInput.value);
            const maxQuantity = parseInt(quantityInput.max);
            
            // Validate quantity
            if (quantity < 1 || quantity > maxQuantity) {
                alert(`Please enter a quantity between 1 and ${maxQuantity}`);
                quantityInput.focus();
                return;
            }

            // Disable button during request
            button.disabled = true;
            button.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-spin">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                Adding...
            `;

            fetch("/shop/add_to_cart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const messageDiv = document.getElementById("cart-message");
                    messageDiv.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        Added to cart successfully!
                    `;
                    messageDiv.style.display = "flex";
                    messageDiv.style.alignItems = "center";
                    messageDiv.style.gap = "0.5rem";
                    
                    setTimeout(() => {
                        messageDiv.style.display = "none";
                    }, 3000);
                } else {
                    alert("Failed to add to cart: " + (data.error || "Please try again"));
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="9" cy="21" r="1"></circle>
                        <circle cx="20" cy="21" r="1"></circle>
                        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                    </svg>
                    Add to Cart
                `;
            });
        });
    });

    // Quantity input validation
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const max = parseInt(this.max);
            const min = parseInt(this.min);
            let value = parseInt(this.value);
            
            if (isNaN(value)) value = min;
            if (value < min) value = min;
            if (value > max) value = max;
            
            this.value = value;
        });
    });
});

// Simple spinner animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .animate-spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
