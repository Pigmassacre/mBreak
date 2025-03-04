import os
import re
import sys

def process_file(file_path):
    """Process a single file to remove GAME_SCALE references"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Check if the file contains GAME_SCALE
    if 'GAME_SCALE' not in content:
        return False
    
    # Remove import of GAME_SCALE if it's the only thing imported
    content = re.sub(r'from settings\.settings import GAME_SCALE\n', '', content)
    
    # Replace various patterns of GAME_SCALE usage
    # Pattern 1: something -> something
    content = re.sub(r'(\d+(?:\.\d+)?) \* settings\.GAME_SCALE', r'\1', content)
    
    # Pattern 2: image.get_width() -> image.get_width()
    content = re.sub(r'([\w\.]+\.get_width\(\)) \* settings\.GAME_SCALE', r'\1', content)
    content = re.sub(r'([\w\.]+\.get_height\(\)) \* settings\.GAME_SCALE', r'\1', content)
    
    # Pattern 3: comments about GAME_SCALE
    content = re.sub(r'# Scale image to settings\.GAME_SCALE\.', '# Scale image.', content)
    
    # Pattern 4: other multiplications with GAME_SCALE
    content = re.sub(r'([\w\.]+) \* settings\.GAME_SCALE', r'\1', content)
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def walk_directory(directory):
    """Walk through all Python files in the directory and process them"""
    modified_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    modified_files.append(file_path)
    
    return modified_files

if __name__ == "__main__":
    directory = "."  # Current directory
    modified_files = walk_directory(directory)
    
    print(f"Modified {len(modified_files)} files:")
    for file in modified_files:
        print(f"  - {file}") 