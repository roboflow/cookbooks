# Text to Speech Demo

This repository contains the code for the "Narrate Objects in a Room with Computer Vision" YouTube Tutorial.

## Getting Started

First, install the required dependencies for this project:

```
pip3 install -r requirements.txt
```

Then, set your Roboflow API key in an environment variable:

```
export ROBOFLOW_API_KEY=""
```

If you don't already have a Roboflow account, you can [sign up for free](https://app.roboflow.com). You can find your API key by following our [API key tutorial](https://docs.roboflow.com/rest-api#obtaining-your-api-key).

Now you are ready to run the project. You can do so using this command:

```
python3 app.py
```

This script will:

1. Identify the room in which a photo was taken.
2. Find objects in the room (limited to the classes in the `all_finalize` model linked below).
3. Narrate the above pieces of information.

To change the photo that is used, replace the `images/kitchen1.jpeg` value in `app.py` with the location of the photo you want to use.

## Models Used

This project uses the following open-source models on Roboflow Universe:

- [MIT Indoor Scene Recognition](https://universe.roboflow.com/popular-benchmarks/mit-indoor-scene-recognition) for detecting the type of room in which a photo was taken.
- [all_finalize](https://universe.roboflow.com/so-d4hcz/all_finalize) for detecting objects in a room.