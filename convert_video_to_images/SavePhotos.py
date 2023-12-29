from roboflow import Roboflow
import os, glob

rf = Roboflow(api_key="enter_roboflow_apikey_here") # enter your Roboflow api key here
project = rf.workspace().project("odometer-digits")
model = project.version(53).model
images_folder = "test/images/"

# grab all the .jpg files
extention_images = ".jpg"
get_images = sorted(glob.glob(images_folder + '*' + extention_images))
counter = 0

print(get_images)

# loop through all the images in the current folder
for images in get_images:

    # infer on a local image
    print(model.predict(images, confidence=40, overlap=30).json())

    # visualize your prediction
    model.predict(images, confidence=40, overlap=30).save("prediction"+str(counter)+".jpg")

    # infer on an image hosted elsewhere
    # print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())

    counter += 1