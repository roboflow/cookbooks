import json

from roboflow import CLIPModel

VIDEO_PATH = "titanic.mp4"

model = CLIPModel(api_key="API_KEY")

job_id, signed_url, expire_time = model.predict_video(
    VIDEO_PATH,
    fps=1,
    prediction_type="batch-video",
)

results = model.poll_until_video_results(job_id)

with open("results.json", "w") as f:
    json.dump(results, f)
