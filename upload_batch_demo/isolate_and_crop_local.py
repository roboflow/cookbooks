
import glob
import os
import json
from PIL import Image
from roboflow import Roboflow

confidence_threshold = 50

rf = Roboflow(api_key="API")
project = rf.workspace().project("train-eval")
model = project.version(11).model

try:
    os.mkdir("cropped")
except:
    pass

try:
    os.mkdir("images")
except:
    pass
        
image_dir = os.path.join("images")

image_count = 0

# grab all the .jpg files
extention_images = ".jpg"
get_images = sorted(glob.glob(image_dir + '/' + '*' + extention_images))

object_counter = 0

# loop through all the images in the current folder
for images in get_images:
    
    print("*** Processing image [" + str(image_count) + "/" + str(len(get_images)) + "] - " + "to isolate and crop" + " ***")

    # isolate image path
    image_name = "False-Positive"
    
    # perform roboflow model prediction
    response = json.dumps(model.predict(images, confidence=confidence_threshold, overlap=30).json(), indent=4)            
    jsonLoaded = json.loads(response)

    # Opens a image in RGB mode
    image_load = Image.open(images)

    # loop through all the response prediction objects and append their class names to class_prediction_array
    for objects in jsonLoaded['predictions']:

        object_width = objects["width"]

        object_height = objects["height"]

        left = objects["x"] - objects["width"] / 2

        top = objects["y"] - objects['height'] / 2

        right = objects["x"] + objects['width'] / 2

        bottom = objects["y"] + objects['height'] / 2

        image_cropped = image_load.crop((left, top, right, bottom))

        image_cropped.save('cropped/' + image_name  + '-' + str(object_counter) + '.jpg')

        object_counter += 1

        print("ISOLATED AND CROPPED: " + str(object_counter) + " objects")

    image_count += 1