class ProductDetailRenderer {
    constructor() {
      this.id = document.getElementById("current-product-id").dataset.value;
      this.fields = document.getElementById("specific-product-fields").dataset.value;
      this.apiUrl = `/products/p/details?id=${this.id}&${this.fields}`;
      this.colors = {
        primary: '#2c3e50',      // Dark blue-gray - professional primary color
        secondary: '#7f8c8d',    // Gray - neutral secondary color
        accent: '#3498db',       // Bright blue - for CTAs and highlights
        danger: '#e74c3c',       // Red - for discounts/important notices
        background: '#f8f9fa'    // Light gray - clean background
      };
    }
  
    async init() {
      try {
        const data = await this.fetchProductData();
        this.renderMainProduct(data.product_data);
        bindCartEvents();
        
        this.renderSuggestedProducts(data.sugessted_products.data);
        this.updateMetadata(data.sugessted_products.meta.total);
      } catch (err) {
        this.handleError(err);
      }
    }
  
    async fetchProductData() {
      const response = await fetch(this.apiUrl);
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return await response.json();
    }
  
    renderMainProduct(product) {
      document.getElementById('product-details-container').innerHTML = `
        <div class="col-lg-6 p-4">
          <div class="position-relative" style="height: 400px;">
            <img src="${product.image_src}" 
                 alt="${product.name}" 
                 class="img-fluid h-100 object-fit-contain"
                 loading="lazy">
          </div>
        </div>
        <div class="col-lg-6 p-4">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb bg-transparent px-0">
              <li class="breadcrumb-item">
                <a href="/products/categories/${product.category}">${product.category}</a>
              </li>
              <li class="breadcrumb-item active">${product.name}</li>
            </ol>
          </nav>
          
          <h1 class="h2 mb-3">${product.name}</h1>
          
          <div class="d-flex align-items-center mb-4">
            <span class="h4" style="color: ${this.colors.accent}">$${parseFloat(product.price).toFixed(2)}</span>
            ${product.discount ? `
              <span class="text-muted text-decoration-line-through me-2">
                $${parseFloat(product.original_price).toFixed(2)}
              </span>
              <span class="badge" style="background-color: ${this.colors.danger}">${product.discount}% OFF</span>
            ` : ''}
          </div>
          
          <div class="mb-4">
            ${product.attribute_values.map(attr => `
              <div class="mb-2">
                <strong style="color: ${this.colors.primary}">${attr.attribute_types[0]}:</strong>
                <span class="ms-2" style="color: ${this.colors.secondary}">${attr.value}${attr.unit ? ` ${attr.unit}` : ''}</span>
              </div>
            `).join('')}
          </div>
          
    <div class="d-flex gap-2 mt-auto">
    <!-- Add to Cart Button (unchanged class structure) -->
    <button class="btn flex-grow-1 py-3 add-to-cart-btn" 
            style="background-color: ${this.colors.accent}; color: white"
            data-product-id="${product.hiden_id}">
      <i class="ni ni-cart me-2"></i> Add to Cart
    </button>

    <!-- Product Actions (unchanged outer container class) -->
    <div class="product-actions">
      <!-- Quantity Selector (maintaining original classes) -->
      <div class="quantity-selector d-flex align-items-center me-2"> <!-- Added Bootstrap spacing -->
        <button class="qty-btn minus btn btn-outline-secondary px-2">-</button> <!-- Enhanced -->
        <input type="number" 
              class="quantity-input form-control mx-1 text-center" 
              style="width: 50px;"
              id="quantity-${product.hiden_id}" 
              value="1" 
              min="1">
        <button class="qty-btn plus btn btn-outline-secondary px-2">+</button> <!-- Enhanced -->
      </div>

      <!-- Wishlist Button (unchanged structure) -->
      <button class="btn btn-outline-secondary">
        <i class="ni ni-favourite-28"></i>
      </button>
    </div>
  </div>

      `;
    }
  
    renderSuggestedProducts(products) {
      document.getElementById('suggested-products-grid').innerHTML = products.map(prod => `
        <div class="col">
          <div class="card h-100 product-card">
            <div class="position-relative" style="height: 200px;">
              <img src="${prod.image_src}" 
                   class="card-img-top h-100 object-fit-contain p-3" 
                   alt="${prod.name}"
                   loading="lazy">
              ${prod.discount ? `
                <span class="badge position-absolute top-0 end-0 m-2" style="background-color: ${this.colors.danger}">
                  ${prod.discount}% OFF
                </span>
              ` : ''}
            </div>
            <div class="card-body d-flex flex-column">
              <h3 class="h5 card-title" style="color: ${this.colors.primary}">${prod.name}</h3>
              <div class="mt-auto">
                <div class="d-flex align-items-center mb-2">
                  <span class="fw-bold" style="color: ${this.colors.accent}">$${parseFloat(prod.price).toFixed(2)}</span>
                  ${prod.original_price ? `
                    <small class="text-muted text-decoration-line-through ms-2">
                      $${parseFloat(prod.original_price).toFixed(2)}
                    </small>
                  ` : ''}
                </div>
                <a href="/products/product/${prod.hiden_id}" 
                   class="btn btn-sm w-100" 
                   style="border-color: ${this.colors.accent}; color: ${this.colors.accent}">
                  View Details
                </a>
              </div>
            </div>
          </div>
        </div>
      `).join('');
    }
  
    updateMetadata(total) {
      const tracker = document.getElementById('specific-product-count-tracker');
      tracker.dataset.count = document.querySelectorAll('#suggested-products-grid .col').length;
      tracker.dataset.total = total;
    }
  
    handleError(err) {
      console.error('Failed to fetch product data', err);
      document.getElementById('product-details-container').innerHTML = `
        <div class="col-12 text-center py-5">
          <div class="alert alert-danger">
            Failed to load product details. 
            <button class="btn btn-link p-0" onclick="window.location.reload()">Try again</button>
          </div>
        </div>
      `;
    }
  }
  
  
  document.addEventListener('DOMContentLoaded', () => {
    const productRenderer = new ProductDetailRenderer();
    productRenderer.init();
  });