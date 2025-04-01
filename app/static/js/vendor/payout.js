
document.addEventListener('DOMContentLoaded', function() {
    // Show account details field based on payment method
    const methodSelect = document.getElementById('method');
    const accountDetails = document.getElementById('account-details');
    
    methodSelect.addEventListener('change', function() {
        accountDetails.style.display = this.value ? 'block' : 'none';
    });
    
    // Validate amount doesn't exceed balance
    const amountInput = document.getElementById('amount');
    const maxAmount = parseFloat(amountInput.max);
    
    amountInput.addEventListener('change', function() {
        const enteredAmount = parseFloat(this.value);
        if (enteredAmount > maxAmount) {
            alert('You cannot withdraw more than your available balance');
            this.value = maxAmount.toFixed(2);
        }
    });
});
