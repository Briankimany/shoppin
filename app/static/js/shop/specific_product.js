
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
                showAlert(`Please enter a quantity between 1 and ${maxQuantity}`,'warning');
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
                headers: getHeaders(),
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert("added to cart",'success',3000);
                } else {
                    showAlert("Failed to add to cart: " + (data.error || "Please try again"),'warning',3000);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showAlert(error,'error');
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

