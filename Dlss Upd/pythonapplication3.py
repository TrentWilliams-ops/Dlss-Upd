import os
import shutil
import tkinter as tk
from tkinter import filedialog
import json

# Define the path for the extracted file
EXTRACTED_FILE = "extracted_files/nvngx_dlss.dll"  # Adjust as needed

# Define a path to save the previous directory
PATHS_FILE = "previous_paths.json"

# Load previous paths from a JSON file
def load_previous_paths():
    if os.path.exists(PATHS_FILE):
        with open(PATHS_FILE, "r") as f:
            return json.load(f)
    return []

# Save the paths to the JSON file
def save_previous_paths(paths):
    with open(PATHS_FILE, "w") as f:
        json.dump(paths, f)

# Function to select multiple directories
def select_multiple_directories():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directories = filedialog.askdirectory(title="Select Folders")  # Open dialog for single selection
    return directories if directories else None

# Function to search and replace the DLL file
def search_and_replace_in_directory(root, extracted_file):
    for dirpath, dirnames, filenames in os.walk(root):
        if "nvngx_dlss.dll" in filenames:
            target_path = os.path.join(dirpath, "nvngx_dlss.dll")
            print(f"Replacing file in: {target_path}")
            shutil.copy2(extracted_file, target_path)
            return True
    return False

# Function to replace the DLL file in all saved paths
def replace_in_saved_paths(extracted_file, previous_paths):
    for path in previous_paths:
        if search_and_replace_in_directory(path, extracted_file):
            print(f"Replacement successful in: {path}")
        else:
            print(f"No target file found in: {path}")

# Main entry point
if __name__ == "__main__":
    previous_paths = load_previous_paths()

    while True:
        print("\nOptions:")
        print("1: Delete previous paths")
        print("2: Select directories")
        print("3: Replace file in saved paths")
        print("4: Exit")
        option = input("Choose an option (1-4): ").strip()

        if option == '1':
            if previous_paths:
                print("\nPrevious paths:")
                for i, path in enumerate(previous_paths):
                    print(f"{i + 1}: {path}")

                # Allow deleting multiple paths
                to_delete = input("Select paths to delete (comma-separated numbers, e.g., 1,2): ")
                indices = to_delete.split(',')
                indices = [int(i.strip()) - 1 for i in indices if i.strip().isdigit() and 0 <= int(i.strip()) - 1 < len(previous_paths)]

                for index in sorted(indices, reverse=True):  # Delete in reverse to avoid index shift
                    deleted_path = previous_paths.pop(index)
                    print(f"Deleted: {deleted_path}")

                save_previous_paths(previous_paths)
            else:
                print("No previous paths to delete.")

        elif option == '2':
            print("Select multiple directories. Click 'Cancel' after picking all your directories.")
            selected_paths = []
            while True:
                selected_path = select_multiple_directories()
                if selected_path:
                    if selected_path not in previous_paths:
                        previous_paths.append(selected_path)
                        selected_paths.append(selected_path)
                        print(f"Added: {selected_path}")
                    else:
                        print(f"The path '{selected_path}' is already in the list.")
                else:
                    break  # Exit the loop if the user cancels the dialog

            # After selection, check for target files
            for path in selected_paths:
                if not search_and_replace_in_directory(path, EXTRACTED_FILE):
                    print(f"No target file found in: {path}")

            save_previous_paths(previous_paths)  # Save updated paths

        elif option == '3':
            if previous_paths:
                replace_in_saved_paths(EXTRACTED_FILE, previous_paths)
            else:
                print("No previous paths available to replace files.")

        elif option == '4':
            print("Exiting the program.")
            break  # Exit the loop, which ends the program

        else:
            print("Invalid option. Please choose 1-4.")
