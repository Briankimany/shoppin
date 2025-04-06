
    document.addEventListener("DOMContentLoaded", function() {
    const confirmBtn = document.getElementById("confirm-btn");
    const phoneInput = document.getElementById("phone");
    const amountInput = document.getElementById("amount");
    const loadingContainer = document.getElementById("loading-container");
    const statusMessage = document.getElementById("status-message");
    const paymentForm = document.getElementById("payment-form");

    // Prevent form submission
    paymentForm.addEventListener("submit", function(e) {
        e.preventDefault();
    });

    confirmBtn.addEventListener("click", function() {
        const phoneNumber = phoneInput.value.trim();
        const amount = amountInput.value.trim();

        // Clear previous messages
        statusMessage.textContent = "";
        statusMessage.className = "status-message";
        statusMessage.style.display = "none";

        // Validate phone number
        if (!phoneNumber || !/^0[0-9]{9}$/.test(phoneNumber)) {
            statusMessage.textContent = "Please enter a valid 10-digit phone number starting with 0";
            statusMessage.className = "status-message error";
            statusMessage.style.display = "block";
            phoneInput.focus();
            return;
        }

        // Show loading state
        loadingContainer.style.display = "flex";

        // Make payment request
        fetch("/shop/api-pay", {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
 
            },
            body: JSON.stringify({ 
                phone: phoneNumber, 
                amount: amount 
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingContainer.style.display = "none";

            if (data.success || data.message === "success") {
                statusMessage.textContent = "Payment successful! Redirecting...";
                statusMessage.className = "status-message success";
                statusMessage.style.display = "block";
                
                setTimeout(() => {
                    window.location.href = "/shop/";
                }, 2000);
            } else {
                statusMessage.textContent = data.message || "Payment processing failed";
                statusMessage.className = "status-message error";
                statusMessage.style.display = "block";
            }
        })
        .catch(error => {
            loadingContainer.style.display = "none";
            statusMessage.textContent = "Payment failed. Please try again or contact support";
            statusMessage.className = "status-message error";
            statusMessage.style.display = "block";
            console.error("Payment error:", error);
        });
    });

    phoneInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
    });
});

