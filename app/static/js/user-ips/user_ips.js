
(async function() {

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
    
    function hasIpBeenUpdated() {

        const serverSideIndicator = document.querySelector('meta[name="ip-updated"]');
        if (serverSideIndicator && serverSideIndicator.content === 'true') {
            return true;
        }
        
        return false;
    }

    function getConsent() {
        return new Promise((resolve) => {
          
            const modal = document.createElement('div');
            modal.id = 'ip-consent-modal';
            modal.className = 'consent-modal';
            
            modal.innerHTML = `
                <div class="consent-content">
                    <div class="consent-text">
                        <h3 class="consent-title">We Value Your Privacy</h3>
                        <p class="consent-message">
                            We collect certain data to enhance security and improve our services. By continuing, 
                            you consent to this data collection. You may choose to accept or decline.
                        </p>
                    </div>
                    <div class="consent-buttons">
                        <button id="consent-decline" class="consent-btn decline-btn">
                            Decline
                        </button>
                        <button id="consent-accept" class="consent-btn accept-btn">
                            Accept
                        </button>
                    </div>
                </div>
            `;
    
            document.body.appendChild(modal);
            
         
            void modal.offsetWidth;
            modal.classList.add('visible');
    
        
            document.getElementById('consent-accept').addEventListener('click', () => {
                dismissModal();
                localStorage.setItem('ipConsent', 'true');
                resolve(true);
            });
    
            document.getElementById('consent-decline').addEventListener('click', () => {
                dismissModal();
                localStorage.setItem('ipConsent', 'false');
                resolve(false);
            });
    
            function dismissModal() {
                modal.classList.remove('visible');
                setTimeout(() => {
                    document.body.removeChild(modal);
                }, 300); 
            }
        });
    }

 
    async function updateIpData() {
        try {
            const response = await fetch('/ips/update', {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({ ips: null })
            });

            if (response.ok) {
                const data = await response.json();
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    document.addEventListener('DOMContentLoaded', async function() {
        if (hasIpBeenUpdated()) {
            return;
        }

        const hasConsent = localStorage.getItem('ipConsent') === 'true';
        const refusedConsent = localStorage.getItem('ipConsent') === 'false';

        if (refusedConsent){
            return;
        }
        const consentGiven = hasConsent || await getConsent();

        if (consentGiven) {
            await updateIpData();
        }
    });
})();