
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
// Delete Product Function
function deleteProduct(productId) {
    const modal = document.getElementById('deleteModal');
    const toast = document.getElementById('notificationToast');
    
    // Show modal
    modal.style.display = 'flex';
  
    // Set up confirm button
    modal.querySelector('.btn-confirm').onclick = async () => {
      try {
        
      
        const csrfToken = getCsrfToken();
        console.log("the csrf token is "+csrfToken);
        const response = await fetch(`/vendor/delete_product/${productId}`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        });
  
        if (response.ok) {
          showNotification('Product deleted successfully!', 'success');
          // Remove the table row
          document.querySelector(`tr[data-product-id="${productId}"]`)?.remove();
        } else {
          throw new Error('Deletion failed');
        }
      } catch (error) {
        showNotification('Error: ' + error.message, 'error');
      } finally {
        modal.style.display = 'none';
      }
    };
  
    // Set up cancel button
    modal.querySelector('.btn-cancel').onclick = () => {
      modal.style.display = 'none';
    };
  }
  
 



