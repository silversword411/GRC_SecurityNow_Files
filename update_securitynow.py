#!/usr/bin/env python3
"""
Security Now! Full Update Pipeline

This script automates the entire update process:
1. Detects the latest local episode
2. Checks for new episodes on grc.com
3. Downloads new episodes
4. Fixes file timestamps
5. Regenerates summary files
6. Creates updated zip file
7. Updates README.md
8. Prepares git commit

Usage:
    python update_securitynow.py           # Interactive mode
    python update_securitynow.py --check   # Just check for new episodes
    python update_securitynow.py --auto    # Auto-download without prompting
"""

import os
import re
import sys
import shutil
import zipfile
import argparse
from datetime import datetime

import requests

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EPISODES_DIR = os.path.join(SCRIPT_DIR, 'episodes')
SUMMARIZED_DIR = os.path.join(SCRIPT_DIR, 'summarized')
ZIPS_DIR = os.path.join(SCRIPT_DIR, 'zips')
README_PATH = os.path.join(SCRIPT_DIR, 'README.md')
URL_TEMPLATE = "https://www.grc.com/sn/sn-{:03d}.txt"
MAX_WORDS = 490000
ZIP_GROUP_SIZE = 500  # Episodes per zip file in zips/ folder


def get_latest_local_episode():
    """Find the highest episode number in the episodes folder."""
    if not os.path.exists(EPISODES_DIR):
        return 0

    pattern = re.compile(r'sn-(\d+)\.txt')
    max_ep = 0

    for filename in os.listdir(EPISODES_DIR):
        match = pattern.match(filename)
        if match:
            ep_num = int(match.group(1))
            max_ep = max(max_ep, ep_num)

    return max_ep


def check_episode_exists(episode_num):
    """Check if an episode exists on grc.com."""
    url = URL_TEMPLATE.format(episode_num)
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


def find_latest_remote_episode(start_from):
    """Find the latest available episode on grc.com."""
    print(f"Checking for new episodes starting from {start_from + 1}...")

    latest = start_from
    check_num = start_from + 1
    consecutive_misses = 0

    while consecutive_misses < 3:
        if check_episode_exists(check_num):
            print(f"  Found episode {check_num}")
            latest = check_num
            consecutive_misses = 0
        else:
            consecutive_misses += 1
        check_num += 1

    return latest


