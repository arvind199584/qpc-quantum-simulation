/**
 * Premiere Pro 2024 Script: Recursive Import, Sort, Trim, and Transitions
 */

app.enableQE(); // Enable QE at the top level

function runAutomation() {
    var project = app.project;
    if (!project) {
        alert("Please open a project first.");
        return;
    }

    // 1. SELECT FOLDER
    var folder = Folder.selectDialog("Select folder with MP4s");
    if (!folder) return;

    // 2. IMPORT FILES RECURSIVELY
    var filePaths = [];
    function findMp4s(dir) {
        var items = dir.getFiles();
        for (var i = 0; i < items.length; i++) {
            if (items[i] instanceof Folder) findMp4s(items[i]);
            else if (items[i].name.toLowerCase().match(/\.mp4$/)) filePaths.push(items[i].fsName);
        }
    }
    findMp4s(folder);

    if (filePaths.length === 0) {
        alert("No MP4 files found.");
        return;
    }

    // 3. IMPORT INTO PROJECT
    // Import to root to keep it simple and avoid bin creation errors
    project.importFiles(filePaths, true, project.rootItem, false);

    // 4. FIND VALID CLIPS AND SORT BY DATE
    var clips = [];
    for (var j = 0; j < project.rootItem.children.numItems; j++) {
        var item = project.rootItem.children[j];
        // 1 is the value for ProjectItemType.CLIP
        if (item.type === 1) { 
            var dur = item.getOutPoint().seconds - item.getInPoint().seconds;
            if (dur > 2) {
                clips.push({
                    item: item,
                    date: getMediaDate(item)
                });
            }
        }
    }

    if (clips.length === 0) {
        alert("No clips > 2s found.");
        return;
    }

    // Sort by date ascending
    clips.sort(function(a, b) { return a.date - b.date; });

    // 5. CREATE SEQUENCE
    var seqName = "Auto_Sequence_" + new Date().getTime();
    project.createNewSequence(seqName, "");
    var activeSeq = project.activeSequence;
    if (!activeSeq) {
        alert("Failed to create sequence.");
        return;
    }

    // 6. TRIM AND ADD TO TIMELINE
    var vTrack = activeSeq.videoTracks[0];
    var insertTime = 0;
    var trimOffset = 15 / 30; // 15 frames at 30fps

    for (var k = 0; k < clips.length; k++) {
        var projectClip = clips[k].item;
        
        // Apply trimming
        var currentIn = projectClip.getInPoint().seconds;
        var currentOut = projectClip.getOutPoint().seconds;
        if ((currentOut - currentIn) > (trimOffset * 3)) {
            projectClip.setInPoint(currentIn + trimOffset, 4);
            projectClip.setOutPoint(currentOut - trimOffset, 4);
        }

        // Overwrite onto timeline
        vTrack.overwriteClip(projectClip, insertTime);
        insertTime += (projectClip.getOutPoint().seconds - projectClip.getInPoint().seconds);
    }

    // 7. APPLY RANDOM TRANSITIONS
    applyRandomTransitions();

    alert("Completed! " + clips.length + " clips processed.");
}

function applyRandomTransitions() {
    try {
        var qeSeq = qe.project.getActiveSequence();
        var qeTrack = qeSeq.getVideoTrackAt(0);
        var transList = qe.project.getVideoTransitionList();
        
        // Filter out VR and problematic ones
        var cleanList = [];
        for (var i = 0; i < transList.length; i++) {
            var n = transList[i];
            if (n.indexOf("VR") === -1 && n.indexOf("Morph") === -1) cleanList.push(n);
        }

        // Apply transitions between clips
        for (var j = 0; j < qeTrack.numItems - 1; j++) {
            var randomTransName = cleanList[Math.floor(Math.random() * cleanList.length)];
            var transObj = qe.project.getVideoTransitionByName(randomTransName);
            if (transObj) {
                qeTrack.getItemAt(j).addTransition(transObj, false, "00:00:00:15");
            }
        }
    } catch (e) {
        // QE is optional/unstable
    }
}

function getMediaDate(item) {
    try {
        var xmp = item.getProjectMetadata();
        var match = xmp.match(/<exif:DateTimeOriginal>(.*?)<\/exif:DateTimeOriginal>/i) ||
                    xmp.match(/<xmp:CreateDate>(.*?)<\/xmp:CreateDate>/i) ||
                    xmp.match(/MediaCreationDate>(.*?)<\/.*?MediaCreationDate/i);
        if (match && match[1]) return new Date(match[1]).getTime();
    } catch (e) {}
    try {
        var f = new File(item.getMediaPath());
        if (f.exists) return f.created.getTime();
    } catch (e) {}
    return 0;
}

runAutomation();
