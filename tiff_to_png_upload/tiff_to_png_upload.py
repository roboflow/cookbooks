from PIL import Image
import os
from roboflow import Roboflow

# Set your Roboflow Workspace API Key and Project Name here
WORKSPACE_API_KEY = "Your_API_Key_Here"
PROJECT_NAME = "Your_Project_Name"

def convert_tiff_to_png(tiff_file_path, png_file_path=None):
    """
    Convert a TIFF image to a PNG image.

    :param tiff_file_path: Path to the TIFF file.
    :param png_file_path: Path where the PNG file will be saved. If None, the PNG will be saved in the same location with the same name.
    """
    # Ensure the source file exists
    if not os.path.exists(tiff_file_path):
        raise FileNotFoundError(f"The file {tiff_file_path} does not exist.")
    
    # Open the TIFF image
    with Image.open(tiff_file_path) as img:
        # Define the PNG file path if not specified
        if png_file_path is None:
            png_file_path = os.path.splitext(tiff_file_path)[0] + '.png'
        
        # Convert and save the image in PNG format
        img.save(png_file_path, 'PNG')
        print(f"Converted '{tiff_file_path}' to '{png_file_path}'.")
        return png_file_path

def upload_directory_to_roboflow(directory_path):
    """
    Converts all TIFF images in a directory to PNG and uploads them to Roboflow.

    :param directory_path: Path to the directory containing TIFF files.
    """
    for tiff_file in os.listdir(directory_path):
        if tiff_file.lower().endswith('.tiff'):
            tiff_file_path = os.path.join(directory_path, tiff_file)
            png_file_path = convert_tiff_to_png(tiff_file_path)
            upload_image_to_roboflow(png_file_path)

def main(directory_path):
    """
    Convert TIFF files to PNG in the given directory and upload them to Roboflow.

    :param directory_path: Path to the directory containing TIFF files.
    """
    upload_directory_to_roboflow(directory_path)

# Example usage
# main('path/to/your/directory')