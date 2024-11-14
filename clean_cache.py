import os
import subprocess

def is_clean(directory):
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs or any(file.endswith('.pyc') for file in files):
            return False
    return True

if is_clean('.'):
    print("The directory is already clean.")
else:
    subprocess.run(['pyclean', '.'])
    print("Cleaned up the directory.")