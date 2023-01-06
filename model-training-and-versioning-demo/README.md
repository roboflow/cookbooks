# Model Training and Versioning Demo

This repository contains the code used in the [Create Dataset Versions and Train Models Using the Roboflow Python Package](https://www.youtube.com/watch?v=5jaaEOv_eN8&t=2s) YouTube video.

## Setup

First, install the Roboflow Python package:

```
pip install roboflow
```

Then, set the required environment variables:

- `export ROBOFLOW_API_KEY=""`: Set your Roboflow API key.
- `export WORKSPACE_ID=""`: Set your workspace ID.

Next, open the `demo.py` file and replace the project IDs in the `projects` list with your project IDs.

Then, open the `configurations` folder and create your own augmentation and preprocessing schemas. You can learn more about the structure for these on the [Roboflow documentation for generating versions](https://docs.roboflow.com/python/platform-actions#generate).

Finally, run the `demo.py` file:

```
python3 demo.py
```

*Please note that each training job will use a training credit, which are given in limited amounts.*