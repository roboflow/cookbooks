from roboflowoak import RoboflowOak
from numpy import mean
import cv2
import time
import RPi.GPIO as GPIO
import numpy as np

# Pin Definitions
output_pin = 7  # BOARD pin 12, BCM pin 18

width = 1080
height = 720
dim = (width, height)

size = (width, height)

video_file = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 15, size)

fpsArray = []

if __name__ == '__main__':
    # instantiating an object (rf) with the RoboflowOak module
    # API Key: https://docs.roboflow.com/rest-api#obtaining-your-api-key
    rf = RoboflowOak(model="hand-gesture-r7qgb", confidence=0.2, overlap=0.5,
    version="2", api_key="enter_roboflow_apikey_here", rgb=True,
    depth=False, device=None, blocking=True)
    # Running our model and displaying the video output with detections

    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(output_pin, GPIO.OUT)

    while True:
        t0 = time.time()

        # The rf.detect() function runs the model inference
        result, frame, raw_frame, depth = rf.detect()
        print(result)
        predictions = result["predictions"]
        print(predictions)
        
        # timing: for benchmarking purposes
        t = time.time()-t0
        print("FPS ", 1/t)
        for p in predictions:
                jsonObject = p.json()
                className = jsonObject["class"]
                print("PREDICTIONS: " + str(className))
                if className == "Thumbs up":
                    GPIO.output(output_pin, True)
                else:
                    GPIO.output(output_pin, False)

        # setting parameters for depth calculation
        max_depth = np.amax(depth)
        # print(max_depth)
        # cv2.imshow("depth", depth/max_depth)

        # resize image
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        
        # font
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        org = (25, 25)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 1

        fpsArray.append(1/t)

        averageFPS = mean(fpsArray)

        resized = cv2.putText(resized, 'FPS: ' + str(averageFPS)[:4], org, font, fontScale, color, thickness, cv2.LINE_AA)

        del fpsArray[-20:]

        video_file.write(resized)

        # displaying the video feed as successive frames
        cv2.imshow("frame", resized)
    
        # how to close the OAK inference window / stop inference: CTRL+q or CTRL+c
        if cv2.waitKey(1) == ord('q'):
            GPIO.output(output_pin, False)
            GPIO.cleanup()
            break