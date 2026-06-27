import zipfile
import os
import shutil

# Extract the logo from their original template
with zipfile.ZipFile('template_repo.zip', 'r') as z:
    for filename in z.namelist():
        if filename.startswith('word/media/image'):
            print(f"Found image: {filename}")
            # Extract it
            source = z.open(filename)
            target = open('logo.png', 'wb')
            with source, target:
                shutil.copyfileobj(source, target)
            print("Extracted logo.png successfully.")
            break
