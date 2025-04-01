
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
        
        fetch("/shop/update_cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
               
            },
            body: JSON.stringify({ quantities })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert("Failed to update cart: " + (data.message || "Please try again"));
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while updating your cart");
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
            
            fetch("/cart/remove", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                 
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cartItem.style.transition = "all 0.3s ease";
                    cartItem.style.height = cartItem.offsetHeight + "px";
                    cartItem.offsetHeight; // Trigger reflow
                    cartItem.style.margin = "0";
                    cartItem.style.padding = "0";
                    cartItem.style.height = "0";
                    cartItem.style.opacity = "0";
                    
                    setTimeout(() => {
                        cartItem.remove();
                        if (!document.querySelector(".cart-item")) {
                            location.reload();
                        }
                    }, 300);
                } else {
                    alert("Failed to remove item: " + (data.message || "Please try again"));
                    cartItem.style.opacity = "1";
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while removing the item");
                cartItem.style.opacity = "1";
                button.disabled = false;
            });
        });
    });
});
