import depthai as dai
import cv2
import time
import argparse  # Import argparse library

def create_pipeline():
    pipeline = dai.Pipeline()

    # Create nodes
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)

    # Set properties for 4K
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)  # Set to 4K
    cam_rgb.setFps(30)

    xout_rgb.setStreamName("rgb_video")

    # Linking
    cam_rgb.video.link(xout_rgb.input)

    return pipeline

def main(name):  # Add a parameter to accept the name
    # Start pipeline
    pipeline = create_pipeline()
    with dai.Device(pipeline) as device:
        video_queue = device.getOutputQueue(name="rgb_video", maxSize=30, blocking=True)
        frame_count = 0
        start_time = time.time()

        # Create a unique output video filename using the custom name and timestamp
        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_filename = f"m1max_vertical_output_{name}_{timestamp}.mp4"  # Include the name in the filename

        # Define codec and create VideoWriter object for vertical 4K video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec
        out = cv2.VideoWriter(output_filename, fourcc, 30.0, (2160, 3840))  # Vertical resolution for 4K

        while True:
            frame = video_queue.get().getCvFrame()
            # Rotate the frame by 90 degrees to make it vertical
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            cv2.imshow("Video", frame)

            # Write the frame into the file
            out.write(frame)

            # Custom image processing can be added here

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            frame_count += 1

        # Release everything when job is finished
        out.release()
        cv2.destroyAllWindows()

        # Calculate and print FPS
        elapsed_time = time.time() - start_time
        print(f"Average FPS: {frame_count / elapsed_time}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Record vertical video with a custom name")
    parser.add_argument("-n", "--name", type=str, default="m1max", help="Name to include in the output filename")
    
    # Parse arguments
    args = parser.parse_args()

    # Call main function with the provided name
    main(args.name)
