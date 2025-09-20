import os

def extract_text_files(directory_path: str) -> list[str]:
    text_files = []
    
    # Get all files in directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            text_files.append(file_path)
    
    return text_files