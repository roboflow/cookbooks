import requests
import argparse
import base64

parser = argparse.ArgumentParser()

parser.add_argument('--image', type=str, required=True)
parser.add_argument('--tags', type=str, required=True)
parser.add_argument('--roboflow_api_key', type=str, required=True)

args = parser.parse_args()

tags = [tag.strip() for tag in args.tags.split(",")]

#Define Request Payload
infer_clip_payload = {
    "subject": {
        "type": "base64",
        "value": base64.b64encode(open(args.image, "rb").read()).decode("utf-8"),
    },
    "subject_type": "image",
    "prompt": tags,
    "prompt_type": "text",
}

try:
    res = requests.post(
        f"http://infer.roboflow.com/clip/compare?api_key={args.roboflow_api_key}",
        json=infer_clip_payload,
    )
except:
    print("Error: Request failed. Ensure you have an active internet connection and that your Roboflow API key is correct.")

similarity = res.json()['similarity']

# get idx of highest similarity
idx = similarity.index(max(similarity))

# get tag of highest similarity
tag = tags[idx]

print(f"Most similar tag: {tag}")