import os
import re
from datetime import datetime

# Directory containing the downloaded files under the 'episodes' folder
save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'episodes')

# Function to extract the date from the file content
def extract_date(file_content):
    # Define a regex pattern to match the date
    date_pattern = re.compile(r"DATE:\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})")
    match = date_pattern.search(file_content)
    if match:
        return match.group(1)
    return None

# Function to change the file's modification date
def change_file_date(file_path, new_date):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(new_date, "%B %d, %Y")
    # Convert the datetime object to a timestamp
    timestamp = date_obj.timestamp()
    # Update the file's modification and access times
    os.utime(file_path, (timestamp, timestamp))

# Iterate over all files in the directory
for file_name in os.listdir(save_dir):
    file_path = os.path.join(save_dir, file_name)
    if os.path.isfile(file_path) and file_name.endswith(".txt"):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            date_str = extract_date(content)
            if date_str:
                change_file_date(file_path, date_str)
                print(f"Updated date for {file_name} to {date_str}")
            else:
                print(f"Date not found in {file_name}")
