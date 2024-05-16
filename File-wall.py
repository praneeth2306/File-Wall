import hashlib
import os
import json
import requests
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to calculate the MD5 hash of a file
def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()

# Function to send notification via ntfy.sh
def send_notification(message):
    url = "https://ntfy.sh/praneeth"  # Replace with your ntfy topic
    headers = {'Title': 'File Integrity Check', 'Priority': 'high'}
    try:
        response = requests.post(url, data=message.encode('utf-8'), headers=headers)
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Function to load stored hashes
def load_hashes(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Function to save hashes
def save_hashes(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to check file integrity
def check_file_integrity(folder_path):
    hash_file_path = os.path.join(folder_path, 'file_hashes.json')
    old_hashes = load_hashes(hash_file_path)
    new_hashes = {}

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename == 'file_hashes.json':
                continue
            file_path = os.path.join(root, filename)
            file_hash = calculate_md5(file_path)
            new_hashes[file_path] = file_hash

            if file_path not in old_hashes:
                send_notification(f"ALERT MR.PRANEETH NEW NUCLEAR CODE CREATED: {file_path}")
            elif old_hashes[file_path] != file_hash:
                send_notification(f"NUCLEAR CODE: {file_path}")

    for file_path in old_hashes:
        if file_path not in new_hashes:
            send_notification(f"ALERT MR.PRANEETH!! SOMEONE STOLE THE CHEAT CODES!!: {file_path}")

    save_hashes(hash_file_path, new_hashes)

class FileIntegrityHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def on_modified(self, event):
        if not event.is_directory:
            check_file_integrity(self.folder_path)

    def on_created(self, event):
        if not event.is_directory:
            check_file_integrity(self.folder_path)

    def on_deleted(self, event):
        if not event.is_directory:
            check_file_integrity(self.folder_path)

def monitor_folder(folder_path):
    event_handler = FileIntegrityHandler(folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    print(f"Monitoring folder: {folder_path}")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_integrity_check.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Folder not found: {folder_path}")
        sys.exit(1)

    # Perform an initial check
    check_file_integrity(folder_path)

    # Start monitoring the folder for changes
    monitor_folder(folder_path)
