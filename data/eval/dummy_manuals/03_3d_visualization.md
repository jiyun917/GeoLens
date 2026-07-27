# 3D Visualization

## Overview

The 3D Scene is the primary interpretation view: a rotatable, zoomable
container that renders any combination of inline, crossline, time-slice,
horizon, well, and fault objects in a shared world-coordinate space.
Building an informative 3D Scene is the interpretive-workflow analogue
of composing a good figure — it determines what the interpreter can and
cannot see.

## Adding a Display

Every display in the 3D Scene is created from the Tree Scene panel on
the left side of the main window. The three display types added most
often are:

- **In-line**: a vertical slice at a fixed inline number, showing
  reflectors along one shooting-direction plane.
- **Cross-line**: a vertical slice at a fixed crossline number,
  orthogonal to inlines.
- **Z-slice**: a horizontal slice at a fixed time (or depth). Called a
  "time slice" for time-domain volumes.

To add an inline: right-click **In-line** in the Tree Scene, choose
**Add Data**, and select the seismic dataset from the popup list.
Repeat for **Cross-line** and **Z-slice**. Each new display appears in
the 3D Scene at a default index (mid-volume for slices, first entry
for line displays).

## Positioning a Slice

Once a display is added, its position in the volume can be adjusted:

- Click and drag the slice handle in the 3D Scene to translate it
  along its normal.
- Right-click the display in the Tree Scene and choose **Position…** to
  enter an exact inline/crossline/time value.
- Use the arrow keys with the display focused to step ±1 unit along the
  slice's normal direction.

## Color Bar and Amplitude Range

Each display carries its own color bar, controlling how amplitude
values map to on-screen color. Right-click a display and choose
**Properties** to open the amplitude-range editor. The default range
is symmetric around zero and clipped at the 99th percentile of the
loaded amplitude distribution; use this default unless the volume
carries a known reference amplitude that requires a fixed clip.

## Completion Criteria for a Standard 3D Scene

A minimal 3D Scene for early-stage interpretation contains:

1. One **In-line** display near the survey center.
2. One **Cross-line** display near the survey center.
3. One **Z-slice** at a mid-volume time.

When all three orthogonal displays are present and correctly positioned,
the reflection package structure is clearly visible, and the
color-bar amplitude range is consistent across displays, the 3D Scene
setup is complete. Downstream steps (horizon picking, attribute
extraction) can now proceed against this scene as their working view.
