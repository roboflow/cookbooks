import yaml
from inference import get_roboflow_model
from image_monitor import ImageMonitor

# Paths
config_dir = "monitor_folder/config.yaml"

# Global variable to store the model
model = None

def infer_image(image_path: str, config: dict):
    """
    Perform inference on the specified image using the loaded model.
    The model is loaded only once and reused in subsequent calls.

    Args:
        image_path (str): Path to the image on which inference is to be performed.
    """
    global model

    # Load the model if it hasn't been loaded yet
    if model is None:
        model_id = config["roboflow"]["project_name"] + "/" + str(config["roboflow"]["version"])
        print(f"Loading model: {model_id}")
        model = get_roboflow_model(model_id=model_id, api_key=config["roboflow"]["api_key"])

    # Run inference
    results = model.infer(image_path)

    # Print results
    print(results)

def main():
    # Load config file
    with open(config_dir, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Monitor a directory for new images
    directory_monitor = config["directory_monitor"]
    wait_time = 1
    monitor = ImageMonitor(directory_monitor, config, wait_time, infer_image)
    monitor.monitor_directory()

if __name__ == "__main__":
    main()