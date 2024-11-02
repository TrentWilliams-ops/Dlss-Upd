import requests
import zipfile
import os
import sys
from tqdm import tqdm  # For progress bar

# Function to download a file with progress
def download_file(url, download_path):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)

    # Check if download was successful
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            total_size = int(response.headers.get('content-length', 0))
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=download_path) as bar:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    bar.update(len(data))
        print(f"Downloaded ZIP file to {download_path}")
    else:
        print(f"Failed to download ZIP file. Status code: {response.status_code}")
        sys.exit(1)

# Function to extract a ZIP file
def extract_zip(zip_path, extract_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        print(f"Extracted contents to {extract_folder}")
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid ZIP file.")
        sys.exit(1)

# Main function
def main(download_url, download_path, extract_folder):
    try:
        # Download the ZIP file
        download_file(download_url, download_path)

        # Ensure the extraction folder exists
        os.makedirs(extract_folder, exist_ok=True)

        # Extract the ZIP file
        extract_zip(download_path, extract_folder)

        # Clean up downloaded ZIP file after extraction
        if os.path.exists(download_path):
            os.remove(download_path)
            print(f"Removed {download_path} after extraction.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    # Exit message for successful run
    print("Process completed successfully.")
    sys.exit(0)

# Execute the main function with hardcoded parameters or from command line arguments
if __name__ == "__main__":
    download_url = 'https://www.techspot.com/downloads/downloadnowfile/7544/?evp=674240c7e60c1cc6f5cace58684d6694&file=11409'
    download_path = 'nvngx_dlss.zip'
    extract_folder = 'extracted_files'
    main(download_url, download_path, extract_folder)
