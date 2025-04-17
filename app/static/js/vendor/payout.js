document.addEventListener('DOMContentLoaded', function() {
    // --- Shared Elements ---
    const modal = document.getElementById('withdrawals-modal');
    const viewBtn = document.getElementById('view-withdrawals-btn');
    const closeBtn = document.querySelector('#withdrawals-modal .close-modal');
    const form = document.getElementById('withdrawal-form');
    const methodSelect = document.getElementById('method');
    const accountDetails = document.getElementById('account-details');
    const amountInput = document.getElementById('amount');
    const accountNumber = document.getElementById("default-account-number")?.dataset.accountNumber;
    let refreshInterval;

    // --- Initialization ---
    initPaymentMethodToggle();
    initAmountValidation();
    initFormSubmission();
    fetchAndUpdateBalances();

    // --- Modal Functions ---
    function openModal() {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        modal.setAttribute('aria-hidden', 'false');
        closeBtn.focus();
        loadWithdrawals();
    }

    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        modal.setAttribute('aria-hidden', 'true');
        clearInterval(refreshInterval);
    }

    async function loadWithdrawals() {
        const container = document.getElementById('withdrawals-list-container');
        container.innerHTML = '<div class="spinner"></div>';

        try {
            const response = await fetch('/vendor/payouts',{method:"POST"});
            const data = await response.json();

            if (!data.withdrawals.length) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No withdrawal history yet</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="transactions-list">
                    ${data.withdrawals.map(w => `
                        <div class="transaction-item ${w.status}">
                            <div class="transaction-meta">
                                <span class="transaction-date">${formatDate(w.request)}</span>
                            </div>
                            <div class="transaction-details">
                                <span class="transaction-amount">Ksh${w.amount.toFixed(2)}</span>
                                <span class="transaction-method">${w.method}</span>
                                <span class="transaction-status">${w.status}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (err) {
            console.error('Error:', err);
            container.innerHTML = `
                <div class="error-state">
                    <p>Error loading data. <button onclick="loadWithdrawals()">Retry</button></p>
                </div>
            `;
        }
    }

    // --- Balance Functions ---
    async function fetchAndUpdateBalances() {
        const container = document.querySelector('.card-content');
        try {
            container.setAttribute('data-loading', 'true');
            const response = await fetch('/vendor/payouts',{method:"POST"});
            const data = await response.json();
            
            document.getElementById('available-balance').textContent = `Ksh${data.balance.available.toFixed(2)}`;
            document.getElementById('pending-balance').textContent = `Ksh${data.balance.pending.toFixed(2)}`;
            document.getElementById('total-balance').textContent = `Ksh${data.balance.total.toFixed(2)}`;
        } catch (error) {
            console.error('Error:', error);
            document.querySelectorAll('.metric-value').forEach(el => {
                el.textContent = 'Error';
            });
        } finally {
            container.removeAttribute('data-loading');
        }
    }

    // --- Form Functions ---
    function initPaymentMethodToggle() {
        if (methodSelect && accountDetails) {
            methodSelect.addEventListener('change', function() {
                accountDetails.style.display = this.value ? 'block' : 'none';
            });
        }
    }

    function initAmountValidation() {
        if (amountInput) {
            const maxAmount = parseFloat(amountInput.max) || 0;
            const errorElement = document.getElementById('amount-error') || createErrorElement(amountInput);
            
            amountInput.addEventListener('input', () => validateAmount(amountInput, maxAmount, errorElement));
            amountInput.addEventListener('blur', () => enforceAmountLimit(amountInput, maxAmount));
        }
    }

    function initFormSubmission() {
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const notification = createNotification();
                
                try {
                    toggleFormLoading(true);
                    const response = await fetch("/vendor/process-pay", {
                        method: "POST",
                        body: new FormData(form),
                        headers: { 'Accept': 'application/json' }
                    });
                    
                    const result = await response.json();
                    showNotification(notification, result.message, response.ok ? "success" : "error");
                    
                    if (response.ok) {
                        form.reset();
                        fetchAndUpdateBalances();
                        pollWithdrawalStatus(result.withdraw_id);
                    }
                } catch (error) {
                    showNotification(notification, "Network error", "error");
                } finally {
                    toggleFormLoading(false);
                }
            });
        }
    }

    // --- Helper Functions ---
    function validateAmount(input, maxAmount, errorElement) {
        const amount = parseFloat(input.value) || 0;
        if (amount > maxAmount) {
            errorElement.textContent = `Max: $${maxAmount.toFixed(2)}`;
            errorElement.style.display = 'block';
            input.classList.add('input-error');
        } else {
            errorElement.style.display = 'none';
            input.classList.remove('input-error');
        }
    }

    function enforceAmountLimit(input, maxAmount) {
        const amount = parseFloat(input.value) || 0;
        if (amount > maxAmount) input.value = maxAmount.toFixed(2);
    }

    function pollWithdrawalStatus(id, maxAttempts = 2) {
        let attempts = 0;
        const interval = setInterval(async () => {
            if (attempts++ >= maxAttempts) {
                clearInterval(interval);
                return;
            }

            try {
                const response = await fetch(`/vendor/withdrawal-status/${id}`);

                const data = await response.json();
                console.log("the status respponse from checking vendor withdraw status "+data);
                
                if (data.status === "completed") {
                    clearInterval(interval);
                    fetchAndUpdateBalances();
                }
            } catch (error) {
                clearInterval(interval);
            }
        }, 5000);
    }

    function createErrorElement(input) {
        const div = document.createElement('div');
        div.id = 'amount-error';
        div.className = 'error-message';
        input.parentNode.appendChild(div);
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

    function toggleFormLoading(loading) {
        const btn = form?.querySelector("button[type='submit']");
        if (btn) btn.disabled = loading;
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    }

    // --- Event Listeners ---
    viewBtn?.addEventListener('click', openModal);
    closeBtn?.addEventListener('click', closeModal);
    modal?.addEventListener('click', (e) => e.target === modal && closeModal());
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal?.style.display === 'block') closeModal();
    });


async function updatePreviousWithdrawals() {
   

    const response = await fetch('/vendor/pending-withdraws', { method: "POST" });
    const data = await response.json(); 
    const ids = data.ids; 
    if (!response.ok) {
        return;
    } else {
      
        const numIds = ids.length;
        let withDrawId;

        for (let i = 0; i < numIds; i++) {
            withDrawId = ids[i];
            pollWithdrawalStatus(withDrawId, 2);
        }
    }
}

updatePreviousWithdrawals();

});