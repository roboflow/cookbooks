
import os
import argparse
import urllib.request
from openai import OpenAI
from API_KEY import openai_api_key

# OpenAI API
client = OpenAI(api_key=openai_api_key)

def generate_images(image_path, mask_path, prompt, count, size):
    # Use DALL-E to generate images
    response = client.images.edit(
        image=open(image_path, "rb"),
        mask=open(mask_path, "rb"),
        prompt=prompt,
        n=count,
        size=size
    )

    # Get image URLs from the response
    image_urls = [image.url for image in response.data]
    
    return image_urls

def download_and_save_images(image_urls, output_folder):
    # Download and save the images
    for i, url in enumerate(image_urls, start=1):
        try:
            # Create the image name
            image_name = f"generated_image_{i}.png"
            
            # Create the full path for saving the image
            save_path = os.path.join(output_folder, image_name)

            # Download the image
            urllib.request.urlretrieve(url, save_path)

            print(f"Image saved: {save_path}")
        except Exception as e:
            print(f"Error saving image from {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate and download images using OpenAI's DALL-E.")
    parser.add_argument("--image_path", required=True, help="Path to the input image")
    parser.add_argument("--mask_path", required=True, help="Path to the mask image")
    parser.add_argument("--prompt", required=True, help="Prompt for DALL-E")
    parser.add_argument("--count", type=int, default=2, help="Number of images to generate (default: 2)")
    parser.add_argument("--size", default="1024x1024", help="Size of the generated images (default: 1024x1024)")
    parser.add_argument("--output_folder", default="dataset", help="Output folder for saving the generated images (default: dataset)")

    args = parser.parse_args()

    # Generate images
    image_urls = generate_images(args.image_path, args.mask_path, args.prompt, args.count, args.size)

    # Specify the directory where you want to save the images
    output_folder = os.path.join(os.getcwd(), args.output_folder)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Download and save the images
    download_and_save_images(image_urls, output_folder)

if __name__ == "__main__":
    main()

