import os
import re

# Define constants
MAX_WORDS = 490000
EPISODES_FOLDER = 'episodes'
SUMMARIZED_FOLDER = 'summarized'

# Create the summarized folder if it doesn't exist
if not os.path.exists(SUMMARIZED_FOLDER):
    os.makedirs(SUMMARIZED_FOLDER)

def count_words(text):
    """Counts the words in a string."""
    return len(re.findall(r'\b\w+\b', text))

def natural_sort_key(filename):
    """
    Returns a list of strings and integers that 
    can be used as a sort key for natural sorting.
    """
    # Extract numeric portions and convert them to int
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', filename)]

def merge_files(files, output_filename):
    """Merge multiple text files into one, given a list of file paths."""
    total_words = 0
    merged_content = ""
    file_list = []
    counter = 1  # Counter to name files part1, part2, etc.

    # Sort files naturally to handle 1000+ episodes correctly
    files = sorted(files, key=lambda f: natural_sort_key(os.path.basename(f)))

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            words_in_file = count_words(content)
            if total_words + words_in_file > MAX_WORDS:
                # Save the current merged file before exceeding the word limit
                save_merged_file(merged_content, file_list, output_filename, counter)
                # Reset for the next batch
                total_words = 0
                merged_content = ""
                file_list = []
                counter += 1  # Increment counter for next part

            merged_content += content + "\n"
            total_words += words_in_file
            file_list.append(file)

    # Save any remaining content
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
    # Specify the folder where your episode files are located
    input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), EPISODES_FOLDER)

    # Get all text files in the episodes directory
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.txt')]

    if not files:
        print("No text files found in the episodes folder.")
        return

    # Merge the files into summary parts without exceeding MAX_WORDS
    merge_files(files, 'summary')

if __name__ == "__main__":
    main()
