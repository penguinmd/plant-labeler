# Plant Labeler

A 3D printable plant labeling system with customizable labels for garden organization.

## Overview

This project provides tools for creating custom plant labels that can be 3D printed. It includes both the 3D model files and a Python script for generating labels with plant information.

## Files

- **Enhanced Plant Labeler.scad** - OpenSCAD file for the 3D printable plant label design
- **Enhanced Plant Labeler.json** - Configuration file for the label parameters
- **plant_label_generator.py** - Python script to generate customized labels
- **plant list.csv** - Sample plant data for label generation
- **5 plants.3mf** - Pre-generated 3D model file ready for printing

## Usage

### 3D Printing
1. Open `Enhanced Plant Labeler.scad` in OpenSCAD
2. Customize the label parameters as needed
3. Export as STL for 3D printing
4. Alternatively, use the pre-generated `5 plants.3mf` file

### Label Generation
1. Edit `plant list.csv` with your plant information
2. Run the Python generator:
   ```bash
   python plant_label_generator.py
   ```
3. The script will generate customized labels based on your plant data

## Requirements

- **For 3D modeling**: OpenSCAD
- **For label generation**: Python 3.x
- **For 3D printing**: Any FDM 3D printer

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Feel free to use and modify as needed.