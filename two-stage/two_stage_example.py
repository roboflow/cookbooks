from roboflow import Roboflow
from PIL import Image
import cv2
import os, glob
import numpy as np

# Roboflow Model 1 and Model 2 Config.
rf = Roboflow(api_key="API")
project_stage_1 = rf.workspace().project("project-id")
model_stage_1 = project_stage_1.version(1).model

rf_color = Roboflow(api_key="API")
project_stage_2 = rf_color.workspace().project("project-id")
model_stage_2 = project_stage_2.version(1).model

# Font and Bounding Box Config.
font = 4
font_color = (255, 255, 255)
font_thickness = 1
font_scale = 1

box_color = (255, 255, 255)
box_thickness = 1 
box_scale = 1

distance_color = (255, 255, 255)
distance_thickness = 1

file_path = "test_images/" # folder of images to test - saved to output
# file_path = "images/single_image" # single image - saved to single_output
extention = ".jpg"
globbed_files = sorted(glob.glob(file_path + '*' + extention))
print(globbed_files)

counter = 0

# loop through folder of images
for image_path in globbed_files:

    image_clean = cv2.imread(image_path)
    blk = np.zeros(image_clean.shape, np.uint8)

    pixel_ratio_array = []

    # infer on a local image
    response_json = model_stage_1.predict(image_path, confidence=30, overlap=30).json()
    # print(response_json)

    print("File: " + image_path)
    print()

    for object in response_json["predictions"]:
        
        object_class = str(object['class'])
        object_class_text_size = cv2.getTextSize(object_class, font, font_scale, font_thickness)
        print("Class: " + object_class)
        object_confidence = str(round(object['confidence']*100 , 2)) + "%"
        print("Confidence: " + object_confidence)

        # pull bbox coordinate points
        x0 = object['x'] - object['width'] / 2
        y0 = object['y'] - object['height'] / 2
        x1 = object['x'] + object['width'] / 2
        y1 = object['y'] + object['height'] / 2
        box = (x0, y0, x1, y1)
        # print("Bounding Box Cordinates:" + str(box))

        image_cropped = image_clean[int(y0):int(y1), int(x0):int(x1)]

        image_cropped_path = "cropped/cropped_" + object_class + "_" + str(counter) + ".jpg"

        cv2.imwrite(image_cropped_path, image_cropped)

        # infer on a local image
        response_color_json = model_stage_2.predict(image_cropped_path).json()
        
        object_condition = response_color_json['predictions'][0]['top']

        print("Condition:" + object_condition)
        print()

        box_start_point = (int(x0), int(y0))
        class_font_start_point = (int(x0), int(y0)-10)
        confidence_font_start_point = (int(x0)+object_class_text_size[0][0], int(y0)-10)
        box_end_point = (int(x1), int(y1))

        # print(start_point)
        # print(end_point)

        image_drawn = cv2.rectangle(image_clean, box_start_point, box_end_point, box_color, box_thickness)

        image_drawn_blk = cv2.rectangle(blk, box_start_point, box_end_point, box_color, box_thickness)

        image_drawn = cv2.putText(image_drawn, object_class, class_font_start_point, font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        image_drawn = cv2.putText(image_drawn, " - " + object_condition + " - " + object_confidence, confidence_font_start_point, font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    cv2.imwrite("boxes" + str(counter) + ".jpg", image_drawn)

    counter += 1

cv2.waitKey(0)