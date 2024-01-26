import depthai as dai
import cv2
import time
import argparse
import time
from itertools import cycle

def create_camera(pipeline, camera_id, fps, focus, width, height, autofocus, exposure_time, iso):
    cam = pipeline.create(dai.node.ColorCamera)
    xout = pipeline.create(dai.node.XLinkOut)

    cam.setBoardSocket(camera_id)
    cam.setFps(fps)

    # Set the resolution directly
    cam.setVideoSize(width, height)
    cam.setPreviewSize(width, height)

    if autofocus:
        cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
    else:
        cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
        cam.initialControl.setManualFocus(focus)

    if exposure_time is not None and iso is not None:
        cam.initialControl.setManualExposure(exposure_time, iso)

    xout.setStreamName(f"rgb_video_{camera_id}")
    cam.video.link(xout.input)

    return cam, xout


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

    # Create and set up the camera
    cam, xout = create_camera(pipeline, dai.CameraBoardSocket.CAM_A, args.fps, args.focus, args.width, args.height, args.autofocus, args.exposure_time, args.iso)

    # Create XLinkIn node for camera control and link it
    controlIn = pipeline.create(dai.node.XLinkIn)
    controlIn.setStreamName("camera_control")
    controlIn.out.link(cam.inputControl)

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
        timestamp = time.strftime("%Y%m%d%H%M%S")

        # Modify the output_filename line to include camera settings
        output_filename = f"{args.output_dir}/camera_{args.name}_"
        output_filename += f"{args.width}x{args.height}_{args.fps}fps"
        output_filename += f"_focus{args.focus}_exposure{args.exposure_time}_iso{args.iso}"
        output_filename += f"_rotation{args.rotation}.{args.output_format}"

        # Adjust the frame size for the VideoWriter based on rotation
        frame_size = (args.width, args.height)
        if args.rotation in [90, 270]:
            frame_size = (args.height, args.width)

        fourcc = get_fourcc(args.codec, args.output_format)
        out = cv2.VideoWriter(output_filename, fourcc, args.fps, frame_size)

        video_queue = device.getOutputQueue(name=f"rgb_video_{dai.CameraBoardSocket.CAM_A}", maxSize=30, blocking=True)
        cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)

        # Initialize frame rate calculation variables
        frame_count = 0
        start_time = time.time()
        fps = 0

        while True:
            in_frame = video_queue.get()
            if in_frame is None:
                break

            frame = in_frame.getCvFrame()

            # Rotate the frame
            rotated_frame = apply_rotation(frame, args.rotation)

            out.write(rotated_frame)

            # Frame rate calculation
            frame_count += 1
            if frame_count >= 10:  # Adjust this number as needed
                end_time = time.time()
                fps = frame_count / (end_time - start_time)
                print(f"FPS: {fps:.2f}")  # Print FPS to the terminal
                start_time = time.time()
                frame_count = 0

            # Adjust preview size based on rotation
            preview_size = (640, 360)
            if args.rotation in [90, 270]:
                preview_size = (360, 640)

            resized_frame = cv2.resize(rotated_frame, preview_size)
            cv2.imshow("Preview", resized_frame)
            if cv2.waitKey(1) == ord('q'):
                break

        out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record video from a camera with custom settings")

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

    args = parser.parse_args()
    main(args)
