# 3D Printable Plant Labels

A comprehensive system for creating custom 3D printable plant labels with intuitive care symbols. Generate professional-looking plant labels with water and light requirement indicators, plus optional features like planting spikes and hanging holes.

## 🌟 Features

### Visual Care Symbols
- **Progress Bar Style Indicators**: Intuitive 4-level system for water and light requirements
- **Water Drops**: 1-4 drops that fill left-to-right based on water needs
- **Sun Symbols**: 1-4 suns that fill left-to-right based on light intensity  
- **Cactus Symbol**: Optional "water sparingly" reminder for plants that need dry soil between waterings

### Customizable Design
- **Multiple Text Fields**: Common name, scientific name, and optional nickname
- **Flexible Sizing**: Custom width and height (defaults: 80mm × 30mm)
- **Optional Features**: Planting spike, hanging holes, decorative frame
- **Print-Optimized**: Designed for reliable 3D printing with raised text and symbols

### Automated Generation - Enhanced Version
- **Robust Batch Processing**: Generate multiple labels from CSV data with comprehensive validation
- **Command-Line Parameter Passing**: Uses OpenSCAD's `-D` flag for reliable parameter injection
- **Data Validation**: Comprehensive error checking with detailed reporting
- **Configurable Parameters**: Override any OpenSCAD parameter via command line
- **Duplicate Detection**: Automatically identifies and handles duplicate entries
- **Enhanced Error Handling**: Detailed logging and validation feedback

## 📁 Project Structure

```
plant-labeler/
├── enhanced_plant_labeler.scad    # Main OpenSCAD file
├── plant_label_generator.py       # Python automation script
├── plant_list.csv                 # Plant data in CSV format
├── examples/                      # Example STL files
└── README.md                      # This file
```

## 🚀 Quick Start

### Method 1: Individual Labels (OpenSCAD)

