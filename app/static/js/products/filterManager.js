class FilterManager {
    static async loadFilters() {
      const response = await fetch('/products/filters');
      const { data } = await response.json();
      this.renderFilters(data);
      this.setupMobileFilterApplyHandler();
    }
  
    static renderFilters(filters) {
      const container = document.getElementById('filters-container');
      
      Object.entries(filters).forEach(([filterName, values]) => {
        container.innerHTML += `
          <div class="collapse-card mt-3">
            <div class="collapse-header" data-bs-toggle="collapse" data-bs-target="#${filterName}-filter">
              <h6 class="mb-0">${this.capitalize(filterName)}</h6>
              <i class="ni ni-bold-down collapse-arrow"></i>
            </div>
            <div id="${filterName}-filter" class="collapse hide">
              <div class="collapse-body">
                ${values.map(value => `
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${filterName}-${value}" value="${value}">
                    <label class="form-check-label" for="${filterName}-${value}">${value}</label>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        `;
      });
      this.syncToMobileFilters();

    }
  
    static capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }

    static resetFilters() {
      const checkboxes = document.querySelectorAll('#filters-container input[type="checkbox"]');
      checkboxes.forEach(cb => cb.checked = false);
      this.handleFilterChange(); // Re-trigger filter logic after reset
    }

    static syncToMobileFilters() {
      const desktopFilters = document.getElementById('filters-container');
      const mobileFilters = document.getElementById('mobile-filters-container');
      if (!desktopFilters || !mobileFilters) return;
    
      // Clone the filters HTML to the mobile container
      mobileFilters.innerHTML = desktopFilters.innerHTML;
    
    }

    static setupMobileFilterApplyHandler() {
      const applyBtn = document.getElementById('mobile-apply-filters');
      if (!applyBtn) return;
    
      applyBtn.addEventListener('click', () => {
        const checkboxes = document.querySelectorAll('#mobile-filters-container input[type="checkbox"]');
        
        // Sync mobile checkboxes with desktop
        checkboxes.forEach(mcb => {
          const id = mcb.id;
          const desktopCb = document.querySelector(`#filters-container #${id}`);
          if (desktopCb) desktopCb.checked = mcb.checked;
        });
    
       ProductRenderer.applyFilters();
    
        const modal = bootstrap.Modal.getInstance(document.getElementById('mobileFiltersModal'));
        if (modal) modal.hide();
      });
    }
    
}

async function applyFilters() {
 
  const params = new URLSearchParams();
  document.querySelectorAll('#filters-container input:checked').forEach(input => {
    params.append(input.id.split('-')[0], input.value);
  });
  const url = `/products/q?${params.toString()}`;
  const response = await fetch(url);
  const { data, meta } = await response.json();
  ProductRenderer.renderProducts(data);

}

document.addEventListener('DOMContentLoaded', async () => {
  await FilterManager.loadFilters();

  const btn = document.getElementById('apply-filters');
  if (btn) {
    btn.addEventListener('click', applyFilters);
  }

});