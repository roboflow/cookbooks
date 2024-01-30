# Image Monitor

## Introduction
This Python script is designed to monitor a directory for new images and perform inference on them using a pre-trained machine learning model. The script uses the Roboflow API to load the model and perform inference, and the Supervision Detection API to annotate the images based on the inference results.

## Installation
To install the necessary dependencies, run the following command:
```bash
pip install supervision opencv-python pyyaml
```

## Usage
To use the script, you need to specify the path to the model and the directory to monitor in a YAML configuration file. Here's an example of what the configuration file might look like:

```yaml
model_path: <path_to_your_model>
image_dir: <path_to_your_image_directory>
```

You can then run the script with the following command:

```bash
python main.py
```

## Features
* Monitors a directory for new images
* Performs inference on new images using a pre-trained model
* Annotates images based on inference results
* Saves annotated images to a file

## Requirements
* Python 3.6 or later
* Roboflow API
* Supervision Detection API
* OpenCV
* PyYAML

## Tags
* `image-processing`: The script processes images by performing inference and annotation.
* `machine-learning`: The script uses a pre-trained machine learning model for inference.
* `real-time-monitoring`: The script monitors a directory for new images in real time.

## Categories
This script falls under the categories of Image Processing and Machine Learning. It could be used in a variety of industries, including healthcare (for processing medical images), security (for processing surveillance images), and manufacturing (for processing product images).