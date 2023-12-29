import glob
import os
import requests
import io
from PIL import Image
from roboflow import Roboflow
from requests_toolbelt.multipart.encoder import MultipartEncoder

## DEFINITIONS
# glob params
image_dir = os.path.join("Images")
file_extension_type = ".jpg"

roboflow_api = "API"
roboflow_projectID = "PROJECT_ID"

# roboflow pip params
rf = Roboflow(api_key=roboflow_api)
upload_project = rf.workspace().project(roboflow_projectID)

# get all images from folder
image_glob = glob.glob('Images' + '/*' + file_extension_type)

print(image_glob)

# perform upload
for image in image_glob:
    
    # Load Image with PIL
    image_open = Image.open(image).convert("RGB")

    # Convert to JPEG Buffer
    buffered = io.BytesIO()
    image_open.save(buffered, quality=90, format="JPEG")

    # Construct the URL
    upload_url = "".join([
        "https://api.roboflow.com/dataset/" + roboflow_projectID + "/upload",
        "?api_key=" + roboflow_api
    ])

    m = MultipartEncoder(fields={'file': (image, buffered.getvalue(), "image/jpeg")})
    r = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type})

    json_blob = r.json()
    # print(json_blob)

    image_id = json_blob['id']
    print("Image ID: " + image_id)

    # Output result
    print(r.json())