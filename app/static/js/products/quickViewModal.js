class QuickView {
    constructor() {
      this.modalElement = document.getElementById('quickViewModal');
      this.modal = new bootstrap.Modal(this.modalElement);
      this.initializeEventListeners();
    }
  
    initializeEventListeners() {
      // Close button event
      this.modalElement.querySelector('.btn-close').addEventListener('click', () => this.close());
      
      // Quantity input validation
      this.modalElement.addEventListener('change', (e) => {
        if (e.target.matches('.quick-view-qty')) {
          this.validateQuantity(e.target);
        }
      });
    }
  
    async open(productId) {
      try {
        // Show loading state
        this.showLoading(true);
        
        const productData = await this.fetchProductData(productId);
        this.renderProductDetails(productData);
        
        // Show the modal after content is loaded
        this.modal.show();
        
        // Initialize carousel if needed
        if (productData.images?.length > 1) {
          this.initCarousel();
        }
      } catch (error) {
        console.error('QuickView Error:', error);
        this.showError('Failed to load product details');
      } finally {
        this.showLoading(false);
      }
    }
  
    close() {
      this.modal.hide();
    }
  
    async fetchProductData(productId) {
      const response = await fetch(`/products/p/details?id=${productId}`);
      if (!response.ok) {
        throw new Error(`Product fetch failed (${response.status})`);
      }
      const { data } = await response.json();
      return data;
    }
  
    renderProductDetails(data) {
      // 1. Product Gallery
      document.getElementById('quickViewGallery').innerHTML = this.generateImageGallery(data);
      
      // 2. Product Header
      document.getElementById('quickViewTitle').innerHTML = this.generateProductHeader(data);
      
      // 3. Pricing Section
      document.getElementById('quickViewPricing').innerHTML = this.generatePricingHTML(data);
      
      // 4. Variant Selection
      document.getElementById('quickViewAttributes').innerHTML = this.generateVariantOptions(data);
      
      // 5. Add to Cart Section
      document.getElementById('quickViewAddToCart').innerHTML = this.generateAddToCartHTML(data);
      
      // 6. Product Description (if available)
      if (data.description) {
        document.getElementById('quickViewDescription').innerHTML = this.generateDescriptionHTML(data);
      }

      // 7. Bind cart items to the butttons
      bindCartEvents();
    }
  
    generateImageGallery(data) {
      const images = data.images?.length ? data.images : [data.image_src || '/static/assets/img/placeholder.jpg'];
      const carouselId = 'quickViewCarousel';
      
      return `
        <div id="${carouselId}" class="carousel slide" data-bs-ride="carousel">
          <div class="carousel-inner ratio ratio-1x1 bg-light rounded">
            ${images.map((img, i) => `
              <div class="carousel-item ${i === 0 ? 'active' : ''}">
                <img src="${img}" 
                     class="d-block w-100 h-100 object-fit-contain" 
                     alt="${data.name}"
                     loading="lazy">
              </div>
            `).join('')}
          </div>
          ${images.length > 1 ? `
            <button class="carousel-control-prev" type="button" data-bs-target="#${carouselId}" data-bs-slide="prev">
              <span class="carousel-control-prev-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#${carouselId}" data-bs-slide="next">
              <span class="carousel-control-next-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Next</span>
            </button>
          ` : ''}
        </div>
        
        <!-- Thumbnails -->
        <div class="d-flex flex-wrap gap-2 mt-3">
          ${images.map((img, i) => `
            <button type="button" 
                    class="thumbnail-btn p-0 border ${i === 0 ? 'border-primary' : 'border-light'}" 
                    data-bs-target="#${carouselId}" 
                    data-bs-slide-to="${i}"
                    aria-label="Slide ${i + 1}">
              <img src="${img}" width="60" height="60" class="object-fit-cover" alt="Thumbnail">
            </button>
          `).join('')}
        </div>
      `;
    }
  
    generateProductHeader(data) {
      return `
        <h2 class="h4 mb-2">${data.name}</h2>
        <div class="d-flex align-items-center mb-3">
          <span class="badge bg-${data.in_stock ? 'success' : 'danger'} me-2">
            ${data.in_stock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>
      `;
    }
  
    generatePricingHTML(data) {
      const discount = this.calculateDiscount(data);
      
      return `
        <div class="d-flex align-items-center flex-wrap gap-2 mb-3">
          <span class="h4 text-primary mb-0">$${parseFloat(data.price).toFixed(2)}</span>
          ${data.original_price ? `
            <del class="text-muted">$${parseFloat(data.original_price).toFixed(2)}</del>
            <span class="badge bg-danger">${discount}% OFF</span>
          ` : ''}
        </div>
      `;
    }
  
    generateVariantOptions(data) {
      if (!data.attributes || Object.keys(data.attributes).length === 0) return '';
      
      return Object.entries(data.attributes).map(([attribute, values]) => `
        <div class="mb-3">
          <h6 class="small text-uppercase text-muted mb-2">${attribute}</h6>
          <div class="d-flex flex-wrap gap-2">
            ${values.map(value => `
              <button type="button" 
                      class="btn btn-sm ${this.isSelectedVariant(data, attribute, value) ? 
                        'btn-primary' : 'btn-outline-secondary'} variant-option"
                      data-attribute="${attribute}"
                      data-value="${value}">
                ${value}
              </button>
            `).join('')}
          </div>
        </div>
      `).join('');
    }
  
    isSelectedVariant(data, attribute, value) {
      return data.attribute_values.some(
        attr => attr.attribute_types.includes(attribute) && attr.value === value
      );
    }
  
    generateAddToCartHTML(data) {
      return `
      <div class="d-flex gap-3 mt-auto align-items-stretch flex-wrap flex-md-nowrap">
        
        <!-- Add to Cart Button -->
        <button class="btn btn-primary flex-grow-1 py-3 px-4 add-to-cart-btn shadow-sm"
                data-product-id="${data.hiden_id}">
          <i class="ni ni-cart me-2"></i> Add to Cart
        </button>
    
        <!-- Product Actions -->
        <div class="product-actions d-flex gap-2 align-items-stretch">
          
          <!-- Quantity Selector -->
          <div class="quantity-selector input-group border border-secondary rounded overflow-hidden" style="width: 120px;">
            <button type="button" class="qty-btn minus btn btn-outline-secondary px-3">
              <i class="ni ni-minus"></i>
            </button>
            <input type="number"
                   class="quantity-input form-control text-center border-0 px-0"
                   id="quantity-${data.hiden_id}"
                   value="1"
                   min="1"
                   aria-label="Quantity">
            <button type="button" class="qty-btn plus btn btn-outline-secondary px-3">
              <i class="ni ni-bold-add"></i>
            </button>
          </div>
    
          <!-- Wishlist Button -->
          <button class="btn btn-outline-secondary px-3 shadow-sm" title="Add to Wishlist">
            <i class="ni ni-favourite-28"></i>
          </button>
        </div>
      </div>

    `;
       
    
    }
  
    generateDescriptionHTML(data) {
      return `
        <div class="mt-4 pt-3 border-top">
          <h6 class="text-uppercase mb-3">Description</h6>
          <div class="product-description">${data.description}</div>
        </div>
      `;
    }
  
    calculateDiscount(data) {
      if (!data.original_price) return 0;
      const discount = (1 - (data.price / data.original_price)) * 100;
      return Math.round(discount);
    }
  
    validateQuantity(input) {
      const value = parseInt(input.value);
      const max = parseInt(input.max) || 10;
      const min = parseInt(input.min) || 1;
      
      if (isNaN(value)) {
        input.value = min;
      } else if (value < min) {
        input.value = min;
      } else if (value > max) {
        input.value = max;
      }
    }
  
    initCarousel() {
      // Initialize Bootstrap carousel with proper options
      const carousel = new bootstrap.Carousel(this.modalElement.querySelector('.carousel'), {
        interval: false, // Disable auto-cycling
        wrap: false // Don't wrap around
      });
      
      // Add event listeners for thumbnail navigation
      this.modalElement.querySelectorAll('.thumbnail-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const slideTo = parseInt(btn.getAttribute('data-bs-slide-to'));
          carousel.to(slideTo);
        });
      });
    }
  
    showLoading(show) {
      const loader = this.modalElement.querySelector('.quick-view-loader');
      const content = this.modalElement.querySelector('.quick-view-content');
      
      if (loader && content) {
        loader.style.display = show ? 'flex' : 'none';
        content.style.display = show ? 'none' : 'block';
      }
    }
  
    showError(message) {
      // You can replace this with your preferred notification system
      const errorElement = document.createElement('div');
      errorElement.className = 'alert alert-danger mt-3';
      errorElement.textContent = message;
      
      this.modalElement.querySelector('.modal-body').prepend(errorElement);
      setTimeout(() => errorElement.remove(), 5000);
    }
  }
  
  // Initialize the QuickView module
  document.addEventListener('DOMContentLoaded', () => {
    window.quickView = new QuickView();
    
    // // Example usage for product links:
    // document.querySelectorAll('[data-quick-view]').forEach(button => {
    //   button.addEventListener('click', (e) => {
    //     e.preventDefault();
    //     const productId = button.getAttribute('data-quick-view');
    //     window.quickView.open(productId);
    //   });
    // });
  });

