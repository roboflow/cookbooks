import depthai as dai
import cv2
import time
import argparse



def create_camera(pipeline, camera_id, fps, focus, autofocus, exposure_time, iso):
    cam = pipeline.create(dai.node.ColorCamera)
    xout_video = pipeline.create(dai.node.XLinkOut)
    xout_still = pipeline.create(dai.node.XLinkOut)

    cam.setBoardSocket(camera_id)
    cam.setFps(fps)

    # Set the highest resolution for still capture
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_12_MP)  # Adjust this based on your camera

    if autofocus:
        cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
    else:
        cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
        cam.initialControl.setManualFocus(focus)

    if exposure_time is not None and iso is not None:
        cam.initialControl.setManualExposure(exposure_time, iso)

    # Setup the output streams
    xout_video.setStreamName(f"rgb_video_{camera_id}")
    cam.video.link(xout_video.input)

    xout_still.setStreamName(f"still_{camera_id}")
    cam.still.link(xout_still.input)

    return cam, xout_video, xout_still

def apply_rotation(frame, rotation):
    if rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return frame

def create_pipeline(args):
    pipeline = dai.Pipeline()
    create_camera(pipeline, dai.CameraBoardSocket.CAM_A, args.fps, args.focus, args.autofocus, args.exposure_time, args.iso)
    return pipeline

def get_fourcc(codec, output_format):
    if output_format == "mp4":
        return cv2.VideoWriter_fourcc(*'avc1')
    elif output_format == "avi":
        if codec == 'mjpeg':
            return cv2.VideoWriter_fourcc(*'MJPG')
        else:
            return cv2.VideoWriter_fourcc(*'XVID')
        
def main(args):
    pipeline = create_pipeline(args)

    with dai.Device(pipeline) as device:
        video_queue = device.getOutputQueue(name=f"rgb_video_{dai.CameraBoardSocket.CAM_A}", maxSize=30, blocking=True)
        still_queue = device.getOutputQueue(name=f"still_{dai.CameraBoardSocket.CAM_A}", maxSize=30, blocking=False)
        cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)

        last_capture_time = time.time()

        while True:
            in_frame = video_queue.get()
            if in_frame is None:
                break

            frame = in_frame.getCvFrame()
            rotated_frame = apply_rotation(frame, args.rotation)

            # Display the video frame
            resized_frame = cv2.resize(rotated_frame, (640, 360))
            cv2.imshow("Preview", resized_frame)

            # Check if it's time to capture a still image
            if time.time() - last_capture_time >= args.photo_interval:
                # Check if a still image is available
                if still_queue.has():
                    in_still = still_queue.get()
                    still_frame = in_still.getCvFrame()

                    # Save the still image
                    image_filename = f"{args.output_dir}/still_{int(time.time())}.png"
                    cv2.imwrite(image_filename, still_frame)

                    # Update the last capture time
                    last_capture_time = time.time()

            # Check for 'q' key to quit
            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take photos from a camera with custom settings")

# Arguments for the camera
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for the camera")
    parser.add_argument("--width", type=int, default=1920, help="Width of the video frame")
    parser.add_argument("--height", type=int, default=1080, help="Height of the video frame")
    parser.add_argument("--focus", type=int, default=130, help="Manual focus value for the camera (0 to 255)")
    parser.add_argument("--codec", type=str, default="mjpeg", choices=["h264", "h265", "mjpeg", "XVID"], help="Video codec for recording (h264, h265, mjpeg)")
    parser.add_argument("--output_dir", type=str, default="output_videos", help="Directory to save the output video")
    parser.add_argument("--autofocus", action='store_true', help="Enable autofocus for the camera")
    parser.add_argument("--res", type=str, default="1080P", choices=["720P", "800P", "1080P", "1200P", "1440x1080", "5MP", "12MP", "13MP", "48MP", "4_K", "4000x3000", "5312x6000"], help="Resolution for the camera (1080P, 4K, 12MP)")
    parser.add_argument('--name', type=str, help='Description for the name argument')
    parser.add_argument("--output_format", type=str, default="mp4", choices=["mp4", "avi"], help="Output video format (mp4 or avi)")
    parser.add_argument("--rotation", type=int, default=0, choices=[0, 90, 180, 270], help="Rotation of the video frame (0, 90, 180, 270 degrees)")
    parser.add_argument("--exposure_time", type=int, default=None, help="Manual exposure time for the camera in microseconds")
    parser.add_argument("--iso", type=int, default=None, help="Sensor's sensitivity to light. Lower ISO values mean the sensor is less sensitive to light, which is ideal for bright environments, whereas higher ISO values increase the sensor's sensitivity, making it better for low-light conditions. However, increasing the ISO also increases the noise or grain in the image, potentially reducing image quality.")
    parser.add_argument("--photo_interval", type=int, default=5, help="Interval between photos in seconds")

    args = parser.parse_args()
    main(args)






