import cv2
import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import numpy as np
import pymiere

def analyze_and_edit():
    # 1. Select Folder
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Video Folder")
    if not folder_selected:
        return

    source_path = Path(folder_selected)
    
    # AI Detectors
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    all_clips = []
    portrait_clips = []
    blurry_clips = []
    action_clips = []
    
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv')
    
    print(f"Step 1: Analyzing clips in {source_path}...")

    raw_paths = []
    for root_dir, _, files in os.walk(source_path):
        for file in files:
            if file.lower().endswith(video_extensions):
                raw_paths.append(os.path.join(root_dir, file))
    
    raw_paths.sort() 

    for i, full_path in enumerate(raw_paths):
        filename = os.path.basename(full_path)
        print(f"[{i+1}/{len(raw_paths)}] Processing: {filename}", end="\r")
        
        all_clips.append(full_path)
        
        cap = cv2.VideoCapture(full_path)
        if cap.isOpened():
            frame_count = 0
            has_face = False
            blur_scores = []
            motion_scores = []
            prev_gray = None
            
            while frame_count < 60:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 10 == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    if not has_face:
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        if len(faces) > 0:
                            has_face = True
                    
                    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                    blur_scores.append(blur_score)
                    
                    if prev_gray is not None:
                        diff = cv2.absdiff(gray, prev_gray)
                        motion_score = np.mean(diff)
                        motion_scores.append(motion_score)
                    prev_gray = gray
                
                frame_count += 1
            
            cap.release()
            
            if has_face:
                portrait_clips.append(full_path)
            if len(blur_scores) > 0 and np.mean(blur_scores) < 100:
                blurry_clips.append(full_path)
            if len(motion_scores) > 0 and np.mean(motion_scores) > 10:
                action_clips.append(full_path)

    print(f"\nAnalysis Complete.")
    print(f"- Total: {len(all_clips)} | Portraits: {len(portrait_clips)} | Action: {len(action_clips)}")
    
    print("\nStep 2: Sending to Premiere Pro...")

    all_clips_str = '["' + '","'.join([p.replace('\\', '/') for p in all_clips]) + '"]'
    portrait_clips_str = '["' + '","'.join([p.replace('\\', '/') for p in portrait_clips]) + '"]'
    blurry_clips_str = '["' + '","'.join([p.replace('\\', '/') for p in blurry_clips]) + '"]'
    action_clips_str = '["' + '","'.join([p.replace('\\', '/') for p in action_clips]) + '"]'

    jsx_logic = f"""
    (function() {{
        app.enableQE();
        var proj = app.project;
        
        function importToBin(paths, binName) {{
            if (paths.length === 0) return [];
            var bin = proj.rootItem.createBin(binName);
            proj.importFiles(paths, true, bin, false);
            var items = [];
            for (var i = 0; i < bin.children.numItems; i++) {{
                if (bin.children[i].type === 1) items.push(bin.children[i]);
            }}
            items.sort(function(a, b) {{ return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1; }});
            return items;
        }}

        var timelineItems = importToBin({all_clips_str}, "01_Main_Timeline");
        importToBin({portrait_clips_str}, "02_Portraits_Detected");
        importToBin({action_clips_str}, "03_Action_Clips");
        importToBin({blurry_clips_str}, "04_Blurry_Clips_Check");

        var clipsToPlace = [];
        var trimSec = 15 / 30;
        for (var j = 0; j < timelineItems.length; j++) {{
            var item = timelineItems[j];
            var dur = item.getOutPoint().seconds - item.getInPoint().seconds;
            if (dur > 2) {{
                var start = item.getInPoint().seconds;
                var end = item.getOutPoint().seconds;
                item.setInPoint(start + trimSec, 4);
                item.setOutPoint(end - trimSec, 4);
                clipsToPlace.push(item);
            }}
        }}

        var seqName = "AI_AutoEdit_" + new Date().getTime();
        proj.createNewSequence(seqName, "");
        var activeSeq = proj.activeSequence;
        var vTrack = activeSeq.videoTracks[0];

        var time = 0;
        for (var k = 0; k < clipsToPlace.length; k++) {{
            var clip = clipsToPlace[k];
            clip.setAudioGain(-3.0, 1); 
            vTrack.overwriteClip(clip, time);
            time += (clip.getOutPoint().seconds - clip.getInPoint().seconds);
        }}

        var qeTrack = qe.project.getActiveSequence().getVideoTrackAt(0);
        var tList = qe.project.getVideoTransitionList();
        var safe = [];
        for (var t = 0; t < tList.length; t++) {{
            if (tList[t].indexOf("VR") === -1 && tList[t].indexOf("Morph") === -1) safe.push(tList[t]);
        }}

        for (var c = 0; c < qeTrack.numItems - 1; c++) {{
            var randT = safe[Math.floor(Math.random() * safe.length)];
            var tObj = qe.project.getVideoTransitionByName(randT);
            if (tObj) qeTrack.getItemAt(c).addTransition(tObj, false, "00:00:00:15");
        }}

        return "Processed " + clipsToPlace.length + " clips.";
    }})();
    """

    try:
        # Use pymiere.gui.eval_script which is the correct way to send raw JSX
        # This requires the Pymiere Link panel to be OPEN in Premiere
        from pymiere import wrapper
        result = wrapper.eval_script(jsx_logic)
        print(f"Premiere says: {result}")
    except Exception as e:
        print(f"Communication Error: {e}")
        print("\nTIP: Make sure the 'Pymiere Link' panel is open in Premiere Pro!")
        print("(Window > Extensions > Pymiere Link)")

if __name__ == "__main__":
    analyze_and_edit()
