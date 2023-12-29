import os
import cv2

# your image folder path
image_folder = "path_to_your_image_folder"

# your label file
label_file = "path_to_your_label_file.txt"

# output folder for yolo format annotations
output_folder = "path_to_your_output_folder"

# read labels
with open(label_file, "r") as f:
    labels = f.readlines()

# for each image
for i, image_name in enumerate(os.listdir(image_folder)):
    # read image
    img = cv2.imread(os.path.join(image_folder, image_name))
    height, width = img.shape[:2]

    # get label
    label = labels[i].strip()

    # the bounding box is the whole image
    x_center = width / 2.0
    y_center = height / 2.0
    w = width
    h = height

    # normalize to [0, 1]
    x_center /= width
    w /= width
    y_center /= height
    h /= height

    # write to output file
    with open(os.path.join(output_folder, os.path.splitext(image_name)[0] + ".txt"), "w") as f:
        f.write(f"{label} {x_center} {y_center} {w} {h}\n")
