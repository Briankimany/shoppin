
// Password visibility toggle
document.querySelectorAll('.toggle-password').forEach(icon => {
    icon.addEventListener('click', function() {
        const target = this.getAttribute('data-target');
        const input = document.getElementById(target);
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        this.classList.toggle('fa-eye-slash');
    });
});

// Form submission
document.getElementById('resetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const userId = document.getElementById('user_id').value;
    const token = document.getElementById('reset_token').value;
    
    // Client-side validation
    if (newPassword !== confirmPassword) {
        document.getElementById('confirm-error').textContent = 'Passwords do not match';
        return;
    }
    
    if (newPassword.length < 8) {
        document.getElementById('password-error').textContent = 'Password must be at least 8 characters';
        return;
    }
    
    try {
        const response = await fetch(window.location.href, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                new_password: newPassword,
                user_id: userId,
                token: token
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = data.redirect_url || '/login';
        } else {
            alert(data.error || 'Password reset failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});