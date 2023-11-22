import json

import clip
import numpy as np
import torch
from flask import Flask, render_template, request
from sklearn.metrics.pairwise import cosine_similarity

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/16", device=device)

# the video must be in the static folder to be served
VIDEO_PATH = "/static/titanic.mp4"

app = Flask(__name__)

with open("results.json", "r") as f:
    video_vectors = json.load(f)


@app.route("/", methods=["GET", "POST"])
def search():
    if request.args.get("q"):
        query = request.args.get("q")

        with torch.no_grad():
            query_features = model.encode_text(clip.tokenize([query]).to(device))

            similarities = {}

            for offset, video in zip(video_vectors["time_offset"], video_vectors["clip"]):
                similarity = cosine_similarity(query_features.cpu(), [video])
                similarities[offset] = similarity[0][0]

        # remove values below threshold
        similarities = {k: v for k, v in similarities.items() if v > 0.25}

        print(similarities)

        # bundle so if there is a < 3 second gap between videos, they are grouped together
        bundles = []

        for key in sorted(similarities.keys()):
            if not bundles:
                bundles.append([key])
            else:
                if key - bundles[-1][-1] < 1:
                    bundles[-1].append(key)
                else:
                    bundles.append([key])

        # remove bundles with 1 frame
        bundles = [bundle for bundle in bundles if len(bundle) > 1]

        first_last_bundle = []

        for bundle in bundles:
            first_last_bundle.append([round(bundle[0], 1), round(bundle[-1], 1)])

        return render_template("index.html", results=first_last_bundle, query=query, VIDEO_PATH=VIDEO_PATH)

        # sort results
    return render_template("index.html", VIDEO_PATH=VIDEO_PATH)


if __name__ == "__main__":
    app.run(debug=True)
