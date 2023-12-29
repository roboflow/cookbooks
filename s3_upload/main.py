import argparse
import logging
from utils import read_config, get_current_date, get_current_timestamp, setup_logging
from imgsampler import ImageSampler
from s3_client import S3Client
from uploader import ImageUploader

def main():
    # Command line arguments
    parser = argparse.ArgumentParser(description="Sample images from an S3 bucket.")
    parser.add_argument("M", type=int, help="Total number of images to pull")
    parser.add_argument("N", type=int, help="Batch size of images to pull at once")
    parser.add_argument("--fetch-from-s3", action="store_true", help="Flag to fetch image names from S3")
    args = parser.parse_args()

    # Setup logging
    timestamp = get_current_timestamp()
    date = get_current_date()
    log_filename = f"logs/S3_log_{timestamp}.log"
    setup_logging(log_filename)

    # Read in config file
    config_path = 'config.yaml'
    config = read_config(config_path)

    # Initialization using configurations
    roboflow_api_key = config['roboflow']['api_key']
    project_name = config['roboflow']['project_name']
    batch_name = config.get('roboflow', {}).get('batch_name', date)
    s3_bucket_name = config['s3']['bucket_name']
    label_null = config['roboflow']['label_null']

    # Instantiate required objects
    s3_client_instance = S3Client()
    uploader_instance = ImageUploader(roboflow_api_key, project_name, batch_name, s3_client_instance, s3_bucket_name, label_null=label_null)

    # Create the ImageSampler object
    sampler = ImageSampler(s3_client_instance, s3_bucket_name, uploader_instance)

    # try:
    sampler.sample_images(args.N, args.M, args.fetch_from_s3)

    # except Exception as e:
    #     logging.error(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    main()
