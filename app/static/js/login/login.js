document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const identifierInput = document.getElementById('identifier');
    const identifierError = document.getElementById('identifier-error');
    const passwordError = document.getElementById('password-error');

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
        
        if (!validateForm()) return;
        
        try {
            const formData = new FormData(loginForm);
            const response = await fetch(loginForm.action, {
                method: 'POST',
                body: formData,
                headers: getHeaders(false),
            });

            const data = await response.json();
            
            if (!response.ok) {
                showAlert(data.data ,data.message ,3500);
            } else{
                showAlert(data.data,data.message ,3000)
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
        
        // Validate identifier
        if (!identifierInput.value.trim()) {
            identifierInput.classList.add('input-error', 'shake');
            identifierError.style.display = 'block';
            isValid = false;
        }
        
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
