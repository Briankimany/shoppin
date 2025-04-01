
    // dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Sparkline Chart
    const sparkline = document.querySelector('.revenue-sparkline');
    if (sparkline) {
        const dates = sparkline.dataset.dates.split(',');
        const amounts = sparkline.dataset.amounts.split(',').map(Number);
        
        renderSparkline(sparkline, dates, amounts);
    }

    // Auto-refresh every 60 seconds
    setInterval(refreshDashboard, 60000);
});

function renderSparkline(container, dates, amounts) {
    // Simple SVG implementation - replace with Chart.js if preferred
    const maxAmount = Math.max(...amounts);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    let pathData = '';
    
    amounts.forEach((amount, i) => {
        const x = (i / (amounts.length - 1)) * 100;
        const y = 100 - (amount / maxAmount) * 90;
        pathData += `${i === 0 ? 'M' : 'L'} ${x}% ${y}% `;
    });
    
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', '#4361ee');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    svg.appendChild(path);
    
    container.innerHTML = '';
    container.appendChild(svg);
}

function refreshDashboard() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            document.querySelector('.dashboard-container').innerHTML = 
                newDoc.querySelector('.dashboard-container').innerHTML;
            
            document.querySelector('.last-updated').innerHTML = 
                '<i class="fas fa-sync-alt"></i> Updated just now';
        });
}

// Ensure sidebar state persists
document.addEventListener('DOMContentLoaded', () => {
    const mainNav = document.getElementById('mainNav');
    
    // Sync collapsed state
    if(localStorage.getItem('vendorNavCollapsed') === 'true') {
      mainNav.classList.add('collapsed');
      document.documentElement.style.setProperty(
        '--sidebar-width', 
        localStorage.getItem('sidebarCollapsed') || '80px'
      );
    }
  
    // Update layout on resize
    window.addEventListener('resize', () => {
      const contentWidth = window.innerWidth - mainNav.offsetWidth;
      document.querySelector('.dashboard-container').style.maxWidth = 
        `${contentWidth}px`;
    });
  });