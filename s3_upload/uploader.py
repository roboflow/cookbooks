import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from roboflow import Roboflow
from roboflow.config import API_URL
from PIL import Image
import io
import threading
import logging
import xml.etree.ElementTree as ET

class ImageUploader:
    def __init__(self, roboflow_api_key, project_name, batch_name, s3_client, bucket_name, label_null=False):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.label_null = label_null
        
        # Construct URL for local image upload
        self.image_upload_url = "".join(
                [
                    API_URL + "/dataset/",
                    project_name,
                    "/upload",
                    "?api_key=",
                    roboflow_api_key,
                    "&batch=",
                    batch_name,
                ]
            )

        # Initialize the Roboflow object with your API key
        self.roboflow_api_key = roboflow_api_key
        self.project_name = project_name
        self.rf = Roboflow(api_key=roboflow_api_key)
        self.project = self.rf.workspace().project(project_name)
        self.batch_name = batch_name

        # Threading
        self.upload_lock = threading.Lock()

    def upload_to_api_and_record(self, image_name):
        """Uploads the image to another site via API and records the image name if successful."""
        try:
            # Get image from S3
            image_obj = self.s3_client.download_file(self.bucket_name, image_name)
            image_data = image_obj['Body'].read()

            # Convert the bytes to a PIL Image
            image_pil = Image.open(io.BytesIO(image_data))

            # Convert to JPEG Buffer
            buffered = io.BytesIO()
            image_pil.save(buffered, quality=100, format="JPEG")

            # Build multipart form and post request
            m = MultipartEncoder(
                fields={
                    "name": image_name,
                    "file": ("imageToUpload", buffered.getvalue(), "image/jpeg"),
                }
            )
            response = requests.post(
                self.image_upload_url, data=m, headers={"Content-Type": m.content_type}
            )

            # Check response
            if 'success' in response.json():
                status_code = response.status_code
            elif 'duplicate' in response.json():
                logging.info(f"Roboflow reported a duplicate for: {image_name}")
                status_code = 300
            else:
                status_code = response.status_code

            # Check if we want to upload image as 'NULL'
            if self.label_null and status_code == 200:
                # Get image ID from response
                image_id = response.json()['id']

                # Upload Null annotation
                annotation_response = self.upload_null_annotation(image_name, image_id)

        except Exception as e:
            logging.error(f"Error occurred while uploading image {image_name}: {str(e)}")
            status_code = 400

        return status_code == 200
    
    def upload_null_annotation(self, image_name, image_id):  
        """Uploads a NULL annotation to the image."""
        # Create empty annotation file
        annotation_filename = image_name.split('.')[0] + '.xml'
        annotation_str = """{
                            "boxes": [],
                            "key": "%s",
                        }""" % image_name

        # Construct annotate URL
        annotate_url = "".join([
            "https://api.roboflow.com/dataset/"+self.project_name+"/annotate/"+image_id,
            "?api_key="+str(self.roboflow_api_key),
            "&name=", str(annotation_filename), "&jobName=",str(self.batch_name), "&overwrite=true"
        ])

        # POST to the annotate API
        response = requests.post(annotate_url, data=annotation_str, headers={
            "Content-Type": "text/plain"
        })

        return response


    def upload_worker(self, image_name, update_callback):
        """Thread worker for uploading images."""
        upload_successful = self.upload_to_api_and_record(image_name)
        if upload_successful:
            with self.upload_lock:
                update_callback(image_name)

# Any additional functions or logic related to Uploader can be added here.
