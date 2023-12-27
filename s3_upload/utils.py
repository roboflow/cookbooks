import yaml
import logging
import datetime

def read_config(file_path):
    """Reads a configuration file in YAML format and returns a dictionary of its contents.

    :param file_path: Path to the YAML configuration file.
    :return: Dictionary containing the configuration settings.
    """
    try:
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        return config_dict
    except Exception as e:
        logging.error(f"Error reading the config file {file_path}: {str(e)}")
        return {}

def get_current_timestamp():
    """Returns the current timestamp in the format YYYYMMDD_HHMMSS."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M.%S")

def get_current_date():
    """Returns the current date in the format %m-%d-%Y."""
    return datetime.date.today().strftime("%m-%d-%Y")

def setup_logging(log_filename, level=logging.INFO):
    """Sets up the logging configuration.

    :param log_filename: Name of the log file to write logs.
    :param level: Logging level (default is INFO).
    """
    logging.basicConfig(level=level, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=log_filename,
                        filemode='w')

# If needed, you can add other utility functions or classes here.

