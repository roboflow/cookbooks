from roboflow import Roboflow
from PIL import Image
import cv2
import os, glob
import numpy as np

rf = Roboflow(api_key="API")
project = rf.workspace().project("car-models-stage-1")
model = project.version(2).model

rf_color = Roboflow(api_key="API")
project_color = rf_color.workspace().project("car-colors-1smyc")
model_color = project_color.version(5).model

font = cv2.FONT_HERSHEY_SIMPLEX
font_color = (255, 255, 255)
font_thickness = 3 
font_scale = 2

box_color = (255, 255, 255)
box_thickness = 3 
box_scale = 2

distance_color = (255, 255, 255)
distance_thickness = 3

# loop through folder of images
file_path = "test_images_cars/" # folder of images to test - saved to output
# file_path = "images/single_image" # single image - saved to single_output
extention = ".jpg"
globbed_files = sorted(glob.glob(file_path + '*' + extention))
print(globbed_files)

counter = 0

for image_path in globbed_files:

    image_clean = cv2.imread(image_path)
    blk = np.zeros(image_clean.shape, np.uint8)

    pixel_ratio_array = []

    # infer on a local image
    response_json = model.predict(image_path, confidence=30, overlap=30).json()
    # print(response_json)

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
        response_color_json = model_color.predict(image_cropped_path).json()
        
        object_color = response_color_json['predictions'][0]['top']

        print("Color:" + object_color)

        if object_color == "Blue":
            box_color = (255, 0, 0)
            font_color = (255, 0, 0)
        elif object_color == "Grey":
            box_color = (127, 127, 127)
            font_color = (127, 127, 127)
        elif object_color == "Black":
            box_color = (0, 0, 0)
            font_color = (0, 0, 0)
        elif object_color == "Red":
            box_color = (0, 0, 255)
            font_color = (0, 0, 255)
        elif object_color == "Silver":
            box_color = (127, 127, 127)
            font_color = (127, 127, 127)
        elif object_color == "Green":
            box_color = (0, 180, 0)
            font_color = (0, 180, 0)
        elif object_color == "White":
            box_color = (255, 255, 255)
            font_color = (255, 255, 255)

        box_start_point = (int(x0), int(y0))
        class_font_start_point = (int(x0), int(y0)-10)
        confidence_font_start_point = (int(x0)+object_class_text_size[0][0], int(y0)-10)
        box_end_point = (int(x1), int(y1))

        # print(start_point)
        # print(end_point)

        image_drawn = cv2.rectangle(image_clean, box_start_point, box_end_point, box_color, box_thickness)

        image_drawn_blk = cv2.rectangle(blk, box_start_point, box_end_point, box_color, box_thickness)

        image_drawn = cv2.putText(image_drawn, object_class, class_font_start_point, font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        image_drawn = cv2.putText(image_drawn, " - " + object_confidence, confidence_font_start_point, font, font_scale, font_color, font_thickness, cv2.LINE_AA)

        if object_class == "Hyundai Elantra":
            
            elantra_inches = 179.1

            elantra_x_min = int(x0)
            elantra_x_max = int(x1)
            elantra_y_min = int(y0)
            elantra_y_max = int(y1)

            elantra_width = object['width']
            elantra_half_height = int(object['height'] / 2)

            pixel_to_inches = elantra_width / elantra_inches
            pixel_ratio_array.append(pixel_to_inches)
            # print(pixel_to_inches)

        if object_class == "Kia Rio":

            rio_inches = 160

            rio_x_min = int(x0)
            rio_x_max = int(x1)
            rio_y_min = int(y0)
            rio_y_max = int(y1)

            rio_width = object['width']
            rio_half_height = int(object['height'] / 2)

            pixel_to_inches = rio_width / rio_inches
            pixel_ratio_array.append(pixel_to_inches)
            # print(pixel_to_inches)

    cv2.imwrite("boxes" + str(counter) + ".jpg", image_drawn)

    counter += 1

    try:
        if elantra_width and rio_width:

            print(np.mean(pixel_ratio_array))
            pixel_to_inches = int(np.mean(pixel_ratio_array))
            font_color = (255, 255, 255)

            x_calc_1 = abs(elantra_x_min - rio_x_min)
            x_calc_2 = abs(elantra_x_min - rio_x_max)
            x_calc_3 = abs(elantra_x_max - rio_x_max)
            x_calc_4 = abs(elantra_x_max - rio_x_min)
            
            # print(str(x_calc_1))
            # print(str(x_calc_2))
            # print(str(x_calc_3))
            # print(str(x_calc_4))

            min_pixel_distance = min(x_calc_1, x_calc_2, x_calc_3, x_calc_4)

            if x_calc_1 == min_pixel_distance:
                
                estimated_distance_inches = round(min_pixel_distance / pixel_to_inches, 2)
                distance_start_point = (rio_x_min, rio_y_max - rio_half_height)
                distance_end_point = (elantra_x_min, elantra_y_max - elantra_half_height)
                distance_text_point = (rio_x_min + int(x_calc_1 / 5), (elantra_y_max - elantra_half_height) - 10)
                
                print("x_calc_1 - smallest: " + str(x_calc_1))
                print("Estimated Inches: " + str(estimated_distance_inches))
                # print(distance_start_point)
                # print(distance_end_point)

            elif x_calc_2 == min_pixel_distance:
                
                estimated_distance_inches = round(min_pixel_distance / pixel_to_inches, 2)
                distance_start_point = (rio_x_max, rio_y_max - rio_half_height)
                distance_end_point = (elantra_x_min, elantra_y_max - elantra_half_height)
                distance_text_point = (rio_x_max + int(x_calc_2 / 5), (elantra_y_max - elantra_half_height) - 20)
                
                print("x_calc_2 - smallest: " + str(x_calc_2))
                print("Estimated Inches: " + str(estimated_distance_inches))
                # print(distance_start_point)
                # print(distance_end_point)

            elif x_calc_3 == min_pixel_distance:
                
                estimated_distance_inches = round(min_pixel_distance / pixel_to_inches, 2)
                distance_start_point = (elantra_x_max, elantra_y_max - elantra_half_height)
                distance_end_point = (rio_x_max, rio_y_max - rio_half_height)
                distance_text_point = (elantra_x_max + int(x_calc_3 / 5), (elantra_y_max - elantra_half_height) - 20)

                print("x_calc_3 - smallest: " + str(x_calc_3))
                print("Estimated Inches: " + str(estimated_distance_inches))
                # print(distance_start_point)
                # print(distance_end_point)

            else:
                
                estimated_distance_inches = round(min_pixel_distance / pixel_to_inches, 2)
                distance_start_point = (elantra_x_max, elantra_y_max - elantra_half_height)
                distance_end_point = (rio_x_min, rio_y_max - rio_half_height)
                distance_text_point = (elantra_x_max + int(x_calc_4 / 5), (elantra_y_max - elantra_half_height) - 20)

                print("x_calc_4 - smallest: " + str(x_calc_4))
                print("Estimated Inches: " + str(estimated_distance_inches))
                # print(distance_start_point)
                # print(distance_end_point)

            image_drawn = cv2.line(image_drawn, distance_start_point, distance_end_point, distance_color, distance_thickness)

            image_drawn = cv2.putText(image_drawn, "~" + str(estimated_distance_inches) + "in.", distance_text_point, font, font_scale, font_color, font_thickness, cv2.LINE_AA)

            cv2.imwrite("distance_estimate_" + str(counter) + ".jpg", image_drawn)

            # cv2.imwrite("distance_estimate_blk_" + str(counter) + ".jpg", image_drawn_blk)

            # cv2.imshow("distance_estimate_" + str(counter), image_drawn)
    except:
        pass

cv2.waitKey(0)