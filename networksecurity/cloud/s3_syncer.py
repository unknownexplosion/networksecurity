import os
import subprocess

class S3Sync:
    def sync_folder_to_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync {folder} {aws_bucket_url}"
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"S3 Sync Error: {result.stderr}")
            raise Exception(f"S3 sync failed: {result.stderr}")
        else:
            print(f"S3 Sync Success: {result.stdout}")

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync {aws_bucket_url} {folder}"
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"S3 Sync Error: {result.stderr}")
            raise Exception(f"S3 sync failed: {result.stderr}")
        else:
            print(f"S3 Sync Success: {result.stdout}")
