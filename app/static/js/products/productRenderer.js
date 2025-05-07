class ProductRenderer {
  constructor(meta = {}) {
    this.totalProducts = meta.totalProducts || 0;
    this.perPage = meta.per_page || 0;
    this.productsRendered = 0; // Track rendered products count
  }

  updateMeta(meta) {
    this.totalProducts = meta.totalProducts || this.totalProducts;
    this.perPage = meta.per_page || this.perPage;
    return this;
  }

  static renderProduct(product) {
    const priceFormatted = (product.price/1).toFixed(2);
    const originalPrice = product.original_price ? (product.original_price/1).toFixed(2) : null;
    const discount = product.discount ? `${product.discount}% OFF` : null;

    return `
    <div class="col-md-4 mb-4 product-item" data-product-id="${product.id}">
      <div class="card h-100 hover-scale shadow-sm border-light">
        <div class="card-img-container position-relative overflow-hidden" style="height: 200px;">
          <img src="${product.image_src || '/static/assets/img/placeholder-product.jpg'}" 
               class="img-fluid w-100 h-100 object-fit-cover border-radius-top" 
               alt="${product.name}"
               loading="lazy">
          
          <!-- Price Badge -->
          <div class="position-absolute top-0 end-0 m-2 d-flex flex-column align-items-end">
            ${originalPrice ? `
              <span class="badge bg-light text-dark text-decoration-line-through mb-1">
                $${originalPrice}
              </span>
            ` : ''}
            <span class="badge bg-dark text-white">
              Price: $${priceFormatted}
            </span>
            ${discount ? `
              <span class="badge bg-danger mt-1">
                ${discount}
              </span>
            ` : ''}
          </div>
        </div>
        
        <div class="card-body d-flex flex-column">
          <h5 class="card-title mb-2 text-dark">${product.name}</h5>
          <small class="text-muted mb-2">ID: ${product.id}</small>
          
          <div class="attributes mb-3">
            ${product.attribute_values.map(attr => `
              <span class="badge bg-light text-dark border me-1 mb-1">
                ${attr.attribute_types[0]}: ${attr.value}${attr.unit ? ` ${attr.unit}` : ''}
              </span>
            `).join('')}
          </div>
          
          <div class="d-flex mt-auto">
            <a href="/products/product/${product.hiden_id}" 
               class="btn btn-sm btn-outline-dark flex-grow-1 me-2">
              <i class="ni ni-zoom-split me-1"></i> Details
            </a>
            <button class="btn btn-sm btn-dark" onclick="openQuickView(${product.hiden_id})">
              <i class="ni ni-album-2 me-1"></i> Quick View
            </button>
          </div>
        </div>
      </div>
    </div>`;
  }

  static renderProducts(products, addProd = false) {
    const container = document.getElementById('products-grid');
    const count = products.length;
    
    if (addProd) {
      container.innerHTML += products.map(product => this.renderProduct(product)).join('');
    } else {
      container.innerHTML = products.map(product => this.renderProduct(product)).join('');
      this.resetProductCount();
    }
    
    this.incrementProductCount(count);
    this.updateProductStats();
    
    const trigger = document.getElementById('infinite-scroll-loader');
    if (trigger) trigger.classList.remove('hidden');
  }

  static updateProductStats() {
    const totalElement = document.getElementById('products-total-count');
    const renderedElement = document.getElementById('products-rendered-count');
    
    if (totalElement) {
      totalElement.textContent = ProductRenderer.getTotalProductCount();
    }
    if (renderedElement) {
      renderedElement.textContent = ProductRenderer.getProductCount();
    }
  }

  static incrementProductCount(amount) {
    const tracker = document.getElementById('product-count-tracker');
    if (tracker) {
      let current = parseInt(tracker.dataset.count || '0', 10);
      tracker.dataset.count = (current + amount).toString();
    }
  }

  static resetProductCount() {
    const tracker = document.getElementById('product-count-tracker');
    if (tracker) {
      tracker.dataset.count = '0';
    }
  }

  static getProductCount() {
    const tracker = document.getElementById('product-count-tracker');
    return tracker ? parseInt(tracker.dataset.count || '0', 10) : 0;
  }

  static getTotalProductCount() {
    const tracker = document.getElementById('product-count-tracker');
    return tracker ? parseInt(tracker.dataset.total || '0', 10) : 0;
  }

  static setTotalProductCount(count) {
    const tracker = document.getElementById('product-count-tracker');
    if (tracker) {
      tracker.dataset.total = count.toString();
    }
  }

  static async applyFilters() {
    // Build filter query from checkboxes
    const params = new URLSearchParams();
    document.querySelectorAll('#filters-container input:checked').forEach(input => {
      params.append(input.id.split('-')[0], input.value);
    });
    const url = `/products/q?${params.toString()}`;
    const response = await fetch(url);
    const { data, meta } = await response.json();
    this.renderProducts(data);
    // Pagination.render(meta);
  }
}