from PIL import Image
import cv2
import os, glob
import numpy as np

# loop through folder of images
file_path = "dataset/" # folder of images to test - saved to output
# file_path = "images/single_image" # single image - saved to single_output
extention = ".mp4"
globbed_videos = sorted(glob.glob(file_path + '*' + extention))
print(globbed_videos)

frameCount = 0

for video_files in globbed_videos:
    print(video_files)

    cap = cv2.VideoCapture(video_files)

    # Read until video is completed
    while(cap.isOpened()):
        
        frameCount += 8

        cap.set(cv2.CAP_PROP_POS_FRAMES, frameCount)
        print('Position:', int(cap.get(cv2.CAP_PROP_POS_FRAMES)))

        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret == True:

            # Display the resulting frame
            cv2.imwrite('scrape/IMAGE-' + str(frameCount) + '.jpg', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Break the loop
        else: 
            break

    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()
