
document.getElementById('forgotForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const responseMessage = document.getElementById('responseMessage');
    const submitBtn = document.getElementById('submitBtn');
    
    // Disable button immediately
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending...';
    
    try {
        const response = await fetch("/user/forgot-password", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        // Show response message
        responseMessage.style.display = 'block';
        responseMessage.className = 'message success';
        responseMessage.textContent = data.message;
        
        // Apply cooldown if specified
        if (data.cooldown) {
            let seconds = data.cooldown;
            const timerInterval = setInterval(() => {
                submitBtn.textContent = `Resend in ${seconds}s`;
                seconds--;
                
                if (seconds < 0) {
                    clearInterval(timerInterval);
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Send Reset Link';
                }
            }, 1000);
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Reset Link';
        }
        
    } catch (error) {
        console.error('Error:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Reset Link';
        responseMessage.style.display = 'block';
        responseMessage.className = 'message error';
        responseMessage.textContent = 'An error occurred. Please try again.';
    }
});
