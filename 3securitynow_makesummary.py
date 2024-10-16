import os
import re

# Define constants
MAX_WORDS = 490000
SUMMARIZED_FOLDER = 'summarized'

# Create the summarized folder if it doesn't exist
if not os.path.exists(SUMMARIZED_FOLDER):
    os.makedirs(SUMMARIZED_FOLDER)

def count_words(text):
    """Counts the words in a string."""
    return len(re.findall(r'\b\w+\b', text))

def merge_files(files, output_filename):
    """Merge multiple text files into one, given a list of file paths."""
    total_words = 0
    merged_content = ""
    file_list = []
    counter = 1  # Counter to name files part1, part2, etc.

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            words_in_file = count_words(content)
            if total_words + words_in_file > MAX_WORDS:
                # Save the current merged file before exceeding the word limit
                save_merged_file(merged_content, file_list, output_filename, counter)
                # Reset for the next file
                total_words = 0
                merged_content = ""
                file_list = []
                counter += 1  # Increment counter for next part

            merged_content += content + "\n"
            total_words += words_in_file
            file_list.append(file)

    # Save any remaining files
    if merged_content:
        save_merged_file(merged_content, file_list, output_filename, counter)

def save_merged_file(content, file_list, output_filename_base, counter):
    """Save the merged content into a new file."""
    first_file = os.path.basename(file_list[0])
    last_file = os.path.basename(file_list[-1])
    # Generate a shorter file name with the first and last file names in the group
    merged_file_name = f"{output_filename_base}_{first_file}_to_{last_file}_part{counter}.txt"
    
    merged_file_path = os.path.join(SUMMARIZED_FOLDER, merged_file_name)
    
    with open(merged_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {merged_file_name}")


def main():
    # Specify the folder where your files are located
    input_folder = os.path.dirname(os.path.abspath(__file__))

    # Get all text files in the directory
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.txt')]

    if not files:
        print("No text files found in the directory.")
        return

    # Call the merge_files function to start merging
    merge_files(files, 'summary')

if __name__ == "__main__":
    main()