def download_episode(episode_num):
    """Download a single episode transcript."""
    url = URL_TEMPLATE.format(episode_num)

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Use 4-digit format for episodes >= 1000
            if episode_num >= 1000:
                filename = f"sn-{episode_num}.txt"
            else:
                filename = f"sn-{episode_num:03d}.txt"

            filepath = os.path.join(EPISODES_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"  Downloaded: {filename}")
            return True
        else:
            print(f"  Failed to download episode {episode_num}: HTTP {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"  Error downloading episode {episode_num}: {e}")
        return False


def extract_date(file_content):
    """Extract the DATE field from episode content."""
    date_pattern = re.compile(r"DATE:\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})")
    match = date_pattern.search(file_content)
    if match:
        return match.group(1)
    return None


def fix_file_timestamp(filepath):
    """Update file timestamp to match episode date."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        date_str = extract_date(content)
        if date_str:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            timestamp = date_obj.timestamp()
            os.utime(filepath, (timestamp, timestamp))
            return date_str
    except Exception as e:
        print(f"  Error fixing timestamp for {filepath}: {e}")
    return None


def fix_all_timestamps():
    """Fix timestamps for all episode files."""
    print("\nFixing file timestamps...")

    for filename in sorted(os.listdir(EPISODES_DIR)):
        if filename.endswith('.txt'):
            filepath = os.path.join(EPISODES_DIR, filename)
            date_str = fix_file_timestamp(filepath)
            if date_str:
                print(f"  {filename} -> {date_str}")


def count_words(text):
    """Count words in text."""
    return len(re.findall(r'\b\w+\b', text))


def natural_sort_key(filename):
    """Natural sort key for filenames with numbers."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', filename)]


def generate_summaries():
    """Generate summary files from episodes."""
    print("\nGenerating summary files...")

    # Clear existing summary files (but not the zip)
    for filename in os.listdir(SUMMARIZED_DIR):
        if filename.startswith('summary_') and filename.endswith('.txt'):
            os.remove(os.path.join(SUMMARIZED_DIR, filename))

    # Get all episode files
    files = [os.path.join(EPISODES_DIR, f)
             for f in os.listdir(EPISODES_DIR)
             if f.endswith('.txt')]

    if not files:
        print("  No episode files found!")
        return 0

    # Sort naturally
    files = sorted(files, key=lambda f: natural_sort_key(os.path.basename(f)))

    # Merge files
    total_words = 0
    merged_content = ""
    file_list = []
    part_num = 1

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        words_in_file = count_words(content)

        if total_words + words_in_file > MAX_WORDS and merged_content:
            # Save current batch
            save_summary(merged_content, file_list, part_num)
            total_words = 0
            merged_content = ""
            file_list = []
            part_num += 1

        merged_content += content + "\n"
        total_words += words_in_file
        file_list.append(filepath)

    # Save remaining content
    if merged_content:
        save_summary(merged_content, file_list, part_num)

    print(f"  Created {part_num} summary files")
    return part_num


def save_summary(content, file_list, part_num):
    """Save a summary file."""
    first_file = os.path.basename(file_list[0]).replace('.txt', '')
    last_file = os.path.basename(file_list[-1]).replace('.txt', '')

    filename = f"summary_{first_file}_to_{last_file}_part{part_num}.txt"
    filepath = os.path.join(SUMMARIZED_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Saved: {filename}")


def create_zip(latest_episode):
    """Create zip file of all summary files."""
    print("\nCreating zip file...")

    zip_name = f"summarized001-{latest_episode}.zip"
    zip_path = os.path.join(SUMMARIZED_DIR, zip_name)

    # Remove old zip files
    for filename in os.listdir(SUMMARIZED_DIR):
        if filename.startswith('summarized') and filename.endswith('.zip'):
            old_path = os.path.join(SUMMARIZED_DIR, filename)
            if old_path != zip_path:
                os.remove(old_path)
                print(f"  Removed old zip: {filename}")

    # Create new zip
    summary_files = [f for f in os.listdir(SUMMARIZED_DIR)
                     if f.startswith('summary_') and f.endswith('.txt')]

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in sorted(summary_files, key=natural_sort_key):
            filepath = os.path.join(SUMMARIZED_DIR, filename)
            zf.write(filepath, filename)

    print(f"  Created: {zip_name}")
    return zip_name


def update_readme(latest_episode, zip_name):
    """Update README.md with new zip file link."""
    print("\nUpdating README.md...")

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update the zip file link
    old_pattern = r'\[summarized\d+-\d+\.zip\]\(/summarized/summarized\d+-\d+\.zip\)'
    new_link = f'[{zip_name}](/summarized/{zip_name})'

    new_content = re.sub(old_pattern, new_link, content)

    if new_content != content:
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Updated link to: {zip_name}")
    else:
        print("  No changes needed")


def get_zip_groups(latest_episode):
    """Calculate which zip groups are needed based on latest episode.

    Groups episodes into chunks of ZIP_GROUP_SIZE (500):
    - SN001-500.zip (episodes 1-500)
    - SN501-1000.zip (episodes 501-1000)
    - SN1001-1500.zip (episodes 1001-1500, grows until 1500)
    """
    groups = []
    start = 1
    while start <= latest_episode:
        end = min(start + ZIP_GROUP_SIZE - 1, latest_episode)
        # For incomplete groups, end is the latest episode
        # For complete groups, end is the group boundary
        if start + ZIP_GROUP_SIZE - 1 <= latest_episode:
            end = start + ZIP_GROUP_SIZE - 1
        else:
            end = latest_episode
        groups.append((start, end))
        start += ZIP_GROUP_SIZE
    return groups


def update_raw_episodes_zips(latest_episode):
    """Update raw episodes zips in the zips folder using 500-episode groups."""
    print("\nUpdating raw episodes zips...")

    groups = get_zip_groups(latest_episode)
    created_zips = []

    # Track which zip prefixes we expect (to clean up old versions)
    expected_prefixes = set()
    for start, end in groups:
        expected_prefixes.add(f"SN{start:03d}-" if start < 1000 else f"SN{start}-")

    for start, end in groups:
        # Format: SN001-500.zip, SN501-1000.zip, SN1001-1500.zip
        if start < 1000:
            zip_name = f"SN{start:03d}-{end}.zip"
            prefix = f"SN{start:03d}-"
        else:
            zip_name = f"SN{start}-{end}.zip"
            prefix = f"SN{start}-"

        zip_path = os.path.join(ZIPS_DIR, zip_name)

        # Remove old versions of this group's zip
        for filename in os.listdir(ZIPS_DIR):
            if filename.startswith(prefix) and filename.endswith('.zip'):
                old_path = os.path.join(ZIPS_DIR, filename)
                if old_path != zip_path:
                    os.remove(old_path)
                    print(f"  Removed old zip: {filename}")

        # Skip if zip already exists and group is complete (won't change)
        group_is_complete = (end == start + ZIP_GROUP_SIZE - 1)
        if os.path.exists(zip_path) and group_is_complete:
            print(f"  Skipped (unchanged): {zip_name}")
            created_zips.append(zip_name)
            continue

        # Collect episode files for this group
        files_to_zip = []
        for ep_num in range(start, end + 1):
            if ep_num >= 1000:
                filename = f"sn-{ep_num}.txt"
            else:
                filename = f"sn-{ep_num:03d}.txt"

            filepath = os.path.join(EPISODES_DIR, filename)
            if os.path.exists(filepath):
                files_to_zip.append((filepath, filename))

        # Create zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filepath, filename in files_to_zip:
                zf.write(filepath, filename)

        print(f"  Created: {zip_name} ({len(files_to_zip)} episodes)")
        created_zips.append(zip_name)

    # Clean up any old zips that don't match current grouping
    # (e.g., SN1-899.zip or SN900-1021.zip from old scheme)
    for filename in os.listdir(ZIPS_DIR):
        if filename.startswith('SN') and filename.endswith('.zip'):
            # Check if this matches any expected prefix
            matches_expected = False
            for prefix in expected_prefixes:
                if filename.startswith(prefix):
                    matches_expected = True
                    break
            if not matches_expected:
                old_path = os.path.join(ZIPS_DIR, filename)
                os.remove(old_path)
                print(f"  Removed legacy zip: {filename}")

    return created_zips


def print_git_commands(latest_episode):
    """Print git commands for the user to run."""
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE!")
    print("=" * 60)
    print("\nTo commit these changes, run:")
    print()
    print(f'  git add -A')
    print(f'  git commit -m "Updating to episode {latest_episode}"')
    print(f'  git push')
    print()


def main():
    parser = argparse.ArgumentParser(description='Security Now! Update Pipeline')
    parser.add_argument('--check', action='store_true',
                        help='Just check for new episodes without downloading')
    parser.add_argument('--auto', action='store_true',
                        help='Auto-download without prompting')
    args = parser.parse_args()

    print("=" * 60)
    print("Security Now! Update Pipeline")
    print("=" * 60)

    # Ensure directories exist
    os.makedirs(EPISODES_DIR, exist_ok=True)
    os.makedirs(SUMMARIZED_DIR, exist_ok=True)
    os.makedirs(ZIPS_DIR, exist_ok=True)

    # Find latest local episode
    local_latest = get_latest_local_episode()
    print(f"\nLatest local episode: {local_latest}")

    # Check for new episodes
    remote_latest = find_latest_remote_episode(local_latest)

    if remote_latest <= local_latest:
        print("\nNo new episodes available.")
        return 0

    new_count = remote_latest - local_latest
    print(f"\nFound {new_count} new episode(s): {local_latest + 1} to {remote_latest}")

    if args.check:
        return 0

    # Confirm download
    if not args.auto:
        response = input("\nDownload new episodes? [Y/n]: ").strip().lower()
        if response and response != 'y':
            print("Aborted.")
            return 0

    # Download new episodes
    print("\nDownloading new episodes...")
    downloaded = 0
    for ep_num in range(local_latest + 1, remote_latest + 1):
        if download_episode(ep_num):
            downloaded += 1

    if downloaded == 0:
        print("No episodes were downloaded.")
        return 1

    print(f"\nDownloaded {downloaded} episode(s)")

    # Fix timestamps for new files only
    print("\nFixing timestamps for new episodes...")
    for ep_num in range(local_latest + 1, remote_latest + 1):
        if ep_num >= 1000:
            filename = f"sn-{ep_num}.txt"
        else:
            filename = f"sn-{ep_num:03d}.txt"

        filepath = os.path.join(EPISODES_DIR, filename)
        if os.path.exists(filepath):
            date_str = fix_file_timestamp(filepath)
            if date_str:
                print(f"  {filename} -> {date_str}")

    # Generate summaries
    generate_summaries()

    # Create summarized zip
    zip_name = create_zip(remote_latest)

    # Update raw episodes zips (500-episode groups)
    update_raw_episodes_zips(remote_latest)

    # Update README
    update_readme(remote_latest, zip_name)

    # Print git commands
    print_git_commands(remote_latest)

    return 0


if __name__ == '__main__':
    sys.exit(main())
