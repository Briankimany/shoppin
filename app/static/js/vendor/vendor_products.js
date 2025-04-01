
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('productSearch');
    const productRows = document.querySelectorAll('.product-row, .product-card');
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        productRows.forEach(row => {
            const productName = row.querySelector('h3, .product-info strong').textContent.toLowerCase();
            const productDesc = row.querySelector('.product-description, .card-description')?.textContent.toLowerCase() || '';
            
            if (productName.includes(searchTerm) || productDesc.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
    
    // Category filter
    const categoryFilter = document.getElementById('categoryFilter');
    
    categoryFilter.addEventListener('change', function() {
        const selectedCategory = this.value;
        
        productRows.forEach(row => {
            const rowCategory = row.getAttribute('data-category');
            
            if (!selectedCategory || rowCategory === selectedCategory) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
});
