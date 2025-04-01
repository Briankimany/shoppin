

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const requirements = {
        length: document.getElementById('length-req'),
        uppercase: document.getElementById('uppercase-req'),
        number: document.getElementById('number-req'),
        special: document.getElementById('special-req')
    };

    // Toggle password visibility
    togglePassword.addEventListener('click', function() {
        const icon = this.querySelector('i');
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.replace('fa-eye-slash', 'fa-eye');
        }
    });

    // Password strength checker
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;
        
        // Check password requirements
        const hasLength = password.length >= 8;
        const hasUppercase = /[A-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        
        // Update requirement indicators
        requirements.length.classList.toggle('met', hasLength);
        requirements.length.classList.toggle('unmet', !hasLength);
        requirements.uppercase.classList.toggle('met', hasUppercase);
        requirements.uppercase.classList.toggle('unmet', !hasUppercase);
        requirements.number.classList.toggle('met', hasNumber);
        requirements.number.classList.toggle('unmet', !hasNumber);
        requirements.special.classList.toggle('met', hasSpecial);
        requirements.special.classList.toggle('unmet', !hasSpecial);
        
        // Calculate strength
        if (hasLength) strength += 25;
        if (hasUppercase) strength += 25;
        if (hasNumber) strength += 25;
        if (hasSpecial) strength += 25;
        
        // Update strength meter
        strengthBar.style.width = `${strength}%`;
        
        // Update strength text
        if (strength < 40) {
            strengthBar.style.backgroundColor = 'var(--error)';
            strengthText.textContent = 'Weak password';
        } else if (strength < 80) {
            strengthBar.style.backgroundColor = 'var(--warning)';
            strengthText.textContent = 'Moderate password';
        } else {
            strengthBar.style.backgroundColor = 'var(--success)';
            strengthText.textContent = 'Strong password';
        }
    });

    // Form validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Validate username
        const nameInput = document.getElementById('name');
        if (!nameInput.value.trim()) {
            showError(nameInput, 'name-error', 'Please enter a username');
            isValid = false;
        } else if (nameInput.value.length < 3) {
            showError(nameInput, 'name-error', 'Username must be at least 3 characters');
            isValid = false;
        }
        
        // Validate email
        const emailInput = document.getElementById('email');
        if (!emailInput.value.trim()) {
            showError(emailInput, 'email-error', 'Please enter an email address');
            isValid = false;
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value)) {
            showError(emailInput, 'email-error', 'Please enter a valid email address');
            isValid = false;
        }
        
        // Validate password
        if (!passwordInput.value.trim()) {
            showError(passwordInput, 'password-error', 'Please enter a password');
            isValid = false;
        } else if (passwordInput.value.length < 8) {
            showError(passwordInput, 'password-error', 'Password must be at least 8 characters');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });

    // Clear errors when typing
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('input', function() {
            const errorId = this.id + '-error';
            const errorElement = document.getElementById(errorId);
            if (errorElement) {
                this.classList.remove('is-invalid', 'shake');
                errorElement.style.display = 'none';
            }
        });
    });

    function showError(input, errorId, message) {
        input.classList.add('is-invalid', 'shake');
        const errorElement = document.getElementById(errorId);
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Remove shake animation after it completes
        input.addEventListener('animationend', () => {
            input.classList.remove('shake');
        }, { once: true });
    }
});
