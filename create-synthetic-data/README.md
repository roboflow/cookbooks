# Synthetic Fruit Dataset

Code for Roboflow's [How to Create a Synthetic Dataset for Computer Vision tutorial](https://blog.roboflow.ai/how-to-create-a-synthetic-dataset-for-computer-vision).

After downloading Open Images and Fruit images and storing them in your home
directory, running `generate.js` will generate synthetic images labeled with
bounding boxes for object detection like these:

![Example Images](https://blog.roboflow.ai/content/images/2020/04/synthetic-fruit-examples.jpg)

A simple pre-trained model trained with CreateML on the output is available here.

![Pre-trained model](https://blog.roboflow.ai/content/images/2020/04/fruit-cropped.small-1.gif)

## Data Download

6,000 pre-generated output images are available on
[Roboflow Public Datasets here](https://public.roboflow.ai/object-detection/synthetic-fruit).
