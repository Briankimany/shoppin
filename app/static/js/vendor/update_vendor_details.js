function submitVendorForm() {
    const formData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        store_name: document.getElementById("store_name").value,
        store_logo: document.getElementById("store_logo").value,
        payment_type: document.getElementById("payment_type").value,
        store_description: document.getElementById("store_description").value,
    };

    fetch("/vendor/update-details", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: formData })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.error) {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error("Error:", error));
}

function updatePreview() {
    const urlInput = document.getElementById("store_logo");
    const fileInput = document.getElementById("store_logo_file");
    const preview = document.getElementById("preview");

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
        urlInput.value = ""; // Clear URL input
    } else if (urlInput.value.trim() !== "") {
        preview.src = urlInput.value;
        preview.style.display = "block";
        fileInput.value = ""; // Clear file input
    } else {
        preview.style.display = "none";
    }
}

function uploadImageThenSubmit() {
    const fileInput = document.getElementById("store_logo_file");
    const urlInput = document.getElementById("store_logo");

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("store_logo_file", file);

        fetch("/vendor/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                urlInput.value = data.image_url; // Set uploaded image URL
                submitVendorForm(); // Now call the existing function
            } else {
                alert("Image upload failed.");
            }
        })
        .catch(error => console.error("Upload error:", error));
    } else {
        submitVendorForm(); // Directly call it if only a URL is provided
    }
}

document.getElementById("store_logo").addEventListener("input", updatePreview);
document.getElementById("store_logo_file").addEventListener("change", updatePreview);
