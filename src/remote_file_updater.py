import os
import hashlib
import requests
import logging
import time
import threading
from datetime import datetime

class RemoteFileUpdater:
    def __init__(self):
        """        
        Args:
            remote_url: URL to download the Excel file
            file_path: Path where the file should be stored locally
            check_interval: Time in seconds between update checks
        """
        self.remote_url = os.getenv('REMOTE_FILE_URL')
        self.file_path = os.getenv('FILE_PATH')
        self.check_interval = int(os.getenv('CHECK_INTERVAL'))
        self.md5_file_path = f"{self.file_path}.md5"
        self.last_update = None
        self._stop_event = threading.Event()
        self.logger = logging.getLogger('RemoteFileUpdater')

    def _calculate_md5(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _save_md5(self, md5_hash):
        """Save the MD5 hash to a file"""
        with open(self.md5_file_path, 'w') as f:
            f.write(md5_hash)

    def _load_md5(self):
        """Load the MD5 hash from a file"""
        try:
            if os.path.exists(self.md5_file_path):
                with open(self.md5_file_path, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            self.logger.error(f"Error loading MD5: {e}")
        return None

    def download_file(self):
        """Download the file and return True if it's new/different"""
        if not self.remote_url:
            self.logger.error("Remote URL not configured")
            return False
            
        temp_file_path = f"{self.file_path}.tmp"
        
        try:
            # Download the file to a temporary location
            self.logger.info(f"Downloading file from {self.remote_url}")
            response = requests.get(self.remote_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            new_md5 = self._calculate_md5(temp_file_path)
            old_md5 = self._load_md5()
            
            if new_md5 != old_md5:
                self.logger.info("New file detected")
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                os.rename(temp_file_path, self.file_path)
                self._save_md5(new_md5)
                self.last_update = datetime.now()
                return True
            else:
                self.logger.info("File unchanged (same MD5)")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return False

    def stop(self):
        """Stop the update thread"""
        self._stop_event.set()

    def start_periodic_check(self, callback=None):
        """
        Start a background thread to periodically check for file updates.        
        Args:
            callback: Function to call when a new file is downloaded
        """
        self.logger.info(f"Starting update thread, checking every {self.check_interval} seconds")
            
        def check_loop():
            while not self._stop_event.is_set():
                if self.download_file() and callback:
                    callback()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
        return thread
