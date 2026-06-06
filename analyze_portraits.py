import cv2
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def analyze_clips():
    # 1. Select Folder
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Video Folder to Analyze")
    if not folder_selected:
        print("No folder selected.")
        return

    source_path = Path(folder_selected)
    output_path = source_path.parent / (source_path.name + "_Analyzed")
    
    portraits_dir = output_path / "Portraits"
    timeline_dir = output_path / "Timeline"
    
    portraits_dir.mkdir(parents=True, exist_ok=True)
    timeline_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load Face Detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    print(f"Analyzing clips in: {source_path}")
    print(f"Output will be in: {output_path}")

    video_extensions = ('.mp4', '.mov', '.avi', '.mkv')
    
    # Recursively find all video files
    video_files = []
    for root_dir, _, files in os.walk(source_path):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_files.append(Path(root_dir) / file)

    # Sort files by path/name to maintain folder order for the timeline
    video_files.sort()

    for i, video_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] Analyzing: {video_file.name}")
        
        is_portrait = False
        cap = cv2.VideoCapture(str(video_file))
        
        if not cap.isOpened():
            print(f"Could not open {video_file.name}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames every 1 second, up to 10 samples
        sample_interval = int(fps) if fps > 0 else 30
        samples = 0
        
        while samples < 10:
            frame_to_read = samples * sample_interval
            if frame_to_read >= total_frames:
                break
                
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_read)
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                is_portrait = True
                break # Found a face, no need to check further
            
            samples += 1
            
        cap.release()

        # 3. Organize Files
        # Create a unique name to avoid collisions if files from different subfolders have same name
        unique_name = f"{i:03d}_{video_file.name}"
        
        # Copy to Timeline folder (maintaining order via prefix)
        shutil.copy2(video_file, timeline_dir / unique_name)
        
        if is_portrait:
            print(f"  -> Portrait detected!")
            shutil.copy2(video_file, portraits_dir / unique_name)

    print("\nAnalysis Complete!")
    print(f"Sorted timeline clips: {timeline_dir}")
    print(f"Detected portraits: {portraits_dir}")
    print("\nNow run the Premiere JSX script and select the '_Analyzed' folder.")

if __name__ == "__main__":
    analyze_clips()
