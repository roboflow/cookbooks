import requests
import base64
from PIL import Image
from io import BytesIO
import os

INFERENCE_ENDPOINT = "https://infer.roboflow.com"
API_KEY = "API_KEY"
IMAGE_DIR = "fruits"

prompts = ["orange", "apple", "banana"]


def classify_image(image: str) -> dict:
    image_data = Image.open(image)

    buffer = BytesIO()
    image_data.save(buffer, format="JPEG")
    image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    payload = {
        "api_key": API_KEY,
        "subject": {"type": "base64", "value": image_data},
        "prompt": prompts,
    }

    data = requests.post(
        INFERENCE_ENDPOINT + "/clip/compare?api_key=" + API_KEY, json=payload
    )

    return data.json()


def get_highest_prediction(predictions: list) -> str:
    highest_prediction = 0
    highest_prediction_index = 0

    for i, prediction in enumerate(predictions):
        if prediction > highest_prediction:
            highest_prediction = prediction
            highest_prediction_index = i

    return prompts[highest_prediction_index]


for file in os.listdir(IMAGE_DIR):
    image = f"{IMAGE_DIR}/{file}"
    predictions = classify_image(image)
    print(get_highest_prediction(predictions["similarity"]), image)
