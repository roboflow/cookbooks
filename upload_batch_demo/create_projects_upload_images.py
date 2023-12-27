from PIL import Image
from roboflow import Roboflow
from requests_toolbelt.multipart.encoder import MultipartEncoder
from fuzzywuzzy import process
import glob
import os
import requests
import io
import json

def find_best_match(input_string, potential_matches):
    best_match = process.extractOne(input_string, potential_matches)
    return best_match

roboflow_api = "API"
rf = Roboflow(api_key=roboflow_api)

for i in range(20):

    project_name = "Annotation-Test-{}".format(i)
    annotation = "Annotation-Test-{}".format(i)
    
    new_project = rf.workspace().create_project(
        project_name=project_name,
        project_license="MIT",
        project_type="object-detection",
        annotation=annotation
    )

    print(new_project)

    ## DEFINITIONS
    # glob params
    image_dir = os.path.join("images")
    file_extension_type = ".jpg"


    # roboflow pip params
    workspace = rf.workspace("WORKSPACE-ID")
    print(workspace)

    # Load the data as a Python dictionary
    dict_data = json.loads(str(workspace))

    # Extract the projects array
    projects = dict_data["projects"]

    potential_matches = projects

    input_string = annotation

    best_match_projectID = find_best_match(input_string, potential_matches)

    print(f"The best match for '{input_string}' is '{best_match_projectID[0]}' with a score of {best_match_projectID[1]}")

    roboflow_projectID = best_match_projectID[0].split("/")
    roboflow_projectID = roboflow_projectID[1]
    print(roboflow_projectID)

    upload_project = rf.workspace().project(roboflow_projectID)

    # get all images from folder
    image_glob = glob.glob(image_dir + '/*' + file_extension_type)

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
            "?api_key=" + roboflow_api + "&overwrite=true"
        ])

        m = MultipartEncoder(fields={'file': (image, buffered.getvalue(), "image/jpeg")})
        r = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type})

        json_blob = r.json()
        # print(json_blob)

        image_id = json_blob['id']
        print("Image ID: " + image_id)

        # Output result
        print(r.json())