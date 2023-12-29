import os
import pandas as pd
import logging

class CSVHandler:
    def __init__(self, filename):
        self.filename = filename
        self.file_exists = os.path.exists(self.filename)

    def read_csv(self, column_name):
        """Read a specific column from the CSV.

        :param column_name: Name of the column to read.
        :return: List of data from the column.
        """
        if not self.file_exists:
            logging.error(f"File {self.filename} not found.")
            return []

        df = pd.read_csv(self.filename)
        if column_name not in df.columns:
            logging.error(f"Column {column_name} not found in {self.filename}.")
            return []

        return df[column_name].tolist()

    def append_to_csv(self, data_dict):
        """Append data to the CSV. Creates the CSV if it doesn't exist.

        :param data_dict: Dictionary of data to append. Keys are column names.
        """
        df_new = pd.DataFrame(data_dict)
        
        if self.file_exists:
            df_existing = pd.read_csv(self.filename)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(self.filename, index=False)
        self.file_exists = True  # Update file existence flag after writing

    def check_and_create(self):
        """Check if CSV exists, and if not, create an empty one."""
        if not self.file_exists:
            with open(self.filename, 'w') as file:
                file.write('')  # Create an empty CSV file
            self.file_exists = True

# Usage examples (comment out or remove in production):
# handler = CSVHandler('sample.csv')
# handler.append_to_csv({"name": ["John", "Jane"], "age": [28, 25]})
# print(handler.read_csv("name"))
