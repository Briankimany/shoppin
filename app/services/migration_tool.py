import requests
from typing import List, Dict, Any
from app.services.upload import ImageManager

class ImageMigrationService:
    def __init__(self, base_url: str = "http://localhost:5500/admin"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}

    def fetch_images(self) -> List[Dict[str, Any]]:
        """Fetch images from the API endpoint"""
        response = requests.get(f"{self.base_url}/get-images")
        response.raise_for_status()
        return response.json().get('data', [])

    def migrate_single_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and migrate a single image"""
        return ImageManager.migrate_images([image_data])[0]

    def update_remote_url(self, migrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update the remote URL via API"""
        response = requests.post(
            f"{self.base_url}/update-images-url",
            json={"data": migrated_data},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def run_migration(self) -> List[Dict[str, Any]]:
        """Run complete migration process"""
        results = []
        images = self.fetch_images()
        
        for image in images:
            try:
                migrated = self.migrate_single_image(image)
                update_result = self.update_remote_url(migrated)
                results.append({
                    "original": image,
                    "migrated": migrated,
                    "api_response": update_result
                })
            except Exception as e:
                results.append({
                    "error": str(e),
                    "failed_image": image
                })
        
        return results


# CLI Usage
if __name__ == "__main__":
    migrator = ImageMigrationService()
    results = migrator.run_migration()
    
    for result in results:
        if 'error' in result:
            print(f"Failed: {result['error']}")
        else:
            print(f"Success: {result['migrated']}")
            print(f"API Response: {result['api_response']}")