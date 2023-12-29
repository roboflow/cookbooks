from roboflowoak import RoboflowOak
import cv2
import csv
import time
import numpy as np

frame_counter = 0

frame_width = 640
frame_height = 640
fps = 20

size = (frame_width, frame_height)

# field names
fields = ['timestamp', 'class_name','x_cord', 'y_cord', 'width', 'height'] 

# name of csv file 
csv_filename = "DetectionLog.csv"

# writing to csv file 
with open(csv_filename, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 

    # writing the fields 
    csvwriter.writerow(fields) 

if __name__ == '__main__':
    
    # instantiating an object (rf) with the RoboflowOak module
    # API Key: https://docs.roboflow.com/rest-api#obtaining-your-api-key
    rf = RoboflowOak(model="utility-poles-fbshq", confidence=0.05, overlap=0.5,
    version="10", api_key="enter_roboflow_apikey_here", rgb=True,
    depth=False, device=None, blocking=True)

    # Below VideoWriter object will create
    # a frame of above defined The output 
    # is stored in 'filename.avi' file.
    write_video = cv2.VideoWriter('filename.avi', 
                            cv2.VideoWriter_fourcc(*'MJPG'),
                            fps, size)

    # Running our model and displaying the video output with detections
    while True:

        t0 = time.time()
        # The rf.detect() function runs the model inference
        result, frame, raw_frame, depth = rf.detect()
        predictions = result["predictions"]
        
        # timing: for benchmarking purposes
        t = time.time()-t0
        print("FPS ", 1/t)
        
        for p in predictions:
                
                jsonObject = p.json()
                class_name = jsonObject["class"]
                x_cord = jsonObject["x"]
                y_cord = jsonObject["y"]
                width = jsonObject["width"]
                height = jsonObject["height"]
                
                print("PREDICTIONS: " + str(class_name))
                
                # Filename
                filename = class_name + str(frame_counter) + ".jpg"
                
                # Using cv2.imwrite() method
                # Saving the image
                cv2.imwrite(filename, frame)

                # Dictionary
                dict = {"timestamp":str(t), "class_name":str(class_name), "x_cord":str(x_cord),"y_cord":str(y_cord), "width":str(width), "height":str(height)}

                # writing to csv file 
                with open(csv_filename, 'a') as csvfile: 
                    # creating a csv writer object 
                    dict_object = csv.DictWriter(csvfile, fieldnames=fields) 

                    # write dict to CSV
                    dict_object.writerow(dict)

        # displaying the video feed as successive frames
        cv2.imshow("frame", frame)
        write_video.write(frame)
    
        # how to close the OAK inference window / stop inference: CTRL+q or CTRL+c
        if cv2.waitKey(1) == ord('q'):
            write_video.release()
            break