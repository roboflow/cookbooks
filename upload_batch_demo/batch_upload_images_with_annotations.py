import glob
import os
import requests
import io
import xml.etree.ElementTree as ET
from PIL import Image
from roboflow import Roboflow
from requests_toolbelt.multipart.encoder import MultipartEncoder

## DEFINITIONS
# glob params
image_dir = os.path.join("images")
file_extension_type = ".jpg"

roboflow_api = "API"
roboflow_projectID = "testing-uploads"

# roboflow pip params
# rf = Roboflow(api_key=roboflow_api)
# upload_project = rf.workspace().project(roboflow_projectID)

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

    # UPLOADING IMAGE #
    m = MultipartEncoder(fields={'file': (image, buffered.getvalue(), "image/jpeg")})
    r = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type})

    json_blob = r.json()
    # print(json_blob)

    image_id = json_blob['id']
    print("SUCCESS IMAGE UPLOAD: " + image_id)

    annotation_filename = "pineapples.xml"
    batch_name = "Tyler Test"

    mytree = ET.parse(annotation_filename)
    myroot = mytree.getroot()

    for filename in myroot.iter('filename'):
        filename.text = str(image)
        # print(filename.text)

    for path in myroot.iter('path'):
        # updates the price value
        path.text = str(image)
        # print(path.text)

    mytree.write("pineapples.xml")

    # Read Annotation as String
    annotation_str = open(annotation_filename, "r").read()

    # Construct the URL
    upload_url = "".join([
        "https://api.roboflow.com/dataset/"+roboflow_projectID+"/annotate/"+image_id,
        "?api_key="+str(roboflow_api),
        "&name=", str(annotation_filename), "&jobName=",str(batch_name), "&overwrite=true"
    ])

    # POST to the API
    r = requests.post(upload_url, data=annotation_str, headers={
        "Content-Type": "text/plain"
    })

    # Output result
    print("SUCCESS ANNOTATION UPLOAD - JSON Code: " + str(r.json()))