import depthai as dai
import cv2
import time
import argparse

def create_pipeline(fps, focus):
    pipeline = dai.Pipeline()

    # Create nodes for first camera (CAM_A), oak
    cam_rgb1 = pipeline.create(dai.node.ColorCamera)
    xout_rgb1 = pipeline.create(dai.node.XLinkOut)
    cam_rgb1.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb1.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    cam_rgb1.setFps(fps)
    cam_rgb1.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
    cam_rgb1.initialControl.setManualFocus(focus)
    xout_rgb1.setStreamName("rgb_video1")
    cam_rgb1.video.link(xout_rgb1.input)

    # Create nodes for second camera (CAM_D), arducam
    cam_rgb2 = pipeline.create(dai.node.ColorCamera)
    xout_rgb2 = pipeline.create(dai.node.XLinkOut)
    cam_rgb2.setBoardSocket(dai.CameraBoardSocket.CAM_D)
    cam_rgb2.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
    cam_rgb2.setFps(fps)
    cam_rgb2.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
    cam_rgb2.initialControl.setManualFocus(focus)
    xout_rgb2.setStreamName("rgb_video2")
    cam_rgb2.video.link(xout_rgb2.input)

    return pipeline

output_folder_name = "12-20-2023_videos/"

def main(name, fps, focus):
    pipeline = create_pipeline(fps, focus)

    with dai.Device(pipeline) as device:
        video_queue1 = device.getOutputQueue(name="rgb_video1", maxSize=30, blocking=True)
        video_queue2 = device.getOutputQueue(name="rgb_video2", maxSize=30, blocking=True)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_filename1 = f"{output_folder_name}oak_IMX378_fixed_focus_{name}_{timestamp}.mp4"
        output_filename2 = f"{output_folder_name}arducam_AR0234_2.3_with_lens_{name}_{timestamp}.mp4"

        fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
        fourcc2 = cv2.VideoWriter_fourcc(*'avc1')
        out1 = cv2.VideoWriter(output_filename1, fourcc1, 30.0, (2160, 3840))
        out2 = cv2.VideoWriter(output_filename2, fourcc2, 30.0, (1200, 1920))

        while True:
            in1 = video_queue1.tryGet()
            in2 = video_queue2.tryGet()

            if in1 is not None:
                frame1 = in1.getCvFrame()
                frame1 = cv2.rotate(frame1, cv2.ROTATE_90_CLOCKWISE)
                cv2.imshow("Camera 1", frame1)
                out1.write(frame1)

            if in2 is not None:
                frame2 = in2.getCvFrame()
                frame2 = cv2.rotate(frame2, cv2.ROTATE_90_CLOCKWISE)
                cv2.imshow("Camera 2", frame2)
                out2.write(frame2)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        out1.release()
        out2.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record vertical video from two cameras with custom settings")
    parser.add_argument("-n", "--name", type=str, default="dual_cam", help="Base name for output filenames")
    parser.add_argument("--fps", type=int, default=30, help="FPS for both cameras")
    parser.add_argument("--focus", type=int, default=130, help="Manual focus for both cameras")
    
    args = parser.parse_args()
    main(args.name, args.fps, args.focus)