# import depthai as dai
# import cv2
# import time
# import argparse
# import os

# def create_camera(pipeline, camera_id, focus, width, height, autofocus, exposure_time, iso):
#     cam = pipeline.create(dai.node.ColorCamera)
#     still = pipeline.create(dai.node.XLinkOut)
#     control_in = pipeline.create(dai.node.XLinkIn)  # Create a control input node

#     # Set camera parameters
#     cam.setBoardSocket(camera_id)
#     # Set other camera parameters as needed, e.g., resolution, fps, etc.

#     if autofocus:
#         cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
#     else:
#         cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
#         cam.initialControl.setManualFocus(focus)

#     if exposure_time is not None and iso is not None:
#         cam.initialControl.setManualExposure(exposure_time, iso)

#     # Link the still output
#     still.setStreamName("still")
#     cam.still.link(still.input)

#     # Setup control input
#     control_in.setStreamName("control")
#     control_in.out.link(cam.inputControl)

#     return cam, still, control_in


# def create_pipeline(args):
#     pipeline = dai.Pipeline()
#     create_camera(pipeline, dai.CameraBoardSocket.CAM_A, args.focus, args.width, args.height, args.autofocus, args.exposure_time, args.iso)
#     return pipeline

# def main(args):
#     pipeline = create_pipeline(args)

#     with dai.Device(pipeline) as device:
#         still_queue = device.getOutputQueue(name="still", maxSize=30, blocking=True)
#         controlQueue = device.getInputQueue("control")
        
#         last_capture_time = time.time()

#         # Create output directory if it doesn't exist
#         if not os.path.exists(args.output_dir):
#             os.makedirs(args.output_dir)

#         while True:
#             # Trigger a still capture event every few seconds
#             if time.time() - last_capture_time >= args.photo_interval:
#                 ctrl = dai.CameraControl()
#                 ctrl.setCaptureStill(True)
#                 controlQueue.send(ctrl)
#                 last_capture_time = time.time()

#             in_frame = still_queue.get()
#             frame = in_frame.getCvFrame()

#             # Save the still image
#             image_filename = f"{args.output_dir}/camera_{args.name}_"
#             image_filename += f"{args.width}x{args.height}_"
#             image_filename += f"focus{args.focus}_exposure{args.exposure_time}_iso{args.iso}_"
#             image_filename += f"{int(time.time())}.png"
#             cv2.imwrite(image_filename, frame)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Capture still photos from a camera with custom settings")

# # Arguments for the camera
#     parser.add_argument("--fps", type=int, default=30, help="Frames per second for the camera")
#     parser.add_argument("--width", type=int, default=1920, help="Width of the video frame")
#     parser.add_argument("--height", type=int, default=1080, help="Height of the video frame")
#     parser.add_argument("--focus", type=int, default=130, help="Manual focus value for the camera (0 to 255)")
#     parser.add_argument("--codec", type=str, default="mjpeg", choices=["h264", "h265", "mjpeg", "XVID"], help="Video codec for recording (h264, h265, mjpeg)")
#     parser.add_argument("--output_dir", type=str, default="output_videos", help="Directory to save the output video")
#     parser.add_argument("--autofocus", action='store_true', help="Enable autofocus for the camera")
#     # parser.add_argument("--res", type=str, default="1080P", choices=["720P", "800P", "1080P", "1200P", "1440x1080", "5MP", "12MP", "13MP", "48MP", "4_K", "4000x3000", "5312x6000"], help="Resolution for the camera (1080P, 4K, 12MP)")
#     parser.add_argument('--name', type=str, help='Description for the name argument')
#     parser.add_argument("--output_format", type=str, default="mp4", choices=["mp4", "avi"], help="Output video format (mp4 or avi)")
#     parser.add_argument("--rotation", type=int, default=0, choices=[0, 90, 180, 270], help="Rotation of the video frame (0, 90, 180, 270 degrees)")
#     parser.add_argument("--exposure_time", type=int, default=None, help="Manual exposure time for the camera in microseconds")
#     parser.add_argument("--iso", type=int, default=None, help="Sensor's sensitivity to light. Lower ISO values mean the sensor is less sensitive to light, which is ideal for bright environments, whereas higher ISO values increase the sensor's sensitivity, making it better for low-light conditions. However, increasing the ISO also increases the noise or grain in the image, potentially reducing image quality.")
#     parser.add_argument("--photo_interval", type=int, default=5, help="Interval between photos in seconds")

#     args = parser.parse_args()
#     main(args)