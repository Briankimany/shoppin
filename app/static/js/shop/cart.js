
document.addEventListener("DOMContentLoaded", function() {
    // Quantity controls
    document.querySelectorAll(".qty-btn").forEach(button => {
        button.addEventListener("click", function() {
            const input = this.parentElement.querySelector(".quantity-input");
            let value = parseInt(input.value);
            
            if (this.dataset.action === "increase") {
                input.value = value + 1;
            } else if (this.dataset.action === "decrease" && value > 1) {
                input.value = value - 1;
            }
        });
    });
    
    // Update cart functionality
    document.getElementById("update-cart-btn")?.addEventListener("click", function() {
        const quantities = {};
        
        document.querySelectorAll(".quantity-input").forEach(input => {
            quantities[input.dataset.productId] = input.value;
        });
        disableButtonWithSpinner(this);
        
        fetch("/shop/update_cart", {
            method: "POST",
            headers:getHeaders(),
            body: JSON.stringify({ quantities })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
                showAlert("Cart updated",'success');
            } else {
                showAlert("Failed to update cart: " + (data.message || "Please try again") ,'error');
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showAlert("An error occurred while updating your cart",'error');
        }).finally(() => {
            enableButton(this); 
        });
    });
    
    // Remove item functionality
    document.querySelectorAll(".remove-btn").forEach(button => {
        button.addEventListener("click", function() {
            const productId = this.dataset.productId;
            const cartItem = this.closest(".cart-item");
            
            // Visual feedback
            cartItem.style.opacity = "0.5";
            this.disabled = true;
            
            disableButtonWithSpinner(this);
            fetch("cart/remove", {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    showAlert("Item removed ",'success')
                } else {
                    showAlert("Failed to remove item: " + (data.message || "Please try again"),'warning');
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showAlert("An error occurred while removing the item",'error');
            }).finally(() => {
                enableButton(this); 
            });
        });
    });
});
