
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const identifierInput = document.getElementById('identifier');
    const identifierError = document.getElementById('identifier-error');
    const passwordError = document.getElementById('password-error');

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

    // Form validation
    loginForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Validate identifier
        if (!identifierInput.value.trim()) {
            identifierInput.classList.add('input-error');
            identifierError.style.display = 'block';
            identifierInput.classList.add('shake');
            isValid = false;
        } else {
            identifierInput.classList.remove('input-error');
            identifierError.style.display = 'none';
        }
        
        // Validate password
        if (!passwordInput.value.trim()) {
            passwordInput.classList.add('input-error');
            passwordError.style.display = 'block';
            passwordInput.classList.add('shake');
            isValid = false;
        } else {
            passwordInput.classList.remove('input-error');
            passwordError.style.display = 'none';
        }
        
        // Remove shake animation after it completes
        const inputs = [identifierInput, passwordInput];
        inputs.forEach(input => {
            input.addEventListener('animationend', () => {
                input.classList.remove('shake');
            }, { once: true });
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });

    // Clear errors when typing
    identifierInput.addEventListener('input', function() {
        if (this.value.trim()) {
            this.classList.remove('input-error');
            identifierError.style.display = 'none';
        }
    });
    
    passwordInput.addEventListener('input', function() {
        if (this.value.trim()) {
            this.classList.remove('input-error');
            passwordError.style.display = 'none';
        }
    });
});
