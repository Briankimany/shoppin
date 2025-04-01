import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "dqmqwijyf", 
    api_key = "492612549584774", 
    api_secret = "G3_aDbgebqFFGeW_4hbgSH_xC80", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# # Upload an image
# my_image_url = "https://kimany.pythonanywhere.com/static/uploads/physics%20joke.jpg"
# upload_result = cloudinary.uploader.upload(my_image_url,
#                                            public_id="shoes")
# print(upload_result["secure_url"])

# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)
def upload_and_transform_image(image_url, public_id):
    # Upload the image
    upload_result = cloudinary.uploader.upload(image_url, public_id=public_id)
    print(f"Uploaded Image URL: {upload_result['secure_url']}")

    # Define different sizes for eCommerce
    sizes = [
        {"width": 1000, "height": 1000},  # Main product image
        {"width": 500, "height": 500},    # Thumbnail
        {"width": 300, "height": 300},    # Smaller thumbnail
        {"width": 800, "height": 800},    # Medium size
        {"width": 1920, "height": 1080}   # Hero image
    ]

    # Generate URLs for each size
    for size in sizes:
        optimized_url, _ = cloudinary_url(
            public_id,
            width=size["width"],
            height=size["height"],
            crop="fill",  # Use "fill" to ensure the image fills the specified dimensions
            fetch_format="auto",
            quality="auto"
        )
        print(f"Optimized URL for {size['width']}x{size['height']}: {optimized_url}")

# Example usage
my_image_url = "https://kimany.pythonanywhere.com/static/uploads/physics%20joke.jpg"
upload_and_transform_image(my_image_url, public_id="shoes")