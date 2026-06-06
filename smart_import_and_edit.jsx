/**
 * Premiere Pro Script: Smart Import & Edit
 * Works with the output of analyze_portraits.py
 */

app.enableQE();

function main() {
    try {
        if (!app.project) {
            alert("Please open a project first.");
            return;
        }

        // 1. SELECT THE ANALYZED FOLDER
        var analyzedFolder = Folder.selectDialog("Select the '_Analyzed' folder created by the Python script");
        if (!analyzedFolder) return;

        var timelineFolder = new Folder(analyzedFolder.fsName + "/Timeline");
        var portraitsFolder = new Folder(analyzedFolder.fsName + "/Portraits");

        if (!timelineFolder.exists) {
            alert("Could not find the 'Timeline' subfolder. Please run the Python script first.");
            return;
        }

        // 2. IMPORT PORTRAITS INTO A BIN
        if (portraitsFolder.exists) {
            var portraitFiles = portraitsFolder.getFiles(/\.(mp4|mov|avi|mkv)$/i);
            if (portraitFiles.length > 0) {
                var portraitBin = app.project.rootItem.createBin("Portraits_Detected");
                var portraitPaths = [];
                for (var p = 0; p < portraitFiles.length; p++) {
                    portraitPaths.push(portraitFiles[p].fsName);
                }
                app.project.importFiles(portraitPaths, true, portraitBin, false);
            }
        }

        // 3. IMPORT TIMELINE CLIPS
        var timelineFiles = timelineFolder.getFiles(/\.(mp4|mov|avi|mkv)$/i);
        if (timelineFiles.length === 0) {
            alert("No clips found in the Timeline folder.");
            return;
        }

        // Sort files alphabetically to respect the Python script's numbering
        timelineFiles.sort(function(a, b) {
            return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1;
        });

        var timelineBin = app.project.rootItem.createBin("Timeline_Clips");
        var timelinePaths = [];
        for (var t = 0; t < timelineFiles.length; t++) {
            timelinePaths.push(timelineFiles[t].fsName);
        }
        app.project.importFiles(timelinePaths, true, timelineBin, false);

        // 4. PREPARE CLIPS FOR TIMELINE
        // We need to get the ProjectItems from the bin, sorted correctly
        var clipsToPlace = [];
        // Note: Premiere import might not preserve order in children, so we re-sort by name
        var tempArray = [];
        for (var i = 0; i < timelineBin.children.numItems; i++) {
            var item = timelineBin.children[i];
            if (item.type === 1) { // CLIP
                tempArray.push(item);
            }
        }
        tempArray.sort(function(a, b) {
            return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1;
        });

        // Filter duration > 2s
        for (var j = 0; j < tempArray.length; j++) {
            var clip = tempArray[j];
            if ((clip.getOutPoint().seconds - clip.getInPoint().seconds) > 2) {
                clipsToPlace.push(clip);
            }
        }

        if (clipsToPlace.length === 0) {
            alert("No valid clips (> 2s) found for the timeline.");
            return;
        }

        // 5. TRIM CLIPS (15 frames)
        var trimSeconds = 15 / 30; // 15 frames at 30fps
        for (var k = 0; k < clipsToPlace.length; k++) {
            var c = clipsToPlace[k];
            var start = c.getInPoint().seconds;
            var end = c.getOutPoint().seconds;
            if ((end - start) > (trimSeconds * 3)) {
                c.setInPoint(start + trimSeconds, 4);
                c.setOutPoint(end - trimSeconds, 4);
            }
        }

        // 6. CREATE SEQUENCE AND ADD CLIPS
        var seqName = "AI_Sorted_Edit_" + new Date().getTime();
        app.project.createNewSequence(seqName, "");
        var activeSeq = app.project.activeSequence;
        
        if (!activeSeq) {
            alert("Failed to create sequence.");
            return;
        }

        var vTrack = activeSeq.videoTracks[0];
        var insertTime = 0;
        for (var l = 0; l < clipsToPlace.length; l++) {
            vTrack.overwriteClip(clipsToPlace[l], insertTime);
            insertTime += (clipsToPlace[l].getOutPoint().seconds - clipsToPlace[l].getInPoint().seconds);
        }

        // 7. APPLY RANDOM TRANSITIONS
        applyRandomTransitions();

        alert("Smart Edit Complete!\n- Imported " + clipsToPlace.length + " timeline clips.\n- Sorted by Folder/Name.\n- Created 'Portraits_Detected' bin.");

    } catch (err) {
        alert("Error: " + err.toString() + (err.line ? "\nLine: " + err.line : ""));
    }
}

function applyRandomTransitions() {
    try {
        var qeSeq = qe.project.getActiveSequence();
        var qeTrack = qeSeq.getVideoTrackAt(0);
        var transList = qe.project.getVideoTransitionList();
        
        var cleanList = [];
        for (var i = 0; i < transList.length; i++) {
            var n = transList[i];
            if (n.indexOf("VR") === -1 && n.indexOf("Morph") === -1) cleanList.push(n);
        }

        for (var j = 0; j < qeTrack.numItems - 1; j++) {
            var randomTransName = cleanList[Math.floor(Math.random() * cleanList.length)];
            var transObj = qe.project.getVideoTransitionByName(randomTransName);
            if (transObj) {
                qeTrack.getItemAt(j).addTransition(transObj, false, "00:00:00:15");
            }
        }
    } catch (e) {}
}

main();
