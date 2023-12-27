import boto3
import logging

class S3Client:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def upload_file(self, file_path, bucket_name, object_name=None):
        """Upload a file to an S3 bucket.

        :param file_path: File to upload
        :param bucket_name: Bucket to upload to
        :param object_name: S3 object name. If not specified then the file_name is used.
        :return: True if file was uploaded, else False
        """
        if not object_name:
            object_name = file_path

        try:
            self.s3.upload_file(file_path, bucket_name, object_name)
            logging.info(f"File {file_path} uploaded successfully to {bucket_name}/{object_name}.")
            return True
        except Exception as e:
            logging.error(f"Error uploading {file_path} to {bucket_name}/{object_name}. Error: {str(e)}")
            return False

    def list_objects(self, bucket_name, prefix=''):
        """List all objects in an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param prefix: Optional prefix filter.
        :return: List of object keys.
        """
        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            results = paginator.paginate(Bucket=bucket_name)
            
            all_files = []
            for page in results:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        all_files.append(obj["Key"])

            return all_files

        except Exception as e:
            logging.error(f"Error listing objects in {bucket_name}. Error: {str(e)}")
            return []

    def download_file(self, bucket_name, object_name):
        """Download a file from an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param object_name: S3 object name.
        """
        try:
            image_obj = self.s3.get_object(Bucket=bucket_name, Key=object_name)
            # logging.info(f"File {object_name} downloaded successfully from {bucket_name}.")

            return image_obj
        except Exception as e:
            logging.error(f"Error downloading {object_name} from {bucket_name}. Error: {str(e)}")

            return False

    # You can add more methods here as needed, like delete_object, copy_object, etc.

# Usage examples (comment out or remove in production):
# client = S3Client('<YOUR_ACCESS_KEY>', '<YOUR_SECRET_KEY>')
# client.upload_file('path/to/local/file', 'bucket-name')
# files = client.list_objects('bucket-name', 'prefix/')
