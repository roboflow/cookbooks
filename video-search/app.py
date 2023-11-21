import json

import clip
import numpy as np
import torch
from flask import Flask, render_template, request
from sklearn.metrics.pairwise import cosine_similarity

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

app = Flask(__name__)

with open("results.json", "r") as f:
    video_vectors = json.load(f)


@app.route("/", methods=["GET", "POST"])
def search():
    if request.args.get("q"):

        query = request.args.get("q")

        with torch.no_grad():
            query_features = model.encode_text(clip.tokenize(query).to(device))

        similarities = []

        for video in video_vectors["clip"]:
            video_features = torch.tensor(np.array(video).reshape(1, -1)).to(device)
            similarity = cosine_similarity(query_features.cpu(), video_features.cpu())
            similarities.append(similarity.item())

        # return results as {idx: similarity}
        similarities = dict(enumerate(similarities))

        # remove values below threshold
        similarities = {k: v for k, v in similarities.items() if v > 0.1}

        # bundle so if there is a < 10 frame gap, it is considered the same video, else it is a new video
        bundles = []

        for idx, similarity in similarities.items():
            if bundles:
                if idx - bundles[-1][-1] < 10:
                    bundles[-1].append(idx)
                else:
                    bundles.append([idx])
            else:
                bundles.append([idx])

        # get first and last values in each bundle
        first_last_bundle = []

        for bundle in bundles:
            first_last_bundle.append([bundle[0], bundle[-1]])

        # convert to timestamps
        for bundle in first_last_bundle:
            bundle[0] = bundle[0] / 5
            bundle[1] = bundle[1] / 5

        return render_template("index.html", results=first_last_bundle, query=query)

        # sort results
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
