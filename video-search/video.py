import json

from roboflow import CLIPModel

model = CLIPModel(api_key="4LoVtLxWAd8lePVDKN0w")

job_id, signed_url, expire_time = model.predict_video(
    "titanic.mp4",
    fps=1,
    prediction_type="batch-video",
)

results = model.poll_until_video_results(job_id)

with open("results.json", "w") as f:
    json.dump(results, f)
