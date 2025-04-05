document.addEventListener('DOMContentLoaded', function() {
    // --- Payment Method Toggle ---
    const methodSelect = document.getElementById('method');
    const accountDetails = document.getElementById('account-details');
    
    if (methodSelect && accountDetails) {
        methodSelect.addEventListener('change', function() {
            accountDetails.style.display = this.value ? 'block' : 'none';
        });
    }

    // --- Amount Validation ---
    const amountInput = document.getElementById('amount');
    let errorElement; // Declare at higher scope
    
    if (amountInput) {
        const maxAmount = parseFloat(amountInput.max) || 0;
        errorElement = document.getElementById('amount-error') || createErrorElement(amountInput);
        
        amountInput.addEventListener('input', function() {
            validateAmount(this, maxAmount, errorElement);
        });
        amountInput.addEventListener('blur', function() {
            enforceAmountLimit(this, maxAmount);
        });
    }

    // --- Form Submission ---
    const form = document.getElementById('withdrawal-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Helper Functions
    function validateAmount(input, maxAmount, errorElement) {
        const enteredAmount = parseFloat(input.value) || 0;
        
        if (enteredAmount > maxAmount) {
            errorElement.textContent = `Maximum withdrawal: $${maxAmount.toFixed(2)}`;
            errorElement.style.display = 'block';
            input.classList.add('input-error');
            
            if (input === document.activeElement) {
                input.dataset.originalValue = input.value;
            } else {
                input.value = maxAmount.toFixed(2);
            }
        } else {
            errorElement.style.display = 'none';
            input.classList.remove('input-error');
            if (input.dataset.originalValue) delete input.dataset.originalValue;
        }
    }

    function enforceAmountLimit(input, maxAmount) {
        const enteredAmount = parseFloat(input.value) || 0;
        if (enteredAmount > maxAmount) input.value = maxAmount.toFixed(2);
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        const notification = createNotification();
        
        try {
            toggleFormLoading(this, true);
            const response = await fetch("/vendor/process-pay", {
                method: "POST",
                body: new FormData(this),
                headers: { 'Accept': 'application/json' }
            });
            
            const result = await response.json();
            showNotification(notification, result.message, response.ok ? "success" : "error");
            if (response.ok) this.reset();
            
        } catch (error) {
            showNotification(notification, "Network error. Try again later.", "error");
            console.error("Fetch error:", error);
        } finally {
            toggleFormLoading(this, false);
        }
    }

    function createErrorElement(inputElement) {
        const div = document.createElement('div');
        div.id = 'amount-error';
        div.className = 'error-message';
        inputElement.parentNode.appendChild(div);
        return div;
    }

    function createNotification() {
        const div = document.createElement("div");
        div.className = "withdrawal-notification";
        document.body.appendChild(div);
        return div;
    }

    function showNotification(element, message, type) {
        element.textContent = message;
        element.style.display = "block";
        element.style.backgroundColor = type === "success" ? "#4CAF50" : "#f44336";
        setTimeout(() => element.style.display = "none", 5000);
    }

    function toggleFormLoading(form, isLoading) {
        const submitBtn = form.querySelector("button[type='submit']");
        if (submitBtn) submitBtn.disabled = isLoading;
    }
});