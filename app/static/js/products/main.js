
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
        tracker.dataset.count = '0';
        document.body.appendChild(tracker);
    }
}


function initEventListeners() {
  setupSearchButtonListener();
  setupSearchEnterListener();
 
}


function setupSearchButtonListener() {
  const btn = document.getElementById('search-btn');
  if (btn) {
    btn.addEventListener('click', searchProducts);
  }
}

function setupSearchEnterListener() {
  const input = document.getElementById('search-input');
  if (input) {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') searchProducts();
    });
  }
}


document.addEventListener('DOMContentLoaded', async () => {
  // document.getElementById('apply-filters').addEventListener('click', applyFilters);
  // document.getElementById('search-btn').addEventListener('click', searchProducts);
  // document.getElementById('search-input').addEventListener('keypress', (e) => {
  //   if (e.key === 'Enter') searchProducts();
  // });
  initEventListeners();
  createProductCountTracker();

});


