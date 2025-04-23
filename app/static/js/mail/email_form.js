

document.addEventListener('DOMContentLoaded', function() {
const emailForm = document.getElementById('emailForm');

const sendBtn = document.getElementById('sendBtn');
const originalHTML = sendBtn.innerHTML;

function disableButton() {
    sendBtn.disabled = true;
    sendBtn.style.opacity = 0.7;
    sendBtn.style.cursor = 'not-allowed';
    sendBtn.innerHTML = `
        <span class="spinner" style="margin-right: 8px;"></span>
        Sending...
    `;
}

function enableButton() {
    sendBtn.disabled = false;
    sendBtn.style.opacity = 1;
    sendBtn.style.cursor = 'pointer';
    sendBtn.innerHTML = originalHTML;
}

emailForm.addEventListener('submit', async function(e) {
e.preventDefault();

try {
    // Get form data
    const formData = new FormData(emailForm);
   
    // Send via fetch
    disableButton();
    const response = await fetch(emailForm.action, {
        method: 'POST',
        body: formData,
        headers:getHeaders(false)
    });
    
    if (!response.ok) {
        const error = await response.json();
        showAlert(error.message || 'Failed to send email' ,'error');
    }
    
    const result = await response.json();
    showAlert('Email sent successfully!', 'success');
    enableButton();
} catch (error) {
    console.error('Error:', error);
    showAlert(error.message, 'error');
}
});
});

