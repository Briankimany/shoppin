
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('registerForm');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const identifierInput = document.getElementById('identifier');
    const identifierError = document.getElementById('identifier-error');
    const passwordError = document.getElementById('password-error');

    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const requirements = {
        length: document.getElementById('length-req'),
        uppercase: document.getElementById('uppercase-req'),
        number: document.getElementById('number-req'),
        special: document.getElementById('special-req')
    };


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

    // Toggle password visibility (unchanged)
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

    // New fetch-based form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
       
        
        try {
            const formData = new FormData(loginForm);
            const response = await fetch(loginForm.action, {
                method: 'POST',
                body: formData,
                headers: getHeaders(false),
            });

            if (!response.ok) {
                const error = await response.json();
                showAlert(error.data ,error.message ,3500);
            }
            const data = await response.json();
            showAlert(data.data,data.message ,5000)
           
            if (data.url){
                window.location.href = data.url;
            }
           
        
        } catch (error) {
            showAlert("Error "+error, type='error' ,duration = 3500);
            console.error('Login error:', error);
        }
    });

    // Extracted validation function
    function validateForm() {
        let isValid = true;
        
   
        // Validate password
        if (!passwordInput.value.trim()) {
            passwordInput.classList.add('input-error', 'shake');
            passwordError.style.display = 'block';
            isValid = false;
        }
        
        // Remove shake animation after it completes
        [identifierInput, passwordInput].forEach(input => {
            input.addEventListener('animationend', () => {
                input.classList.remove('shake');
            }, { once: true });
        });
        
        return isValid;
    }

    // Clear errors when typing (unchanged)
    identifierInput.addEventListener('input', clearError.bind(null, identifierInput, identifierError));
    passwordInput.addEventListener('input', clearError.bind(null, passwordInput, passwordError));
    
    function clearError(input, errorElement) {
        if (input.value.trim()) {
            input.classList.remove('input-error');
            errorElement.style.display = 'none';
        }
    }
});
