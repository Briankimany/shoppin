
function showAlert(type, message) {
    const alertBox = document.getElementById("alert-box");
    alertBox.style.display = "block";
    alertBox.style.padding = "10px";
    alertBox.style.borderRadius = "5px";
    alertBox.style.marginTop = "10px";
    alertBox.style.color = "#fff";

    if (type === "success") {
        alertBox.style.backgroundColor = "#4CAF50";
    } else if (type === "error") {
        alertBox.style.backgroundColor = "#f44336";
    }

    alertBox.textContent = message;

    // Auto-hide after 4 seconds
    setTimeout(() => {
        alertBox.style.display = "none";
    }, 4000);
}

function toggleButtonLoading(isLoading) {
    const button = document.getElementById("submit-btn");
    const text = button.querySelector(".btn-text");
    const spinner = button.querySelector(".spinner");

    if (isLoading) {
        button.disabled = true;
        text.style.display = "none";
        spinner.style.display = "inline-block";
    } else {
        button.disabled = false;
        text.style.display = "inline";
        spinner.style.display = "none";
    }
}


async function submitVendorForm() {
    toggleButtonLoading(true);
    const fields = [
        "name", "email", "phone", "store_name",
        "store_logo", "payment_type", "store_description"
    ];

    const formData = {};
    for (const field of fields) {
        formData[field] = document.getElementById(field).value;
    }

    try {
        const response = await fetch("/vendor/update-details", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ data: formData })
        });

        const data = await response.json();
        console.log("data is "+data);

        if (data.error) {
            showAlert("error","unable to process request");
            return;
        }
        
        showAlert('Updated details');
        toggleButtonLoading(false);
        for (const field of fields) {
            if (data[field] !== undefined) {
                document.getElementById(field).value = data[field];
            }
        }

    } catch (error) {
        console.error("Error:", error);
        toggleButtonLoading(false);
    }
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

document.addEventListener("DOMContentLoaded", function () {
    const storeLogoInput = document.getElementById("store_logo");
    const storeLogoFileInput = document.getElementById("store_logo_file");

    if (storeLogoInput) {
        storeLogoInput.addEventListener("input", updatePreview);
    }

    if (storeLogoFileInput) {
        storeLogoFileInput.addEventListener("change", updatePreview);
    }
});
