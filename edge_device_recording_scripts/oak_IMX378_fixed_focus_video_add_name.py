import depthai as dai
import cv2
import time
import argparse

def create_pipeline(fps, focus):
    pipeline = dai.Pipeline()

    # Create nodes for camera on CAM_A
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    cam_rgb.setFps(fps)
    cam_rgb.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
    cam_rgb.initialControl.setManualFocus(focus)
    xout_rgb.setStreamName("rgb_video")
    cam_rgb.video.link(xout_rgb.input)

    return pipeline

output_folder_name = "12-20-2023_videos/"

def main(name, fps, focus):
    pipeline = create_pipeline(fps, focus)

    with dai.Device(pipeline) as device:
        video_queue = device.getOutputQueue(name="rgb_video", maxSize=30, blocking=True)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_filename = f"{output_folder_name}oak_IMX378_fixed_focus_{name}_{timestamp}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, 30.0, (2160, 3840))

        while True:
            in_frame = video_queue.tryGet()

            if in_frame is not None:
                frame = in_frame.getCvFrame()
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                cv2.imshow("Camera", frame)
                out.write(frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record vertical video from CAM_A with custom settings")
    parser.add_argument("-n", "--name", type=str, default="single_cam", help="Base name for output filename")
    parser.add_argument("--fps", type=int, default=30, help="FPS for the camera")
    parser.add_argument("--focus", type=int, default=130, help="Manual focus for the camera")
    
    args = parser.parse_args()
    main(args.name, args.fps, args.focus)
