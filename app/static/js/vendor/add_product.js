
document.addEventListener('DOMContentLoaded', function() {
    // Category Handling
    const categorySelect = document.getElementById('category');
    const newCategoryWrapper = document.getElementById('newCategoryWrapper');
    const newCategoryInput = document.getElementById('newCategoryInput');
    const form = document.getElementById('productForm');
    
    // Toggle new category input
    categorySelect.addEventListener('change', function() {
        if (this.value === '__new__') {
            newCategoryWrapper.style.display = 'block';
            newCategoryInput.focus();
        } else {
            newCategoryWrapper.style.display = 'none';
        }
    });
    
    // Enhanced Form Submission
    form.addEventListener('submit', function(e) {
        // Handle category selection
        if (categorySelect.value === '__new__') {
            const newCategory = newCategoryInput.value.trim();
            if (!newCategory || newCategory.length < 2) {
                e.preventDefault();
                alert('Please enter a valid category name (at least 2 characters)');
                newCategoryInput.focus();
                return;
            }
            // Replace the select value with the new category
            categorySelect.options[categorySelect.selectedIndex].value = newCategory;
        }
        
        // Validate at least one image source is provided
        const imageUrl = document.getElementById('image_url').value;
        const imageUpload = document.getElementById('image_upload').files[0];
        
        if (!imageUrl && !imageUpload) {
            e.preventDefault();
            alert('Please provide either an image URL or upload an image');
            return;
        }
        
        // If image is being uploaded, handle via fetch API
        if (imageUpload && !imageUrl) {
            e.preventDefault();
            uploadImageAndSubmit();
        }
    });
    
    // Image Upload Handling
    const imageUpload = document.getElementById('image_upload');
    const imagePreview = document.getElementById('image_preview');
    
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                alert('Image size must be less than 5MB');
                this.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(event) {
                imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Modern image upload function
    function uploadImageAndSubmit() {
        const formData = new FormData();
        formData.append('image', imageUpload.files[0]);
        
        fetch('/vendor/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Upload failed');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                document.getElementById('image_url').value = data.image_url;
                form.submit();
            } else {
                throw new Error(data.message || 'Upload failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Image upload failed: ${error.message}`);
        });
    }
});
