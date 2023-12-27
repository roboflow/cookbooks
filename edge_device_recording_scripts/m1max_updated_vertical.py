import depthai as dai
import cv2
import time
import argparse

def create_pipeline(fps, focus, autofocus):
    pipeline = dai.Pipeline()

    # Create nodes
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)

    # Set properties for 4K
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    cam_rgb.setFps(fps)

    # Set autofocus or manual focus
    if autofocus:
        cam_rgb.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.AUTO)
    else:
        cam_rgb.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
        cam_rgb.initialControl.setManualFocus(focus)

    xout_rgb.setStreamName("rgb_video")

    # Linking
    cam_rgb.video.link(xout_rgb.input)

    return pipeline

def main(name, fps, focus, autofocus):
    # Determine focus type
    focus_type = "autofocus" if autofocus else "fixed_focus"

    pipeline = create_pipeline(fps, focus, autofocus)
    with dai.Device(pipeline) as device:
        video_queue = device.getOutputQueue(name="rgb_video", maxSize=30, blocking=True)
        frame_count = 0
        start_time = time.time()

        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_filename = f"12-20-2023_videos/m1max_updated_vertical_{focus_type}_{name}_{timestamp}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (2160, 3840))  # Resolution changed for vertical video

        while True:
            frame = video_queue.get().getCvFrame()

            # Rotate the frame by 90 degrees to make it vertical
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            cv2.imshow("Video", frame)
            out.write(frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            frame_count += 1

        out.release()
        cv2.destroyAllWindows()
        elapsed_time = time.time() - start_time
        print(f"Average FPS: {frame_count / elapsed_time}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record vertical video with custom settings")
    parser.add_argument("-n", "--name", type=str, default="m1max", help="Name to include in the output filename")
    parser.add_argument("-f", "--fps", type=int, default=30, help="Frames per second for video recording")
    parser.add_argument("-c", "--focus", type=int, default=130, help="Manual focus value (0 to 255)")
    parser.add_argument("-a", "--autofocus", action='store_true', help="Enable autofocus")

    args = parser.parse_args()
    main(args.name, args.fps, args.focus, args.autofocus)
