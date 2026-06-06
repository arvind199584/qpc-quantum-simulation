import os
import re
import time
from pathlib import Path

def remove_numbers_from_filenames(root_folder, dry_run=True):
    """
    Recursively removes all numeric characters (0-9) from MP3 filenames.
    :param root_folder: The directory to scan.
    :param dry_run: If True, only prints changes without renaming files.
    """
    root_path = Path(root_folder)
    if not root_path.exists():
        print(f"Error: Folder {root_folder} does not exist.")
        return

    count = 0
    start_time = time.time()
    
    print(f"{'DRY RUN MODE' if dry_run else 'LIVE MODE'}: Scanning {root_folder}...")

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith('.mp3'):
                old_name = file
                
                # Split name and extension
                name_stem = Path(file).stem
                extension = Path(file).suffix
                
                # Remove all digits (0-9)
                new_name_stem = re.sub(r'\d+', '', name_stem)
                
                # Optional: Clean up double spaces or trailing dashes/underscores
                new_name_stem = new_name_stem.replace('  ', ' ').strip(' _-')
                
                new_name = new_name_stem + extension
                
                if old_name != new_name:
                    old_file_path = os.path.join(root, old_name)
                    new_file_path = os.path.join(root, new_name)
                    
                    # Handle collisions (if renaming results in an existing filename)
                    if os.path.exists(new_file_path) and not dry_run:
                        # Append a small timestamp or counter if collision occurs
                        new_name = f"{new_name_stem}_{int(time.time() % 1000)}{extension}"
                        new_file_path = os.path.join(root, new_name)

                    if dry_run:
                        print(f"[PREVIEW] {old_name} -> {new_name}")
                    else:
                        try:
                            os.rename(old_file_path, new_file_path)
                            print(f"[RENAMED] {old_name} -> {new_name}")
                        except Exception as e:
                            print(f"[ERROR] Could not rename {old_name}: {e}")
                    
                    count += 1

    duration = time.time() - start_time
    status = "Previewed" if dry_run else "Renamed"
    print(f"\nTask Complete!")
    print(f"{status} {count} files in {duration:.2f} seconds.")
    if dry_run:
        print("\nSet dry_run=False in the script to apply these changes.")

if __name__ == "__main__":
    # 1. Provide your folder path here
    target_dir = r"F:\songs"
    
    # 2. Run the script (Dry Run is ON by default for safety)
    remove_numbers_from_filenames(target_dir, dry_run=True)
