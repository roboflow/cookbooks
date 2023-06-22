# A script to upload images in a private GCS bucket to Roboflow.
# The script uses a GCP service account private key to create
# signed URLs; these are time-limited URLs that Roboflow can use
# to ingest image data into the Roboflow workspaces.
#
# Requirements
# This script assumes gsutil is configured to the corresponding project;
# documentation here:
# https://cloud.google.com/storage/docs/gsutil_install
# Openssl is required to sign the URLs, install with this command:
# pip3 install pyopenssl
# Install the requests package
# pip3 install requests
# Use this link to learn and obtain a GCP service account key
# https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys )

# Roboflow API key
# Export your ROBOFLOW_API_KEY in the terminal you are running this script; for example
# export ROBOFLOW_API_KEY=<private API key>
# To obtain your API key, follow the instructions here:  https://docs.roboflow.com/rest-api#obtaining-your-api-key

# Using the script
# This script needs 3 command line arguments to run
# $1 --> The path to the service account private key
# $2 --> The name of the gcs bucket e.g. gs://foo-bar-bucket/ containing the images
# $3 --> The Roboflow dataset ID to upload the image into

# Example invocation
# python3 gcs-signed-urls-for-upload.py ./gcp-sa-key-file.json gs://test-signing-urls/ hard-hat-sample-qulad

import os
import subprocess
import sys
import urllib.parse

import requests

SIGNED_URL_VALIDITY = "10m"
if "ROBOFLOW_API_KEY" not in os.environ:
    print("Please export the ROBOFLOW_API_KEY into your environment.")
key_path = sys.argv[1]
bucket_name = sys.argv[2]
upload_endpoint = "https://api.roboflow.com/dataset/" + sys.argv[3] + "/upload"
# A list of objects in the bucket; note: if there are too many objects in the bucket (5000+ for example), consider getting this
# list in a different way e.g. using the boto3 library and pagination, etc.
bucket_objects = subprocess.check_output(
    ["gsutil", "ls", sys.argv[2]], universal_newlines=True
).split("\n")

for each_object in bucket_objects:
    # Filter out any non-image objects in the bucket
    if each_object.endswith((".jpeg", ".jpg", ".png", ".PNG", ".JPEG", ".JPG")):
        # Obtain signed URL for the object
        raw_data = subprocess.check_output(
            ["gsutil", "signurl", "-d", SIGNED_URL_VALIDITY, key_path, each_object],
            universal_newlines=True,
        )
        # Construct the URL correctly
        signed_img_url = "https://" + raw_data.split("https://")[-1]
        img_name = each_object.split("/")[-1]
        # Create the upload URL to post to the Roboflow Upload endpoint
        upload_url = "".join(
            [
                upload_endpoint,
                "?api_key="
                + os.environ.get(
                    "ROBOFLOW_API_KEY",
                ),
                "&name=" + img_name,
                "&split=train",
                "&image=" + urllib.parse.quote_plus(signed_img_url),
            ]
        )
        # POST to the Roboflow Upload API
        r = requests.post(upload_url)
        # Post result
        print(r.text)
