
document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("search-form");
    const searchMessage = document.getElementById("search-message");

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault(); 
        searchMessage.style.display = "block";
    });
});

function getCsrfToken(){
    return document.querySelector('meta[name="csrf-token"]').content;
    }

function getHeaders(get_content_type=true){
    if (!get_content_type){
        return {'X-CSRFToken': getCsrfToken()}
    }
     return {
        'X-CSRFToken': getCsrfToken(),
        'Content-Type': 'application/json'
      };
}

  
function showAlert(message, type = 'success' ,duration=5000) {
    const alertContainer = document.getElementById('alert-container');
    const alertId = Date.now();
    
    const alertEl = document.createElement('div');
    alertEl.className = `alert ${type}`;
    alertEl.id = `alert-${alertId}`;
    
    const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        warning: 'fa-triangle-exclamation'
    };
    
    alertEl.innerHTML = `
        <i class="fas ${icons[type] || 'fa-info-circle'} alert-icon"></i>
        <div class="alert-message">${message}</div>
        <button class="alert-close" onclick="dismissAlert('${alertId}')">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alertContainer.appendChild(alertEl);
    
    setTimeout(() => {
        alertEl.classList.add('show');
    }, 10);
    
   
    setTimeout(() => {
        dismissAlert(alertId);
    }, duration);
}

function dismissAlert(id) {
    const alertEl = document.getElementById(`alert-${id}`);
    if (alertEl) {
        alertEl.classList.remove('show');
        setTimeout(() => {
            alertEl.remove();
        }, 300);
    }
}


function disableButtonWithSpinner(button) {
    button.disabled = true;
    button.style.opacity = 0.7;
    button.style.cursor = 'not-allowed';
    button.dataset.originalHtml = button.innerHTML;

    button.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="9" cy="21" r="1"></circle>
        <circle cx="20" cy="21" r="1"></circle>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
    </svg>
    Add to Cart
`;
}

function enableButton(button) {
    button.disabled = false;
    button.style.opacity = 1;
    button.style.cursor = 'pointer';

    if (button.dataset.originalHtml) {
        button.innerHTML = button.dataset.originalHtml;
    }
}

const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .animate-spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
