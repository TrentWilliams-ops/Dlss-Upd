import os
import shutil
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import string

# Define paths for saved search results
FOUND_PATHS_FILE = "found_paths.json"
FAILED_PATHS_FILE = "failed_paths.json"
EMPTY_PATHS_FILE = "empty_paths.json"  # File to store paths that have been checked and found empty

# Define paths for source directory (current directory where this script is located)
EXTRACTED_FILE = os.path.join(os.path.dirname(__file__), "extracted_files", "nvngx_dlss.dll")

# Load saved paths if they exist
def load_paths(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return set(json.load(file))
    return set()

found_paths = load_paths(FOUND_PATHS_FILE)
failed_paths = load_paths(FAILED_PATHS_FILE)
empty_paths = load_paths(EMPTY_PATHS_FILE)  # Load previously checked empty paths

# Function to save paths for future use
def save_paths(file_path, paths):
    with open(file_path, "w") as file:
        json.dump(list(paths), file)

# Function to find all drives in the system
def get_all_drives():
    drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
    return drives

# Check if a directory should be skipped
def should_skip_directory(directory):
    skip_dirs = {"C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users", "C:\\$RECYCLE.BIN"}
    return any(directory.startswith(skip) for skip in skip_dirs)

# Search and replace on a single directory
def search_and_replace_in_directory(root, extracted_file):
    if should_skip_directory(root):
        return None  # Skip this directory

    try:
        # Skip previously checked empty paths
        if root in empty_paths:
            return None

        # Print out the directory being checked
        print(f"Checking directory: {root}")

        if root in failed_paths:
            return None  # Skip previously failed path

        # Use os.scandir for better performance
        with os.scandir(root) as entries:
            found_file = False  # Flag to indicate if the target file was found
            for entry in entries:
                if entry.name == "nvngx_dlss.dll" and entry.is_file():
                    target_path = entry.path
                    if target_path not in found_paths:  # Avoid previously found paths
                        shutil.copy2(extracted_file, target_path)
                        print("Replacing file in directory...")  # General message
                        found_file = True  # Mark as found
                        return target_path  # Indicate success

            # If the loop completes without finding the file, mark as empty
            if not found_file:
                print("No target file found in the directory.")
                empty_paths.add(root)  # Add to empty paths set
                return None  # No file found here

    except Exception as e:
        print(f"Failed to replace in {root}. Error: {e}")
        return "fail"  # Indicate failure

# Find and replace files across all drives in parallel
def find_and_replace_files(extracted_file, found_paths, failed_paths, empty_paths):
    # Ensure the extracted file exists
    if not os.path.isfile(extracted_file):
        print(f"Error: {extracted_file} not found.")
        return

    # Prepare lists for current run
    current_found = []
    current_failed = []

    # Get all drives and iterate over them
    drives = get_all_drives()
    print(f"Found drives: {drives}")

    with ThreadPoolExecutor() as executor:
        futures = []
        for drive in drives:
            print(f"Starting search on drive: {drive}")  # Debugging output
            for root, dirs, _ in os.walk(drive):
                # Limit search depth (set to 3 levels deep)
                if root.count(os.sep) > 3:
                    continue
                if should_skip_directory(root):
                    continue  # Skip known system directories
                futures.append(executor.submit(search_and_replace_in_directory, root, extracted_file))

        # Process results as they complete
        for future in tqdm(as_completed(futures), total=len(futures), desc="Searching..."):
            result = future.result()
            if result == "fail":
                current_failed.append(root)
            elif result:
                current_found.append(result)

    # Update found/failed paths and save for future runs
    found_paths.update(current_found)
    failed_paths.update(current_failed)
    save_paths(FOUND_PATHS_FILE, found_paths)
    save_paths(FAILED_PATHS_FILE, failed_paths)
    save_paths(EMPTY_PATHS_FILE, empty_paths)  # Save empty paths

    print(f"\nTotal Files Replaced: {len(current_found)}")
    print(f"Total Paths Failed: {len(current_failed)}")

# Main entry point
if __name__ == "__main__":
    try:
        # Run the main function
        find_and_replace_files(EXTRACTED_FILE, found_paths, failed_paths, empty_paths)
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Wait for user input before exiting
    input("Press Enter to exit...")
