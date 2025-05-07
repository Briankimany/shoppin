document.addEventListener('DOMContentLoaded', async () => {
    // Initialize components
    prodRenderer = new ProductRenderer();
 
    window.renderProducts = ProductRenderer.renderProducts;
    await FilterManager.loadFilters();
    await loadProducts();
    
    // Event listeners
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('search-btn').addEventListener('click', searchProducts);
    document.getElementById('search-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') searchProducts();
    });
  
    // // Delegated event for pagination
    // document.getElementById('pagination').addEventListener('click', (e) => {
    //   if (e.target.closest('.page-link')) {
    //     e.preventDefault();
    //     loadProducts(parseInt(e.target.dataset.page));
    //   }
    // });
  });

  async function loadProducts() {

    const response = await fetch('/products/q');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    console.log('Received products:', data.data.length);
    console.log(data.meta);

    ProductRenderer.renderProducts(data.data);
    ProductMetaTracker.update(data.meta);
  
    // Pagination.render(meta);
  }
  
  async function applyFilters() {
    // Build filter query from checkboxes
    const params = new URLSearchParams();
    document.querySelectorAll('#filters-container input:checked').forEach(input => {
      params.append(input.id.split('-')[0], input.value);
    });
    const url = `/products/q?${params.toString()}`;
    const response = await fetch(url);
    const { data, meta } = await response.json();
    ProductRenderer.renderProducts(data);
    // Pagination.render(meta);
  }
  
  async function searchProducts() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;
  
    const response = await fetch(`/products/search?q=${query}`);
    const { data } = await response.json();
    ProductRenderer.renderProducts(data);
    document.getElementById('pagination').innerHTML = '';
  }

  function createProductCountTracker() {
    let tracker = document.getElementById('product-count-tracker');
    if (!tracker) {
        tracker = document.createElement('div');
        tracker.id = 'product-count-tracker';
        tracker.style.display = 'none';
        tracker.dataset.count = '0'; // Use dataset for structured access
        document.body.appendChild(tracker);
    }
}
