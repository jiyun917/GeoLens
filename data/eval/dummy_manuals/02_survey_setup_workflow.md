# Survey Setup Workflow

## Purpose

Before any interpretation work can begin, a new survey must be created
in the interpretation software. This chapter documents the standard
survey-setup workflow: creating the survey definition, loading the
seismic volume, and verifying that the resulting geometry matches the
acquisition metadata.

## Step 1 — Launch the Survey Manager

Open the interpretation software and select **Survey → New Survey**
from the top menu. The Survey Manager dialog appears. Enter a
descriptive name (avoid spaces and special characters — the software
uses the survey name as a directory identifier on disk) and choose a
data-root path with at least twice the disk space of the SEG-Y volume
you intend to load.

## Step 2 — Define the Grid

In the New Survey dialog:

1. Set the **coordinate system** (UTM zone or geographic).
2. Enter the **inline range** (start, stop, step).
3. Enter the **crossline range** (start, stop, step).
4. Enter the **Z range** (typically time in milliseconds; step is the
   sampling interval, usually 2 or 4 ms).

Click **OK** to create the survey directory structure. The Survey
Manager reports the created path.

## Step 3 — Load the Seismic Volume

Select **Survey → Load 3D Seismic Volume**. In the file browser, point
to the SEG-Y file. The software scans the file's binary and text
headers and pre-populates the trace-header byte mapping.

Confirm or adjust the byte offsets for inline number, crossline number,
X coordinate, and Y coordinate. Most SEG-Y files follow the SEG
Technical Standards Committee recommendations, but non-standard header
mappings are common in older data. If the preview shows scrambled
coordinates, revisit the byte-offset step.

Click **Import** to begin loading. Depending on volume size, the load
may take several minutes. Progress is reported in the status bar at
the bottom of the main window.

## Step 4 — Quality-Check the Geometry

After the load completes, open the **Tree Scene** and:

1. Right-click **In-line** in the tree, choose **Add Data**, and
   select the newly loaded seismic dataset. An inline section appears
   in the 3D Scene.
2. Right-click **Cross-line** and repeat.
3. Right-click **Z-slice** and add a slice at a mid-volume time.

Rotate the 3D Scene and confirm that the three orthogonal displays
form a coherent block. If any display is empty or shows a wall of
zeros, revisit the byte-offset mapping.

## Completion Criteria

The survey is considered set up when all three orthogonal displays
(In-line, Cross-line, Z-slice) render valid seismic amplitude and the
survey coordinate metadata matches the acquisition report. This is the
baseline state required for all downstream interpretation work
(horizon picking, fault mapping, attribute extraction).
