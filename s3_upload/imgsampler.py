import os
import pandas as pd
import random
import logging
import threading

class ImageSampler:
    def __init__(self, s3_client, bucket_name, uploader, sampled_file="sampled_images.csv", all_files="all_images.csv"):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.sampled_file = sampled_file
        self.all_files = all_files
        self.sampled_images = self._load_sampled_images()
        self.total_images_run = 0
        self.uploader = uploader

    def _load_sampled_images(self):
        """Load previously sampled images from a csv file."""
        if os.path.exists(self.sampled_file):
            df = pd.read_csv(self.sampled_file)
            return df['image_name'].tolist()
        return []

    def _update_sampled_images(self, new_samples):
        """Append new sampled images to the csv file."""
        df = pd.DataFrame({'image_name': new_samples})
        if os.path.exists(self.sampled_file):
            df.to_csv(self.sampled_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.sampled_file, index=False)

        self.sampled_images.extend(new_samples)

    def get_all_images(self, fetch_from_s3=True):
        """Retrieve the list of all images in the S3 bucket or from the local .csv file."""
        if fetch_from_s3:
            logging.info("Fetching list of all images directly from the S3 bucket.")
            all_files = self.s3_client.list_objects(self.bucket_name)

            df = pd.DataFrame({'image_name': all_files})
            df.to_csv(self.all_files, index=False)
            
            logging.info(f"Saved a list of {len(all_files)} images to '{self.all_files}'.")
            
            return all_files
        
        else:
            if os.path.exists(self.all_files):
                df = pd.read_csv(self.all_files)
                return df['image_name'].tolist()
            else:
                logging.warning("No local image list found. Consider fetching from S3 by using --fetch-from-s3 flag.")
                exit(1)

    def _upload_callback(self, image_name):
        self._update_sampled_images([image_name])
        self.total_images_run += 1

    def sample_images(self, n, m, fetch_from_s3=True):
        """Sample images in batches."""
        all_images = self.get_all_images(fetch_from_s3)
        unsampled_images = [img for img in all_images if img not in self.sampled_images]

        # Loop through batches of images
        while self.total_images_run < m:
            # Get batch size
            batch_size = min(n, m - self.total_images_run)
            if len(unsampled_images) < batch_size:
                logging.warning("Not enough unsampled images for a full batch. Processing available images.")
                batch_size = len(unsampled_images)
                if batch_size == 0:
                    break

            # Sample images randomly
            sampled = random.sample(unsampled_images, batch_size)

            # Threading
            threads = []
            for image_name in sampled:
                thread = threading.Thread(target=self.uploader.upload_worker, args=(image_name, self._upload_callback))
                thread.start()
                threads.append(thread)

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

            # Update unsampled images
            unsampled_images = [img for img in all_images if img not in self.sampled_images]

            logging.info(f"Sampled and uploaded {self.total_images_run} out of {m} images")

        logging.info(f"Sampled total of {len(self.sampled_images)} / {len(all_images)} images")

# Any additional functions or logic related to ImageSampler can be added here.
