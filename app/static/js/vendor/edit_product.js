document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('productForm');
    const submitBtn = document.getElementById('submitBtn');
    const imageUpload = document.getElementById('image_upload');
    const imagePreview = document.getElementById('image_preview');

    // Image preview handler
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const previewUrl = URL.createObjectURL(file);
            
            imagePreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = previewUrl;
            img.style.maxWidth = '200px';
            imagePreview.appendChild(img);
        }
    });

    // Form submission handler
    submitBtn.addEventListener('click', handleFormSubmit);

    async function handleFormSubmit() {
        try {
            if (imageUpload.files.length > 0) {
                const imageUrl = await uploadImage(imageUpload.files[0]);
                document.getElementById('image_url').value = imageUrl;
            }
            await submitForm();
        } catch (error) {
            console.error('Error:', error);
            showNotification(error.message, 'error');
        }
    }

    async function uploadImage(file) {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch('/vendor/upload', {
            method: 'POST',
            body: formData,
            headers: getHeaders(false)
        });

        const data = await response.json();
        
        if (!response.ok || !data.success) {
           showNotification(data.message || 'Image upload failed' ,'error');
        }

        return data.image_url;
    }

    async function submitForm() {
        const formData = new FormData(form);
       
        // Add all regular form fields
        formData.append('name', document.getElementById('name').value);
        formData.append('description', document.getElementById('description').value);
        formData.append('price', document.getElementById('price').value);
        formData.append('stock', document.getElementById('stock').value);
        formData.append('category', document.getElementById('category').value);
        formData.append('image_url', document.getElementById('image_url').value);
        
        console.log(formData);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: getHeaders(false)
        });

        if (!response.ok) {
            const error = await response.json();
            showNotification(error.message || 'Form submission failed' ,'error');
        }

        const result = await response.json();
        showNotification(result.data, 'success');
        return result;
    }
});