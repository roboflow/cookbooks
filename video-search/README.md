# Build a Video Search Engine

With [Roboflow Video Inference](https://roboflow.com), you can calculate CLIP vectors for use in creating a video search engine that accepts natural language queries and returns related frames.

This repository contains all the code you need to build a custom video search engine.

<video width="100%" controls>
  <source src="https://media.roboflow.com/video-search-demo.mp4" type="video/mp4">
</video>

## Getting Started

To get started, first clone this project:

```
git clone https://github.com/roboflow/video-search
```

Then, install the required dependencies:

```
pip3 install -r requirements.txt
```

Next, select a video that you want to search. Open `video.py` and update the `VIDEO_PATH` value to point to your video.

Then, run the `video.py` script:

```
python video.py
```

This script will send your video to Roboflow and calculate CLIP vectors for every fifth frame. The script will continuously poll the Roboflow API until your video has been processed. The time it takes for your video to process will depend on how long your video is.

Once your video has been processed, the script will save a `results.json` file containing the CLIP vectors for each frame.

Next, run the `app.py` script to start the video search engine:

```
python app.py
```

## License

This project is licensed under an [MIT license](LICENSE).