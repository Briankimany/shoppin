async function openQuickView(productId) {
    try {
        const response = await fetch(`/products/details/${productId}`);
        if (!response.ok) throw new Error(`Product fetch failed (${response.status})`);
        
        const { data } = await response.json();
        
        // 1. PRODUCT GALLERY ======================================
        const galleryContainer = document.getElementById('quickViewGallery');
        galleryContainer.innerHTML = generateImageGallery(data);
        
        // 2. PRODUCT HEADER ======================================
        document.getElementById('quickViewTitle').innerHTML = `
            ${data.name}
            <span class="badge bg-gradient-${data.in_stock ? 'success' : 'danger'} ms-2">
                ${data.in_stock ? 'In Stock' : 'Out of Stock'}
            </span>
        `;
        
        // 3. PRICING SECTION =====================================
        document.getElementById('quickViewPricing').innerHTML = `
            <h3 class="mb-0">$${(data.price / 100).toFixed(2)}</h3>
            ${data.original_price ? `
                <del class="text-muted ms-2">$${(data.original_price / 100).toFixed(2)}</del>
                <span class="badge bg-gradient-danger ms-2">Save ${calculateDiscount(data)}%</span>
            ` : ''}
        `;
        
        // 4. ATTRIBUTES FILTERS ==================================
        document.getElementById('quickViewAttributes').innerHTML = `
            <div class="d-flex flex-wrap gap-2">
                ${data.attribute_values.map(attr => `
                    <a href="/products/filters/?${attr.attribute_types[0]}=${encodeURIComponent(attr.value)}" 
                       class="btn btn-sm btn-outline-dark mb-0">
                        ${attr.attribute_types[0]}: <strong>${attr.value}</strong>
                        ${attr.unit ? ` ${attr.unit}` : ''}
                    </a>
                `).join('')}
            </div>
        `;
        
        // 5. ADD TO CART SECTION =================================
        document.getElementById('quickViewAddToCart').innerHTML = `
            <div class="row">
                <div class="col-4">
                    <div class="input-group input-group-outline">
                        <label class="form-label">Qty</label>
                        <input type="number" class="form-control" value="1" min="1">
                    </div>
                </div>
                <div class="col-8">
                    <button class="btn btn-gradient-dark w-100 mb-0" 
                            onclick="addToCart(${data.id})">
                        <i class="fas fa-shopping-cart me-2"></i> Add to Cart
                    </button>
                </div>
            </div>
        `;
        
        // 6. SHOW MODAL ==========================================
        new bootstrap.Modal(document.getElementById('quickViewModal')).show();
        
    } catch (error) {
        console.error('QuickView Error:', error);
        showNotification('error', 'Failed to load product details');
    }
}

// HELPER FUNCTIONS ============================================
function generateImageGallery(data) {
    const images = data.images?.length ? data.images : [data.image_src || '/static/assets/img/placeholder.jpg'];
    
    return `
        <!-- Main Image -->
        <div class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-inner rounded-3">
                ${images.map((img, i) => `
                    <div class="carousel-item ${i === 0 ? 'active' : ''}">
                        <img src="${img}" class="d-block w-100" alt="${data.name}">
                    </div>
                `).join('')}
            </div>
            ${images.length > 1 ? `
                <button class="carousel-control-prev" type="button" data-bs-target="#quickViewGallery" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#quickViewGallery" data-bs-slide="next">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                </button>
            ` : ''}
        </div>
        
        <!-- Thumbnails -->
        <div class="d-flex mt-3">
            ${images.map((img, i) => `
                <a href="#" class="me-2" onclick="event.preventDefault(); document.querySelectorAll('#quickViewGallery .carousel-item')[${i}].classList.add('active')">
                    <img src="${img}" width="60" class="rounded-2 ${i === 0 ? 'border border-dark' : ''}" alt="Thumbnail">
                </a>
            `).join('')}
        </div>
    `;
}

function calculateDiscount(data) {
    if (!data.original_price) return 0;
    return Math.round((1 - data.price / data.original_price) * 100);
}

function showNotification(type, message) {
    // Implement your preferred notification system
    alert(`${type.toUpperCase()}: ${message}`);
}