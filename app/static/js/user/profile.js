
document.addEventListener('DOMContentLoaded', function() {
    // Edit field functionality
    document.querySelectorAll('.edit-trigger').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.input-group');
            container.querySelector('.static-value').style.display = 'none';
            container.querySelector('.edit-controls').style.display = 'block';
            this.style.display = 'none';
            container.querySelector('.form-input').focus();
        });
    });
    
    // Cancel edit
    document.querySelectorAll('.cancel-edit').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.input-group');
            container.querySelector('.static-value').style.display = 'block';
            container.querySelector('.edit-controls').style.display = 'none';
            container.querySelector('.edit-trigger').style.display = 'inline-flex';
        });
    });
    
    // Toggle password form
    document.getElementById('password-toggle').addEventListener('click', function() {
        const form = this.closest('.form-group').querySelector('.password-form');
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });
    
    // Cancel password change
    document.querySelector('.cancel-password')?.addEventListener('click', function() {
        this.closest('.password-form').style.display = 'none';
    });
    
    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
    
    // Password strength meter
    document.getElementById('new-password')?.addEventListener('input', function() {
        const password = this.value;
        const strengthBar = this.closest('.form-group').querySelector('.strength-bar');
        const strengthText = this.closest('.form-group').querySelector('.strength-text');
        
        // Calculate strength
        let strength = 0;
        if (password.length > 0) strength += 20;
        if (password.length >= 8) strength += 20;
        if (/[A-Z]/.test(password)) strength += 20;
        if (/[0-9]/.test(password)) strength += 20;
        if (/[^A-Za-z0-9]/.test(password)) strength += 20;
        
        // Update UI
        strengthBar.style.width = `${strength}%`;
        
        if (strength < 40) {
            strengthBar.style.backgroundColor = 'var(--danger)';
            strengthText.textContent = 'Weak password';
        } else if (strength < 80) {
            strengthBar.style.backgroundColor = 'var(--warning)';
            strengthText.textContent = 'Moderate password';
        } else {
            strengthBar.style.backgroundColor = 'var(--success)';
            strengthText.textContent = 'Strong password';
        }
    });
    
    // Save changes (simplified example)
    document.querySelectorAll('.save-edit').forEach(button => {
        button.addEventListener('click', function() {
            // In a real app, you would send this to your backend
            const input = this.closest('.edit-controls').querySelector('.form-input');
            const value = input.value;
            const field = input.id.replace('-input', '');
            
            // Update the displayed value
            const valueSpan = document.getElementById(`${field}-value`);
            valueSpan.textContent = value || 'Not provided';
            
            // Hide edit controls
            this.closest('.edit-controls').style.display = 'none';
            valueSpan.style.display = 'block';
            this.closest('.input-group').querySelector('.edit-trigger').style.display = 'inline-flex';
            
            // Show success feedback
            alert(`${field.charAt(0).toUpperCase() + field.slice(1)} updated successfully!`);
        });
    });
});
