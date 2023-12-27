
# Upload Images from AWS S3 to Roboflow

This project facilitates the sampling of images from an AWS S3 bucket and subsequently uploads them to Roboflow via their API.

## Table of Contents
- [Project Files](#project-files)
- [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Files

**1. `main.py`:**
   - **Purpose:** Serves as the entry point for the program. It parses command line arguments, sets up required configurations, and coordinates the image sampling and uploading process.

**2. `uploader.py`:**
   - **Purpose:** Contains the `ImageUploader` class which is responsible for uploading sampled images to Roboflow.

**3. `imgsampler.py`:**
   - **Purpose:** Hosts the `ImageSampler` class which fetches images from the S3 bucket, samples them, and saves metadata about sampled images.

**4. `s3_client.py`:**
   - **Purpose:** Consists of the `S3Client` class which abstracts interactions with the AWS S3 service, enabling listing, fetching, and other S3-related operations.

**5. `csv_handler.py`:**
   - **Purpose:** Contains utility functions for reading and writing to CSV files, ensuring that metadata about images is stored and retrieved effectively.

**6. `utils.py`:**
   - **Purpose:** A utility file that contains helper functions like `read_config` to assist with common tasks throughout the application.

**7. `requirements.txt`:**
   - **Purpose:** Lists all the Python dependencies required for the project, ensuring reproducibility and consistent environment setups.

**8. `config.yaml`:**
   - **Purpose:** Provides configuration settings for the Roboflow API and AWS S3. Contains API keys, project names, and bucket details.

**9. `all_images.csv`:**
   - **Purpose:** (Program creates this file) Pulls a list of available images in S3 and saves them to a csv. This is used to determine which images to pull from the S3 bucked. This can be toggled on / off with the flag `--fetch-from-s3`.

**10. `sampled_images.csv`:**
   - **Purpose:** (Program creates this file) A csv containing a list of images successfully sent to Roboflow. The CSV helps ensure duplicates are not sent to Roboflow when sampling.

## Setup

### Requirements

- Python 3.x
- AWS CLI configured with the necessary permissions to access the S3 bucket.
- An account on Roboflow and API key information.

## AWS Configuration

Before using the script, ensure you've set up AWS CLI with the necessary authentication credentials. This will allow you to access and manage the desired S3 bucket.

### Installing the AWS CLI

If you haven't already installed the AWS CLI, you can do so by following the official installation guide:
- [Installing the AWS CLI version 2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

### Configuring the AWS CLI

1. Once you've installed the AWS CLI, open a terminal or command prompt.
2. Run the following command:

   ```bash
   aws configure
   ```

3. You'll be prompted to enter your AWS credentials:

   ```
   AWS Access Key ID [None]: YOUR_ACCESS_KEY
   AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
   Default region name [None]: YOUR_PREFERRED_REGION (e.g., us-west-1)
   Default output format [None]: json
   ```

   Make sure to replace `YOUR_ACCESS_KEY`, `YOUR_SECRET_ACCESS_KEY`, and `YOUR_PREFERRED_REGION` with your actual AWS details. It's recommended to set the output format to `json` for easier parsing.

**Security Note:** Always keep your AWS credentials confidential to prevent misuse. Avoid uploading or sharing configuration files containing your access and secret keys. If using a public version control system like GitHub, make sure to ignore files that might contain sensitive information.

### Installation

1. Clone this repository:

   ```bash
   git clone [REPOSITORY_LINK]
   cd [REPOSITORY_DIRECTORY]
   ```

2. Create and activate a virtual environment (Optional but recommended):

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy and edit the `config.yaml` file with appropriate values (Roboflow API key, S3 bucket name, etc.)


## Configuration File (`config.yaml`)

To customize the behavior of the script for your specific use case, you will need to provide a `config.yaml` configuration file. This file holds essential parameters like your Roboflow API key, the Roboflow project name, and the S3 bucket name.

Here's a template for the `config.yaml`:

```yaml
roboflow:
  api_key: YOUR_ROBOFLOW_API_KEY
  project_name: YOUR_PROJECT_NAME
  label_null: LABEL_NULL_BOOL
s3:
  bucket_name: YOUR_BUCKET_NAME
```

### Filling in the Configuration:

- `YOUR_ROBOFLOW_API_KEY`: This is the API key provided by Roboflow. For example: `afejfe3453ferge`.
- `YOUR_PROJECT_NAME`: The name of your Roboflow project. For instance, `image-upload`.
- `LABEL_NULL_BOOL`: If you want to upload images as null images, set this to `True`. Otherwise, set it to `False` and they will be unlabeled.
- `YOUR_BUCKET_NAME`: The name of the S3 bucket from which the images will be pulled. For instance, `roboflowpulltestimages`.

**Security Note:** The `config.yaml` file contains sensitive information, particularly the Roboflow API key. It's crucial never to commit this file to a public repository or share it in a way that can expose these details. Ensure your `.gitignore` file (or similar for other VCS) includes `config.yaml` to prevent accidental commits.


## Usage

```bash
python main.py M N --fetch-from-s3
```
Where:
- `M` is the total number of images to pull.
- `N` is the batch size of images to pull at once (the program uses threading).
- `--fetch-from-s3` is an optional flag to fetch image names directly from the S3 bucket. If not provided, the program will try to read from a local `.csv` file. Include this flag the first time you run the program!

**Example:** 
```bash
python main.py 100 10 --fetch-from-s3
```
