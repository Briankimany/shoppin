document.getElementById('submit-btn').addEventListener('click', async function() {
    // Ensure elements exist first
    const emailInput = document.getElementById('email');
    const btn = this;
    const messageEl = document.getElementById('message');
    
    if (!emailInput || !btn || !messageEl) {
        console.error('Required elements not found!');
        return;
    }

    const spinner = btn.querySelector('.spinner');
    const buttonText = btn.querySelector('.button-text');
    
    // Clear previous state
    let timer = window.passwordResetTimer;
    if (timer) clearInterval(timer);
    messageEl.style.display = 'none'; // Only if messageEl exists

    // Show loading state
    if (buttonText && spinner) {
        buttonText.style.opacity = '0';
        spinner.style.display = 'block';
    }
    
    if (emailInput) emailInput.disabled = true;
    if (btn) btn.disabled = true;

    try {
        const response = await fetch("/user/reset-password", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: emailInput.value.trim() })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result = await response.json();
        if (messageEl) {
            messageEl.textContent = result.message;
            messageEl.className = `message ${result.success ? 'success' : 'error'}`;
            messageEl.style.display = 'block';
        }

        if (result.success && result.cooldown) {
            let remaining = result.cooldown;
            
            window.passwordResetTimer = setInterval(() => {
                remaining--;
                if (buttonText) {
                    buttonText.textContent = `Resend in ${remaining}s`;
                }
                
                if (remaining <= 0) {
                    clearInterval(window.passwordResetTimer);
                    resetControls();
                }
            }, 1000);
            
            // Initial update
            if (buttonText) buttonText.textContent = `Resend in ${remaining}s`;
        } else {
            resetControls();
        }

    } catch (error) {
        console.error('Error:', error);
        if (messageEl) {
            messageEl.textContent = 'Failed to process request';
            messageEl.className = 'message error';
            messageEl.style.display = 'block';
        }
        resetControls();
    }

    function resetControls() {
        if (emailInput) emailInput.disabled = false;
        if (btn) btn.disabled = false;
        if (buttonText && spinner) {
            buttonText.style.opacity = '1';
            spinner.style.display = 'none';
            buttonText.textContent = 'Send Reset Link';
        }
        if (messageEl) messageEl.style.display = 'none';
    }
});