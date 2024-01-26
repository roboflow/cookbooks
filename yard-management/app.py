import argparse
import json
from functools import partial
from typing import Callable, Optional, Tuple

import cv2
import numpy as np
import supervision as sv
import tqdm
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import VideoFrame, display_image
from PIL import Image

tracker = sv.ByteTrack()
smoother = sv.DetectionsSmoother()
video_info = sv.VideoInfo.from_video_path(video_path="container.mp4")
height, width = video_info.resolution_wh

line_zone = sv.LineZone(
    start=sv.Point(x=width / 2, y=0), end=sv.Point(x=width / 2, y=height)
)

containers_captured = set({})

parser = argparse.ArgumentParser()

# python3 app.py --video=video.mp4 --model-id=model/1 --output=output.mp4
parser.add_argument("--video", type=str, required=True)
parser.add_argument("--model-id", type=str, required=True)
parser.add_argument("--output", type=str, required=True)

args = parser.parse_args()


def callback(
    predictions: dict,
    scene: VideoFrame,
    display_size: Optional[Tuple[int, int]] = (1280, 720),
    on_frame_rendered: Callable[[np.ndarray], None] = display_image,
) -> None:
    classes = [i["class"] for i in predictions["predictions"]]
    detections = sv.Detections.from_roboflow(predictions)

    detections = detections[detections.confidence > 0.7]
    detections = tracker.update_with_detections(detections)
    detections = smoother.update_with_detections(detections)

    class_names = [classes[i] for i in detections.class_id]

    container_detections = detections[detections.class_id == 0]

    _, in_to_out = line_zone.trigger(container_detections)

    out_count = line_zone.out_count

    global containers_captured

    for i, detection in enumerate(in_to_out):
        corresponding_detection = detections[i]

        # must be container
        if (
            corresponding_detection.tracker_id[0] not in containers_captured
            and corresponding_detection.class_id[0] == 0
        ):
            roi = corresponding_detection.xyxy[0]
            x0, y0, x1, y1 = roi.tolist()

            x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)

            if x0 < 0:
                x0 = 0

            if y0 < 0:
                y0 = 0

            container_image = scene.image[y0:y1, x0:x1]

            # convert to rgb
            container_image = container_image[:, :, ::-1]

            print("Container detected")

            try:
                Image.fromarray(container_image).save(
                    f"results/container_{len(containers_captured) + 1}.png"
                )
            except:
                print("Error saving image")

            containers_captured.add(corresponding_detection.tracker_id[0])

    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    scene = cv2.resize(scene.image, display_size)

    annotated_image = bounding_box_annotator.annotate(
        scene=scene, detections=detections
    )
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=class_names
    )

    annotated_image = sv.draw_line(
        scene=annotated_image,
        start=sv.Point(x=width / 2, y=0),
        end=sv.Point(x=width / 2, y=height),
        thickness=3,
        color=sv.Color(r=0, g=255, b=0),
    )

    annotated_image = sv.draw_text(
        scene=annotated_image,
        text="Containers found: " + str(len(containers_captured)),
        text_anchor=sv.Point(x=100, y=100),
        background_color=sv.Color(r=0, g=0, b=0),
        text_color=sv.Color(r=255, g=255, b=255),
    )

    on_frame_rendered(annotated_image)


output_size = (height, width)
fps = video_info.fps
video_sink = cv2.VideoWriter(
    "output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, output_size
)
on_prediction = partial(
    callback, display_size=output_size, on_frame_rendered=video_sink.write
)

pipeline = InferencePipeline.init(
    model_id=args.model_id,
    video_reference=args.video,
    on_prediction=on_prediction,
)
pipeline.start()
pipeline.join()

model = ocr_predictor(
    det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True
)

ocr_results = []

for i in tqdm.tqdm(range(len(containers_captured))):
    doc = DocumentFile.from_images([f"./results/container_{i + 1}.png"])

    result = model(doc).export()

    text = ""

    for item in result["pages"]:
        for b in item["blocks"]:
            for l in b["lines"]:
                words = l["words"]

                for w in words:
                    text += w["value"]

                text += " | "

    ocr_results.append(text)

with open("ocr_results.json", "w+") as f:
    json.dump(ocr_results, f)
