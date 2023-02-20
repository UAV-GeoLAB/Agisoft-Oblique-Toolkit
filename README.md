# UAV Geolab - Agisoft Oblique Toolkit v1.1
## About
This toolkit was created to perform more efficient computing while processing blocks of aerial oblique imagery blocks 
eg. Leica CityMapper data.

## Installation
Whole toolkit is just .py file collection, so there's no need to perform real installation. To make sure the toolkit
works just install python requirements USING METASHAPE BUILT-IN INTERPRETER. If your not sure how to do it you can try
to use configuration script placed in *scripts* directory. Just run it with any python on your PC.


## Usage:
All stages must be run sequentially one after another.

### Requirements
There are certain requirements that your project must apply to for toolkit to work properly:
* CRS - make sure you use some kind of projected cartesian coordinate system (eg. UTM).
* Rotation - currently there's no Roll-Pitch-Heading to Omega-Phi-Kappa conversion mechanism implemented
inside our toolkit, so make sure to convert your project to Omega-Phi-Kappa.
* Camera calibration - our toolkit uses camera calibration for few calculations. Therefore, you need to specify
either:
  * Focal length in pixels
  * Focal length in mm + Physical pixel size

### 1. Footprints generation (Oblique/Create footprints)
First step of processing is to create 2D footprint for every image in the block. Footprint is calculated based on
initial EO (Reference) and camera calibration image matrix size and focal lenght  (Tools/Camera calibration).
Footprints will be placed in new shape group called "Footprints".

### 2. Direction assignment (Oblique/Group by direction)
For better image alignment we need to split images into directions (Nadir, Front etc.). Currently image from every
direction will be moved to new camera group, so if your chunk has important directories structure be ready to lose it...

### (optional) 3. Block definition (Oblique/Create blocks) 
When working with big datasets you can use this tool to perform two main tasks:
* Filter images by AOI - if there's other shape group except Footprints containing just one polygon feature images
which footprints does not overlap with AOI polygon will be moved to new camera group.
* Build processing blocks - additionally, you can "cut" AOI polygon with line features and split your data to multiple
chunks, that will be processed separately.

### 4. Guided image matching (Oblique/Footprint-based image matching)
Images will be matched using built-in Agisoft Metashape algorithm, but pairs will be generated based on footprints
overlap.

### 5. Two-stage image alignment (Oblique/Multi-stage image alignment)
Based on previous image matching now algorithm will perform proper Bundle Adjustment. Alignment will be performed 
sequentially - first Oblique images, then Front, Left and so on... 

### 6. (optional) Tie points filtering (Oblique/Tie points filtering)
This function will filter tie points based on its projections. It's recommended to make copy of aligned chunk first.
Filtering step is optional. After execution make sure to optimize cameras again.