import depthai as dai
import cv2
import time
import argparse
from depthai_sdk import OakCamera, RecordType

def main(name, fps, focus, autofocus, quality):
    with OakCamera() as oak:
        af_mode = dai.RawCameraControl.AutoFocusMode.AUTO if autofocus else dai.RawCameraControl.AutoFocusMode.OFF

        c1 = oak.create_camera(dai.CameraBoardSocket.CAM_A, resolution=dai.ColorCameraProperties.SensorResolution.THE_4_K, fps=fps, encode='MJPEG')
        c1.config_encoder_mjpeg(quality=quality,lossless=False)
        c1.config_color_camera(af_mode=af_mode, manual_focus=focus)

        c2 = oak.create_camera(dai.CameraBoardSocket.CAM_C, resolution=dai.ColorCameraProperties.SensorResolution.THE_800_P, fps=fps, encode='MJPEG')
        c2.config_encoder_mjpeg(quality=quality,lossless=False)
        c2.config_color_camera(af_mode=af_mode, manual_focus=focus)


        # Synchronize & save all (encoded) streams
        oak.record([c1.out.encoded,c2.out.encoded], './'+name, RecordType.VIDEO)
        # Show color stream
        oak.visualize([c1.out.camera,c2.out.camera], scale=1/4, fps=True)

        oak.start(blocking=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record vertical video with custom settings")
    parser.add_argument("-n", "--name", type=str, default="m1max", help="Name to include in the output filename")
    parser.add_argument("-f", "--fps", type=int, default=30, help="Frames per second for video recording")
    parser.add_argument("-focus", "--focus", type=int, default=130, help="Manual focus value (0 to 255)")
    parser.add_argument("-a", "--autofocus", action='store_true', help="Enable autofocus")
    parser.add_argument("-q", "--quality", type=int, default=100, help="Set the encoding quality (0 to 100)")

    args = parser.parse_args()
    main(args.name, args.fps, args.focus, args.autofocus, args.quality)