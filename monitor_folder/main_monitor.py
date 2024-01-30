import yaml
from image_monitor import ImageMonitor 
from roboflow import RoboflowModel

# Load the YAML configuration file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load the model
model = RoboflowModel(config['model_path'])

def infer_image(image_path):
    # Perform inference on the image
    results = model.infer(image_path)

    # Print the results
    print(results)

# Create an ImageMonitor for the directory
monitor = ImageMonitor(config['image_dir'])

# Monitor the directory for new images
for image_path in monitor:
    infer_image(image_path)