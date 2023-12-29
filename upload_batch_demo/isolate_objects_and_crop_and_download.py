
import glob
import os
import json
from PIL import Image
from roboflow import Roboflow

confidence_threshold = 50

rf = Roboflow(api_key="enter_your_roboflow_api_key_here") # enter your Roboflow API key here
project = rf.workspace().project("train-eval")
dataset = project.version(11).download("yolov7") # UNCOMMENT TO DOWNLOAD DATASET IN YOLOv7 FORMAT 
model = project.version(11).model

# set model ID and split it
projectID = model.id
projectID_split = projectID.split("/")

# set name and version from model ID
workspace = projectID_split[0] # project.workspace does not return workspace...
projectName = projectID_split[1]
version = projectID_split[2]

# establish folder naming convertion based on download
folderName = project.name + " " + str(version)
folderName = folderName.replace(" ", "-" )

# loop through files/folder of dataset folder
dataset_path = folderName + "/" # path to train, test, valid folder
get_folders = sorted(glob.glob(dataset_path + '*'))

try:
    os.mkdir("cropped")
except:
    pass

# loop through all the files in the dataset_path folder and filter out the train, test, valid folder
for folders in get_folders:
    if "." in folders:
        pass
    else:
        
        print(folders)
        image_count = 0

        # grab all the .jpg files
        extention_images = ".jpg"
        get_images = sorted(glob.glob(folders + '/images/' + '*' + extention_images))

        # grab all the .txt files
        extention_annotations = ".txt"
        get_annotations = sorted(glob.glob(folders + '/labels/' + '*' + extention_annotations))

        # loop through all the images in the current folder
        for images in get_images:

            object_counter = 0
            
            print("*** Processing image [" + str(image_count) + "/" + str(len(get_images)) + "] - " + "to isolate and crop" + " ***")

            image_split = images.split("/")
            image_name = image_split[3]
            
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

                image_cropped.save('cropped/' + str(object_counter) + '-' +image_name)

                object_counter += 1

                print("ISOLATED AND CROPPED: " + str(object_counter) + " objects")
                print("FROM: " + image_name)

            image_count += 1