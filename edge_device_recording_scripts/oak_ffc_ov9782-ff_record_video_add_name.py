import depthai as dai
import cv2
import time
import argparse
import subprocess
import numpy as np

def create_pipeline(fps, focus):
    pipeline = dai.Pipeline()

    # Create nodes
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)

    # Set properties for the camera
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_800_P)
    cam_rgb.setFps(fps)

    # Disable auto-focus and set a fixed focus value
    cam_rgb.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
    cam_rgb.initialControl.setManualFocus(focus)

    xout_rgb.setStreamName("rgb_video")

    # Linking
    cam_rgb.video.link(xout_rgb.input)

    return pipeline

def main(name, fps, focus):
    pipeline = create_pipeline(fps, focus)
    with dai.Device(pipeline) as device:
        video_queue = device.getOutputQueue(name="rgb_video", maxSize=30, blocking=True)
        frame_count = 0
        start_time = time.time()

        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_filename = f"12-20-2023_videos/ov9782-ff_output_{name}_{timestamp}.mp4"

        # Define the FFmpeg command for writing video in RGB format
        ffmpeg_cmd = ['ffmpeg',
                      '-y',  # Overwrite output file if it exists
                      '-f', 'rawvideo',  # Input format
                      '-vcodec', 'rawvideo',  # Input codec
                      '-s', '600x800',  # Size of one frame after rotation
                      '-pix_fmt', 'rgb24',  # Input pixel format (changed to RGB)
                      '-r', str(fps),  # Frames per second (dynamic)
                      '-i', '-',  # Input comes from a pipe
                      '-an',  # No audio
                      '-vcodec', 'libx264',  # Output codec
                      '-pix_fmt', 'yuv420p',  # Output pixel format
                      output_filename]

        # Start the FFmpeg subprocess
        ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        while True:
            in_frame = video_queue.get()
            if in_frame is not None:
                frame = in_frame.getCvFrame()

                # Convert frame to RGB format
                converted_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Rotate the frame to vertical orientation
                rotated_frame = cv2.rotate(converted_frame, cv2.ROTATE_90_CLOCKWISE)

                # Resize the frame if necessary
                resized_frame = cv2.resize(rotated_frame, (600, 800))

                cv2.imshow("Video", resized_frame)

                # Write frame to FFmpeg subprocess
                try:
                    ffmpeg.stdin.write(resized_frame.tobytes())
                except BrokenPipeError:
                    print("Broken pipe: FFmpeg process may have terminated unexpectedly.")
                    break
                except Exception as e:
                    print(f"Error sending frame: {e}")
                    break

                frame_count += 1

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        elapsed_time = time.time() - start_time
        print(f"Average FPS: {frame_count / elapsed_time}")

        # Finalize video writing
        ffmpeg.stdin.close()
        ffmpeg.wait()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record vertical video with a custom name using FFmpeg")
    parser.add_argument("-n", "--name", type=str, default="m1max", help="Name to include in the output filename")
    parser.add_argument("--fps", type=int, default=30, help="FPS for the camera")
    parser.add_argument("--focus", type=int, default=130, help="Manual focus for the camera")
    
    args = parser.parse_args()
    main(args.name, args.fps, args.focus)
