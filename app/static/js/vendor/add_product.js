
// document.addEventListener('DOMContentLoaded', function() {
//     // Category Handling
//     const categorySelect = document.getElementById('category');
//     const newCategoryWrapper = document.getElementById('newCategoryWrapper');
//     const newCategoryInput = document.getElementById('newCategoryInput');
//     const form = document.getElementById('productForm');
    
//     // Toggle new category input
//     categorySelect.addEventListener('change', function() {
//         if (this.value === '__new__') {
//             newCategoryWrapper.style.display = 'block';
//             newCategoryInput.focus();
//         } else {
//             newCategoryWrapper.style.display = 'none';
//         }
//     });
    
//     // Enhanced Form Submission
//     form.addEventListener('submit', function(e) {
//         // Handle category selection
//         if (categorySelect.value === '__new__') {
//             const newCategory = newCategoryInput.value.trim();
//             if (!newCategory || newCategory.length < 2) {
//                 e.preventDefault();
//                 showNotification('Please enter a valid category name (at least 2 characters)' ,'error');
//                 newCategoryInput.focus();
//                 return;
//             }
//             // Replace the select value with the new category
//             categorySelect.options[categorySelect.selectedIndex].value = newCategory;
//         }
        
//         // Validate at least one image source is provided
//         const imageUrl = document.getElementById('image_url').value;
//         const imageUpload = document.getElementById('image_upload').files[0];
        
//         if (!imageUrl && !imageUpload) {
//             e.preventDefault();
//             showNotification('Please provide either an image URL or upload an image' ,'warning');
//             return;
//         }
        
//         // If image is being uploaded, handle via fetch API
//         if (imageUpload && !imageUrl) {
//             e.preventDefault();
//             uploadImageAndSubmit();
//         }
//     });
    
//     // Image Upload Handling
//     const imageUpload = document.getElementById('image_upload');
//     const imagePreview = document.getElementById('image_preview');
    
//     imageUpload.addEventListener('change', function(e) {
//         if (e.target.files.length > 0) {
//             const file = e.target.files[0];
//             if (file.size > 5 * 1024 * 1024) { // 5MB limit
//                 showNotification('Image size must be less than 5MB','error');
//                 this.value = '';
//                 return;
//             }
            
//             const reader = new FileReader();
//             reader.onload = function(event) {
//                 imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
//             };
//             reader.readAsDataURL(file);
//         }
//     });
    
//     // Modern image upload function
//     function uploadImageAndSubmit() {
//         const formData = new FormData();
//         formData.append('image', imageUpload.files[0]);
        
//         fetch('/vendor/upload', {
//             method: 'POST',
//             body: formData,
//             headers :getHeaders(false)
//         })
//         .then(response => {
//             if (!response.ok) throw new Error('Upload failed');
//             return response.json();
//         })
//         .then(data => {
//             if (data.success) {
//                 document.getElementById('image_url').value = data.image_url;
//                 form.submit();
//             } else {
//                 throw new Error(data.message || 'Upload failed');
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             showNotification(`Image upload failed: ${error.message}`,'error');
//         });
//     }
// });


document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.getElementById('productForm');
    const categorySelect = document.getElementById('category');
    const newCategoryWrapper = document.getElementById('newCategoryWrapper');
    const newCategoryInput = document.getElementById('newCategoryInput');
    const imageUpload = document.getElementById('image_upload');
    const imagePreview = document.getElementById('image_preview');

    // Toggle new category input
    categorySelect.addEventListener('change', function() {
        newCategoryWrapper.style.display = this.value === '__new__' ? 'block' : 'none';
        if (this.value === '__new__') newCategoryInput.focus();
    });

    // Image preview handler
    imageUpload.addEventListener('change', handleImagePreview);

    // Form submission handler
    form.addEventListener('submit', handleFormSubmit);

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        try {
            // Validate category
            if (categorySelect.value === '__new__') {
                const newCategory = newCategoryInput.value.trim();
                if (newCategory.length < 2) {
                    showNotification('Category name must be at least 2 characters' ,'error');
                }
                categorySelect.options[categorySelect.selectedIndex].value = newCategory;
            }

            // Validate image
            const imageUrl = document.getElementById('image_url').value;
            if (!imageUrl && !imageUpload.files[0]) {
                showNotification('Please provide either an image URL or upload an image' ,'error');
            }

            // Handle image upload if needed
            if (imageUpload.files[0] && !imageUrl) {
                const imageUrl = await uploadImage(imageUpload.files[0]);
                document.getElementById('image_url').value = imageUrl;
            }

            // Submit the form
            await submitForm();
            
        } catch (error) {
            showNotification(error.message, 'error');
            console.error('Form error:', error);
        }
    }

    function handleImagePreview(e) {
        if (!e.target.files.length) return;
        
        const file = e.target.files[0];
        if (file.size > 5 * 1024 * 1024) {
            showNotification('Image size must be less than 5MB', 'error');
            e.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = function(event) {
            imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }

    async function uploadImage(file) {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch('/vendor/upload', {
            method: 'POST',
            body: formData,
            headers: getHeaders(false)
        });

        if (!response.ok) {
            const error = await response.json();
            showNotification(error.message || 'Image upload failed' ,'error');
        }

        const data = await response.json();
        return data.image_url;
    }

    async function submitForm() {
        const formData = new FormData(form);
        
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: getHeaders(false)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Form submission failed');
        }

        const result = await response.json();
        showNotification('Product added successfully!', 'success');
        return result;
    }

});

function fillDummyData() {
    // Get current date for product name
    const dateStr = new Date().toLocaleDateString();
    
    // Fill form fields
    document.getElementById('name').value = `Test Product ${dateStr}`;
    document.getElementById('description').value = `This is a test product description created on ${dateStr}. It has all required features and specifications.`;
    document.getElementById('price').value = (Math.random() * 100 + 5).toFixed(2);
    document.getElementById('stock').value = Math.floor(Math.random() * 100) + 10;
    
    // Select a random category or create new
    const categories = document.getElementById('category').options;
    const randomCategory = Math.random() > 0.7 ? '__new__' : Math.floor(Math.random() * (categories.length - 2)) + 1;
    
    document.getElementById('category').value = randomCategory;
    if (randomCategory === '__new__') {
        document.getElementById('newCategoryWrapper').style.display = 'block';
        document.getElementById('newCategoryInput').value = `New Category ${Math.floor(Math.random() * 1000)}`;
    }
    
    // Leave image_url and image_upload empty
    document.getElementById('preview_url').value = '';
}

// Call the function to auto-fill when needed
// fillDummyData();