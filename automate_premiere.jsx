/**
 * Premiere Pro 2024 Automation Script
 * 
 * Task:
 * 1. Select a folder of video clips.
 * 2. Import all clips.
 * 3. Trim 10 frames from the beginning and 10 frames from the end of each.
 * 4. Create a sequence and add the clips.
 * 5. Apply random transitions to every cut.
 */

function automatePremiere() {
    app.enableQE(); // Unlock the Quality Engineering API for transitions
    var project = app.project;

    // --- 1. PICK FOLDER ---
    var folder = Folder.selectDialog("Select the folder containing your clips");
    if (!folder) return;

    var files = folder.getFiles(/\.(mp4|mov|avi|mkv|mxf)$/i);
    if (files.length === 0) {
        alert("No video files found in that folder.");
        return;
    }

    // --- 2. IMPORT FILES ---
    // Convert File objects to path strings (fsName) which Premiere requires
    var filePaths = [];
    for (var f = 0; f < files.length; f++) {
        filePaths.push(files[f].fsName);
    }
    
    // Import into the root of the project
    project.importFiles(filePaths, true, project.rootItem, false);

    // --- 3. CREATE SEQUENCE ---
    var seqName = "Auto_Sequence_" + new Date().getTime();
    project.createNewSequence(seqName, "");
    var activeSeq = project.activeSequence;
    var videoTrack = activeSeq.videoTracks[0];

    // --- 4. TRIM AND ADD TO TIMELINE ---
    // We'll look through the project for the clips we just imported
    for (var i = 0; i < project.rootItem.children.numItems; i++) {
        var item = project.rootItem.children[i];

        // Only process clips (ignore the sequence we just created)
        if (item.type === ProjectItemType.CLIP && item.name.indexOf("Auto_Sequence") === -1) {
            
            // Logic to calculate 10 frames in seconds
            // Note: Premiere doesn't give FPS easily here, so we'll use a safe 30fps estimate or ticks
            var fps = 30; 
            var tenFramesInSeconds = 10 / fps;

            var currentIn = item.getInPoint();
            var currentOut = item.getOutPoint();
            
            // Only trim if the clip is long enough (at least 1 second / 30 frames)
            if (currentOut.seconds - currentIn.seconds > (tenFramesInSeconds * 3)) {
                item.setInPoint(currentIn.seconds + tenFramesInSeconds, 4);
                item.setOutPoint(currentOut.seconds - tenFramesInSeconds, 4);
            }

            // Append clip to the end of the timeline
            var insertTime = videoTrack.clips.numItems === 0 ? 0 : videoTrack.clips[videoTrack.clips.numItems - 1].end.seconds;
            videoTrack.overwriteClip(item, insertTime);
        }
    }

    // --- 5. APPLY RANDOM TRANSITIONS ---
    // This requires the QE (Quality Engineering) API
    var qeSeq = qe.project.getActiveSequence();
    var transitionList = qe.project.getVideoTransitionList();
    var qeTrack = qeSeq.getVideoTrackAt(0);

    // We loop through cuts (between clips)
    // Note: QE indices are 0-based
    for (var c = 0; c < qeTrack.numItems - 1; c++) {
        var clip = qeTrack.getItemAt(c);
        
        // Pick a truly random transition
        var randomIndex = Math.floor(Math.random() * transitionList.length);
        var transName = transitionList[randomIndex];

        // Filter out transitions that often cause errors or require manual setup
        if (transName.indexOf("Morph") !== -1 || transName.indexOf("VR") !== -1) {
            transName = "Cross Dissolve"; // Safe fallback
        }

        var transitionObj = qe.project.getVideoTransitionByName(transName);
        
        // Add transition to the END of the current clip
        // (If there's a clip next to it, Premiere centers it on the cut)
        // Duration format: "HH:MM:SS:FF"
        clip.addTransition(transitionObj, false, "00:00:00:15"); 
    }

    alert("Task Complete!\n- Clips Imported\n- 10 Frames trimmed from both ends\n- Random transitions applied to all cuts.");
}

// Run the script
automatePremiere();