1. **Install OpenSCAD**: Download from [openscad.org](https://openscad.org/downloads.html)
2. **Open the file**: Load `enhanced_plant_labeler.scad` in OpenSCAD
3. **Customize**: Use the Customizer panel (Window → Customizer) to set:
   - Plant names and care requirements
   - Label dimensions and features
   - Symbol preferences
4. **Generate**: Press F6 to render, then export as STL

### Method 2: Batch Generation (Python + OpenSCAD)

1. **Install Requirements**:
   ```bash
   pip install pandas
   ```
   
2. **Prepare Your Data**: Edit `plant_list.csv` with your plants (see CSV format below)

3. **Generate All Labels**:
   ```bash
   python plant_label_generator.py --csv plant_list.csv --template enhanced_plant_labeler.scad
   ```

4. **Find Your STL Files**: Check the `generated_labels/` folder

## 📊 CSV Format

Your CSV file should contain these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Nickname` | Text (Optional) | Short nickname for the plant | "Lemon Lime" |
| `Common Name` | Text (Required) | Full common name | "Maranta 'Lemon Lime'" |
| `Scientific Name` | Text (Required) | Botanical name | "Maranta leuconeura" |
| `Water` | Number (Required) | Water requirement level 1-4 | 2 |
| `Light` | Number (Required) | Light requirement level 1-4 | 3 |
| `Dry between Waterings` | TRUE/FALSE (Required) | Show cactus symbol | TRUE |
| `Spike` | TRUE/FALSE (Required) | Include planting spike | TRUE |
| `Holes` | TRUE/FALSE (Required) | Include hanging holes | FALSE |
| `Width` | Number (Optional) | Label width in mm | 80 |
| `Height` | Number (Optional) | Label height in mm | 30 |

### Care Level Guide

**Water Levels (1-4):**
- 1 = Low water needs (drought tolerant)
- 2 = Moderate water needs  
- 3 = Regular water needs
- 4 = High water needs (keep moist)

**Light Levels (1-4):**
- 1 = Low light (shade tolerant)
- 2 = Medium light (bright indirect)
- 3 = Bright light (some direct sun)
- 4 = Full sun (direct sunlight)

### Example CSV Row
```csv
Nickname,Common Name,Scientific Name,Water,Light,Dry between Waterings,Spike,Holes,Width,Height
Lemon Lime,Maranta 'Lemon Lime',Maranta leuconeura,2,2,TRUE,TRUE,FALSE,80,30
```

## 🎨 Symbol System

### Water Requirement Symbols
The water symbols use a progress bar approach with 1-4 water drops:
- **1 Drop**: Minimal water (succulents, cacti)
- **2 Drops**: Low-moderate water (most houseplants)  
- **3 Drops**: Regular water (tropical plants)
- **4 Drops**: High water (water-loving plants)

### Light Requirement Symbols  
The light symbols use 1-4 sun icons:
- **1 Sun**: Low light (north windows, shade)
- **2 Suns**: Medium light (east/west windows)
- **3 Suns**: Bright light (south windows, some direct sun)
- **4 Suns**: Full sun (outdoor direct sunlight)

### Special Symbols
- **Cactus**: Appears when "Dry between Waterings" is TRUE - reminds you to let soil dry completely between waterings

## ⚙️ Advanced Customization

### OpenSCAD Parameters

Key parameters you can adjust in the OpenSCAD file:

```openscad
// Plant Information
plant_name = "Your Plant Name";
scientific_name = "Scientific name";
nickname = "Optional nickname";

// Care Requirements  
water_drops = 2;        // 1-4 water level
light_type = 3;         // 1-4 light level

// Label Dimensions
label_width = 80;       // Width in mm
label_height = 30;      // Height in mm
label_thickness = 3;    // Base thickness in mm

// Features
spike_enabled = true;           // Planting spike
enable_hanging_holes = false;   // Hanging holes
show_dry_soil_symbol = true;    // Cactus symbol
```

### Python Script Options - Enhanced Version

The enhanced script provides comprehensive command-line configuration:

```bash
python plant_label_generator.py [options]

# Basic Options
--csv CSV_FILE              CSV file with plant data (default: plant_list.csv)
--template TEMPLATE_FILE    OpenSCAD template file (default: enhanced_plant_labeler.scad)
--output-dir OUTPUT_DIR     Output directory for STL files (default: generated_labels)
--verbose, -v               Enable detailed logging and validation output

# Label Dimensions
--label-width WIDTH         Label width in mm (default: 80)
--label-height HEIGHT       Label height in mm (default: 30)
--label-thickness THICK     Label thickness in mm (default: 3)

# Text Appearance
--text-height HEIGHT        Height of raised text in mm (default: 1.5)
--text-size MULTIPLIER      Text size multiplier (default: 1.0)
--font FONT_NAME           Font for text rendering (default: Liberation Sans)

# Symbol Appearance
--symbol-size MULTIPLIER    Symbol size multiplier (default: 1.0)

# Display Options
--no-plant-name            Hide plant common name
--no-scientific-name       Hide scientific name
--no-nickname              Hide nickname
--no-water-symbols         Hide water requirement symbols
--no-light-symbols         Hide light requirement symbols

# Frame and Border
--no-frame                 Disable raised frame border
--corner-radius RADIUS     Radius for rounded corners (default: 3)
--frame-width WIDTH        Width of raised frame border (default: 1.5)
--frame-height HEIGHT      Height of raised frame (default: 0.8)

# Spike Options (overrides CSV settings)
--no-spike                 Disable spike for all labels
--spike-length LENGTH      Length of spike in mm (default: 40)
--spike-width WIDTH        Width of spike at base in mm (default: 6)
--spike-taper RATIO        Spike taper ratio (default: 0.7)
--spike-position POS       Spike position: -1=left, 0=center, 1=right (default: 0)

# Hanging Holes (overrides CSV settings)
--no-holes                 Disable hanging holes for all labels
--hole-diameter DIAMETER   Diameter of hanging holes in mm (default: 3)
--hole-margin-x MARGIN     Horizontal distance from edge (default: 4)
--hole-margin-y MARGIN     Vertical distance from edge (default: 4)
```

### Usage Examples

```bash
# Basic usage with validation output
python plant_label_generator.py --verbose

# Custom dimensions and no spikes
python plant_label_generator.py --label-width 100 --label-height 40 --no-spike

# Large symbols for better visibility
python plant_label_generator.py --symbol-size 2.0 --text-size 1.2

# Minimal labels (text only, no symbols or features)
python plant_label_generator.py --no-water-symbols --no-light-symbols --no-spike --no-holes --no-frame

# Custom CSV and template files
python plant_label_generator.py --csv my_plants.csv --template my_template.scad --output-dir my_labels
```

### Key Improvements

- **Robust Parameter Passing**: Uses OpenSCAD's `-D` flag instead of file modification
- **Comprehensive Validation**: Validates all CSV data with detailed error reporting
- **Duplicate Detection**: Automatically identifies and removes duplicate entries
- **Flexible Configuration**: Override any OpenSCAD parameter via command line
- **Enhanced Logging**: Detailed progress and error information with `--verbose`
- **No Temporary Files**: Direct STL generation without intermediate file creation

## 🖨️ 3D Printing Tips

### Recommended Settings
- **Layer Height**: 0.2mm for good detail
- **Infill**: 15-20% (labels don't need to be solid)
- **Supports**: Not needed - designed to print without supports
- **Orientation**: Print with text facing up for best quality

### Material Recommendations
- **PLA**: Easy to print, good for indoor use
- **PETG**: More durable, weather resistant for outdoor use
- **ASA/ABS**: Best for outdoor durability and UV resistance

### Post-Processing
- Light sanding can improve text readability
- Consider painting raised text with contrasting colors
- Seal outdoor labels with appropriate coating

## 📂 Examples

Check the `examples/` folder for sample STL files showing different configurations and plant types.

## 🛠️ Development

### Requirements
- **OpenSCAD**: For 3D modeling and STL generation
- **Python 3.6+**: For automation scripts
- **pandas**: For CSV processing (`pip install pandas`)

### File Structure
- `enhanced_plant_labeler.scad`: Main OpenSCAD template with all customization options
- `plant_label_generator.py`: Python script for batch processing CSV data
- `plant_list.csv`: Example plant database in the required format

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs or suggest improvements
- Add new symbol designs or features
- Improve the documentation
- Share your plant label designs

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🌱 Happy Gardening!

Create beautiful, informative labels for your plant collection and never forget their care requirements again!