import os
import time
import json
from typing import Callable, List

class ImageMonitor:
    """Monitor a directory for new images and trigger a pipeline.

    Attributes:
        directory (str): The directory to monitor for images.
        wait_time (int): The wait time before triggering the pipeline.
        processed_images_file (str): File to store processed images.
        pipeline (Callable): The pipeline function to be triggered.
        processed_images (List[str]): List of processed images.
    """

    def __init__(self, directory: str, config: dict, wait_time: int, pipeline: Callable):
        """Initialize the ImageMonitor class.

        Args:
            directory (str): Directory to monitor.
            config (dict): Configuration dictionary.
            wait_time (int): Wait time in seconds before triggering pipeline.
            pipeline (Callable): Pipeline function to execute on new images.
        """
        self.directory = directory
        self.wait_time = wait_time
        self.pipeline = pipeline
        self.config = config
        self.processed_images_file = os.path.join(directory, 'processed_images.json')
        self.processed_images = self.load_processed_images()

    def load_processed_images(self) -> List[str]:
        """Load the list of processed images from file.

        Returns:
            List[str]: A list of processed image filenames.
        """
        if os.path.exists(self.processed_images_file):
            with open(self.processed_images_file, 'r') as file:
                return json.load(file)
        return []

    def save_processed_images(self):
        """Save the list of processed images to file."""
        with open(self.processed_images_file, 'w') as file:
            json.dump(self.processed_images, file)

    def monitor_directory(self):
        """Monitor the directory for new images and trigger the pipeline."""
        while True:
            new_images = [img for img in os.listdir(self.directory) 
                          if img.endswith(('.png', '.jpg', '.jpeg')) and img not in self.processed_images]

            if new_images:
                time.sleep(self.wait_time)
                # Loop through images:
                self.process_images(new_images)

            time.sleep(2)  # Check every 2 seconds

    def process_images(self, images: List[str]):
        """Process new images and update the processed images list.

        Args:
            images (List[str]): List of new image filenames to process.
        """
        for image in images:
            try:
                # self.pipeline(os.path.join(self.directory, image))
                self.pipeline(os.path.join(self.directory, image), self.config)
                self.processed_images.append(image)
                self.save_processed_images()
            except Exception as e:
                print(f"Error processing {image}: {e}")

# Example usage
def example_pipeline(image_path: str, config = {}):
    """Example pipeline function to process an image."""
    print(f"Processing {image_path}")

# Main
if __name__ == "__main__":
    # Initialize and start monitoring
    path_monitor = '/Users/reed/Documents/GitHub/field_engineering_internal/client_projects/DANA/x-ray-project/data/JAN 4 2024 Test Set/Monitor'
    wait_time = 1
    config = {}
    monitor = ImageMonitor(path_monitor, config, wait_time, example_pipeline)
    monitor.monitor_directory()
