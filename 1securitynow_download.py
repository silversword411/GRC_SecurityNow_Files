import os
import requests

# Define the range of file numbers
start_num = 995
end_num = 996

# Define the URL template
url_template = "https://www.grc.com/sn/sn-{:03d}.txt"

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the subfolder 'episodes' where files will be saved
save_dir = os.path.join(script_dir, 'episodes')

# Create the 'episodes' directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

# Function to download a file
def download_file(file_num):
    url = url_template.format(file_num)
    response = requests.get(url)
    if response.status_code == 200:
        file_name = f"sn-{file_num:03d}.txt"
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Downloaded {file_name} to {save_dir}")
    else:
        print(f"Failed to download {url}")

# Download all files in the specified range
for num in range(start_num, end_num + 1):
    download_file(num)
