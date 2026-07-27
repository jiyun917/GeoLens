# Introduction to Seismic Interpretation

## Overview

Seismic interpretation is the process of extracting geological information
from seismic reflection data. Interpreters identify subsurface structures,
stratigraphic features, and hydrocarbon indicators by analyzing amplitude
patterns, waveform characteristics, and reflector continuity across
processed seismic volumes.

## Data Types

A seismic dataset typically arrives as one of two primary volume types:

- **Pre-stack** data contains individual traces before summation across
  common midpoint gathers. Pre-stack analysis supports AVO (amplitude
  versus offset) work and detailed velocity modeling.
- **Post-stack** data has been summed and migrated to produce a single
  trace per surface location. Post-stack volumes are the standard input
  for horizon picking and structural interpretation.

Volumes are stored in industry formats such as SEG-Y or SEG-D, which
encode trace headers alongside sample values. The interpretation
software reads these headers to reconstruct the survey geometry.

## Basic Terminology

- **Inline** and **crossline** are the two orthogonal directions in a
  3D survey grid. Inlines run parallel to the acquisition direction,
  crosslines perpendicular. Together they index every trace in the
  volume.
- **Time slice** (or **z-slice**) is a horizontal section extracted at
  a constant two-way travel time. Time slices reveal areal patterns
  such as channels and structural contours.
- **Horizon** is a continuous reflector interpreted across the volume,
  typically corresponding to a stratigraphic boundary of interest.
- **Fault** is a discontinuity in reflector continuity representing a
  break in the subsurface rock body.

## Typical Interpretation Workflow

An interpretation project generally proceeds through the following
phases: (1) load the seismic volume and quality-check the geometry,
(2) display inline, crossline, and time-slice sections in the 3D scene
to build a mental model of the survey, (3) pick key horizons across
the volume using auto-tracking or manual seed picking, (4) map faults
on inline sections and correlate them across crosslines, and (5)
extract attributes (similarity, curvature, spectral decomposition) that
highlight subtle features not visible in the raw amplitude.

## Coordinate Reference

Every trace in an interpreted survey has three coordinates: inline
number, crossline number, and vertical sample (time or depth). The
software maintains a bijection between (inline, crossline) grid indices
and the field coordinates (x, y) defined at survey load time. All
picked horizons, faults, and extracted geometries inherit this
reference frame.
