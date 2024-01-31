# Python Image Folder Monitoring

## Introduction
The script dynamically monitors a directory for new images and process them as they arrive.

## Installation
To install the necessary dependencies, run the following command:
```bash
pip install -r requirements.txt
```
The `requirements.txt` file should include:
```
opencv-python
pyyaml
inference
```
You also need to have the `image_monitor` module available in your Python environment.

## Usage
To use the script, you need to set the paths to your image directory and configuration file at the top of the script:
```python
config_dir = "/path/to/your/config.yaml"
```
The configuration file should be in YAML format and include the following keys:
```yaml
roboflow:
  project_name: <your_project_name>
  version: <your_model_version>
  api_key: <your_roboflow_api_key>
directory_monitor: <directory_to_monitor>
```
You can then run the script with the following command:
```bash
python main_monitor.py
```

## Features
* Dynamic monitoring of a directory for new images
* Inference on images using a pre-trained model

## Requirements
* Python 3.6 or later
* OpenCV
* PyYAML
* A Roboflow account and API key

## Tags
* `python`
* `image-processing`
* `machine-learning`
* `inference`
* `image-monitoring`
* `roboflow`
* `opencv`
* `pyyaml`

## Categories
* Industry: Healthcare, Manufacturing
* Application: Image Processing, Machine Learning, Real-time Monitoring, Quality Control