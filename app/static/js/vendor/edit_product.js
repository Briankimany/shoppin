
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('productForm');
    const submitBtn = document.getElementById('submitBtn');
    const imageUpload = document.getElementById('image_upload');
    const imageUrl = document.getElementById('image_url');
    const imagePreview = document.getElementById('image_preview');

    // Handle image preview
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const previewUrl = URL.createObjectURL(file);
            
            // Clear previous preview
            imagePreview.innerHTML = '';
            
            // Create new preview
            const img = document.createElement('img');
            img.src = previewUrl;
            img.style.maxWidth = '200px';
            imagePreview.appendChild(img);
        }
    });

    // Handle form submission
    submitBtn.addEventListener('click', function() {
        if (imageUpload.files.length > 0) {
            // If file is selected, upload first
            uploadImage().then(function(imageUrl) {
                if (imageUrl) {
                    // Set the image URL field with the returned URL
                    document.getElementById('image_url').value = imageUrl;
                    form.submit();
                }
            }).catch(function(error) {
                console.error('Upload failed:', error);
                alert('Image upload failed. Please try again.');
            });
        } else {
            // No file selected, submit directly
            form.submit();
        }
    });

    function uploadImage() {
        return new Promise(function(resolve, reject) {
            const formData = new FormData();
            formData.append('image', imageUpload.files[0]);
            
            fetch('/vendor/upload', {
                method: 'POST',
                body: formData
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    resolve(data.image_url);
                } else {
                    reject(new Error(data.message || 'Upload failed'));
                }
            })
            .catch(function(error) {
                reject(error);
            });
        });
    }
});
