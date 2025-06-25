#!/usr/bin/env python3
"""
Plant Label STL Generator - Enhanced Version

This script reads a CSV file containing plant information and automatically generates
STL files for 3D printable plant labels using OpenSCAD with robust parameter passing.

Requirements:
- Python 3.6+
- pandas library (pip install pandas)
- OpenSCAD installed and accessible from command line

Usage:
    python plant_label_generator.py [options]

Key Features:
- Uses OpenSCAD's -D flag for robust parameter passing (no file modification)
- Comprehensive data validation with detailed error reporting
- Configurable OpenSCAD parameters via command line
- Duplicate detection and handling
- Enhanced error handling and logging

CSV Format:
The CSV file should contain the following columns:
- Nickname: Plant nickname (optional, extracted from Common Name if not provided)
- Common Name: Full common name of the plant
- Scientific Name: Scientific/botanical name
- Water: Water requirement level (1-4, where 1=low, 4=high)
- Light: Light requirement level (1-4, where 1=low light, 4=full sun)
- Dry between Waterings: TRUE/FALSE - whether to let soil dry between waterings
- Spike: TRUE/FALSE - whether plant has spikes/thorns
- Holes: TRUE/FALSE - whether to add drainage holes to label
- Width: Label width in mm (optional, defaults to 80mm)
- Height: Label height in mm (optional, defaults to 30mm)
"""

import pandas as pd
import subprocess
import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class PlantLabelGenerator:
    def __init__(self, csv_file: str = "plant_list.csv", template_file: str = "enhanced_plant_labeler.scad"):
        self.csv_file = csv_file
        self.template_file = template_file
        self.output_dir = "generated_labels"
        
        # OpenSCAD parameter defaults (can be overridden via command line)
        self.openscad_params = {
            # Label dimensions
            'label_width': 80,
            'label_height': 30,
            'label_thickness': 3,
            
            # Text appearance
            'text_height': 1.5,
            'text_size_multiplier': 1.0,
            
            # Symbol appearance
            'symbol_size_multiplier': 1.0,
            
            # Display options
            'show_plant_name': True,
            'show_scientific_name': True,
            'show_nickname': True,
            'show_water_symbols': True,
            'show_light_symbols': True,
            
            # Frame and border
            'show_frame': True,
            'corner_radius': 3,
            'frame_width': 1.5,
            'frame_height': 0.8,
            
            # Spike options
            'spike_length': 40,
            'spike_width': 6,
            'spike_taper': 0.7,
            'spike_position': 0,
            'spike_base_radius': 1.5,
            
            # Hanging holes
            'hole_diameter': 3,
            'hole_margin_x': 4,
            'hole_margin_y': 4,
            
            # Advanced
            'font_name': 'Liberation Sans'
        }
        
        # Create output directory
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def validate_csv_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Comprehensive validation of CSV data with detailed error reporting.
        Returns cleaned dataframe and list of validation warnings.
        """
        warnings = []
        errors = []
        
        # Check required columns
        required_cols = ['Common Name', 'Scientific Name', 'Water', 'Light',
                        'Dry between Waterings', 'Spike', 'Holes']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise DataValidationError(f"Missing required columns: {missing_cols}")
        
        # Validate each row
        valid_rows = []
        for index, row in df.iterrows():
            row_errors = []
            
            # Validate Common Name
            if pd.isna(row['Common Name']) or not str(row['Common Name']).strip():
                row_errors.append(f"Row {index+1}: Common Name is empty")
            
            # Validate Scientific Name
            if pd.isna(row['Scientific Name']) or not str(row['Scientific Name']).strip():
                row_errors.append(f"Row {index+1}: Scientific Name is empty")
            
            # Validate Water level (1-4)
            try:
                water_val = int(row['Water'])
                if not 1 <= water_val <= 4:
                    row_errors.append(f"Row {index+1}: Water level must be 1-4, got {water_val}")
            except (ValueError, TypeError):
                row_errors.append(f"Row {index+1}: Water level must be numeric (1-4), got '{row['Water']}'")
            
            # Validate Light level (1-4)
            try:
                light_val = int(row['Light'])
                if not 1 <= light_val <= 4:
                    row_errors.append(f"Row {index+1}: Light level must be 1-4, got {light_val}")
            except (ValueError, TypeError):
                row_errors.append(f"Row {index+1}: Light level must be numeric (1-4), got '{row['Light']}'")
            
            # Validate boolean fields
            for bool_field in ['Dry between Waterings', 'Spike', 'Holes']:
                if not self._is_valid_boolean(row[bool_field]):
                    row_errors.append(f"Row {index+1}: {bool_field} must be TRUE/FALSE, got '{row[bool_field]}'")
            
            # Validate dimensions if provided
            for dim_field in ['Width', 'Height']:
                if dim_field in df.columns and pd.notna(row[dim_field]):
                    try:
                        dim_val = float(row[dim_field])
                        if dim_val <= 0:
                            row_errors.append(f"Row {index+1}: {dim_field} must be positive, got {dim_val}")
                        elif dim_val > 200:  # Reasonable upper limit
                            warnings.append(f"Row {index+1}: {dim_field} is very large ({dim_val}mm)")
                    except (ValueError, TypeError):
                        row_errors.append(f"Row {index+1}: {dim_field} must be numeric, got '{row[dim_field]}'")
            
            if row_errors:
                errors.extend(row_errors)
            else:
                valid_rows.append(row)
        
        if errors:
            raise DataValidationError(f"Data validation failed:\n" + "\n".join(errors))
        
        # Check for duplicates
        if len(valid_rows) > 0:
            clean_df = pd.DataFrame(valid_rows)
            duplicates = clean_df.duplicated(subset=['Common Name', 'Scientific Name'], keep=False)
            if duplicates.any():
                duplicate_plants = clean_df[duplicates]['Common Name'].tolist()
                warnings.append(f"Found duplicate entries: {set(duplicate_plants)}")
                # Remove duplicates, keeping first occurrence
                clean_df = clean_df.drop_duplicates(subset=['Common Name', 'Scientific Name'], keep='first')
                warnings.append(f"Removed {duplicates.sum() - len(set(duplicate_plants))} duplicate rows")
        else:
            clean_df = pd.DataFrame()
        
        return clean_df, warnings
    
    def _is_valid_boolean(self, value: Any) -> bool:
        """Check if a value is a valid boolean representation"""
        if pd.isna(value):
            return True  # Will be converted to False
        
        value_str = str(value).strip().upper()
        return value_str in ['TRUE', 'FALSE', '1', '0', 'YES', 'NO']
    
    def convert_boolean_to_openscad(self, value: Any) -> str:
        """Convert various boolean representations to OpenSCAD boolean values"""
        if pd.isna(value):
            return "false"
        
        value_str = str(value).strip().upper()
        if value_str in ['TRUE', '1', 'YES']:
            return "true"
        elif value_str in ['FALSE', '0', 'NO']:
            return "false"
        else:
            # Handle numeric values for backward compatibility
            try:
                numeric_val = float(value)
                return "true" if numeric_val != 0 else "false"
            except (ValueError, TypeError):
                return "false"  # Default to false for invalid values
    
    def sanitize_filename(self, name: str) -> str:
        """Create a safe filename from plant name"""
        # Remove special characters and replace spaces with underscores
        filename = re.sub(r'[^\w\s-]', '', name)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename.strip('_')
    
    def extract_nickname(self, common_name: str) -> Tuple[str, str]:
        """Extract nickname from common name if it contains quotes"""
        # Look for text in single quotes like "Maranta 'Lemon Lime'"
        quote_match = re.search(r"'([^']*)'", common_name)
        if quote_match:
            nickname = quote_match.group(1)
            base_name = re.sub(r"'[^']*'", "", common_name).strip()
            return base_name, nickname
        
        # Look for text in double quotes
        quote_match = re.search(r'"([^"]*)"', common_name)
        if quote_match:
            nickname = quote_match.group(1)
            base_name = re.sub(r'"[^"]*"', "", common_name).strip()
            return base_name, nickname
        
        return common_name, ""
    
    def build_openscad_command(self, plant_data: pd.Series, output_file: str) -> List[str]:
        """
        Build OpenSCAD command using -D flags for parameter passing.
        This eliminates the need to modify the .scad file.
        """
        # Handle nickname - use dedicated column if available, otherwise extract from common name
        if 'Nickname' in plant_data and pd.notna(plant_data['Nickname']) and plant_data['Nickname'].strip():
            nickname = plant_data['Nickname']
            common_name = plant_data['Common Name']
        else:
            common_name, nickname = self.extract_nickname(plant_data['Common Name'])
        
        scientific_name = plant_data['Scientific Name']
        
        # Get numeric values for water and light (1-4 scale)
        water_drops = int(plant_data['Water']) if pd.notna(plant_data['Water']) else 2
        light_type = int(plant_data['Light']) if pd.notna(plant_data['Light']) else 2
        
        # Get boolean values and convert to OpenSCAD format
        dry_between_waterings = self.convert_boolean_to_openscad(plant_data['Dry between Waterings'])
        spike_enabled = self.convert_boolean_to_openscad(plant_data['Spike'])
        enable_hanging_holes = self.convert_boolean_to_openscad(plant_data['Holes'])
        
        # Get dimensions with defaults
        label_width = float(plant_data['Width']) if pd.notna(plant_data['Width']) else self.openscad_params['label_width']
        label_height = float(plant_data['Height']) if pd.notna(plant_data['Height']) else self.openscad_params['label_height']
        
        # Build command with -D parameters
        cmd = ["openscad", "-o", output_file]
        
        # Plant information parameters
        cmd.extend(["-D", f'plant_name="{common_name}"'])
        cmd.extend(["-D", f'scientific_name="{scientific_name}"'])
        cmd.extend(["-D", f'nickname="{nickname}"'])
        
        # Plant care parameters
        cmd.extend(["-D", f"water_drops={water_drops}"])
        cmd.extend(["-D", f"light_type={light_type}"])
        cmd.extend(["-D", f"show_dry_soil_symbol={dry_between_waterings}"])
        
        # Label configuration parameters
        cmd.extend(["-D", f"spike_enabled={spike_enabled}"])
        cmd.extend(["-D", f"enable_hanging_holes={enable_hanging_holes}"])
        cmd.extend(["-D", f"label_width={label_width}"])
        cmd.extend(["-D", f"label_height={label_height}"])
        
        # Add all configurable OpenSCAD parameters
        for param, value in self.openscad_params.items():
            if param not in ['label_width', 'label_height']:  # Already handled above
                if isinstance(value, bool):
                    cmd.extend(["-D", f"{param}={'true' if value else 'false'}"])
                elif isinstance(value, str):
                    cmd.extend(["-D", f'{param}="{value}"'])
                else:
                    cmd.extend(["-D", f"{param}={value}"])
        
        # Add the template file
        cmd.append(self.template_file)
        
        return cmd
    
    def render_stl(self, plant_data: pd.Series, output_filename: str) -> bool:
        """Use OpenSCAD to render STL file using command-line parameters"""
        stl_output = f"{self.output_dir}/{output_filename}.stl"
        
        try:
            # Build OpenSCAD command with -D parameters
            cmd = self.build_openscad_command(plant_data, stl_output)
            
            self.logger.info(f"Rendering {output_filename}.stl...")
            self.logger.debug(f"OpenSCAD command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info(f"✓ Successfully created {stl_output}")
                return True
            else:
                self.logger.error(f"✗ Failed to render {output_filename}.stl")
                self.logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"✗ Timeout rendering {output_filename}.stl")
            return False
        except FileNotFoundError:
            self.logger.error("✗ OpenSCAD not found! Please install OpenSCAD and make sure it's in your PATH.")
            self.logger.error("Download from: https://openscad.org/downloads.html")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error rendering {output_filename}.stl: {e}")
            return False
    
    def check_openscad(self) -> bool:
        """Check if OpenSCAD is available"""
        try:
            result = subprocess.run(["openscad", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info(f"OpenSCAD found: {result.stdout.strip()}")
                return True
        except:
            pass
        
        self.logger.error("⚠️  OpenSCAD not found in PATH!")
        self.logger.error("Please install OpenSCAD from: https://openscad.org/downloads.html")
        self.logger.error("Make sure it's accessible from command line.")
        return False
    
    def check_template_file(self) -> bool:
        """Check if the OpenSCAD template file exists"""
        if not Path(self.template_file).exists():
            self.logger.error(f"Template file '{self.template_file}' not found!")
            return False
        return True
    
    def load_plant_data(self) -> Optional[pd.DataFrame]:
        """Load and validate plant data from CSV file"""
        try:
            df = pd.read_csv(self.csv_file)
            self.logger.info(f"Loaded {len(df)} plants from {self.csv_file}")
            
            # Validate data
            clean_df, warnings = self.validate_csv_data(df)
            
            # Report warnings
            for warning in warnings:
                self.logger.warning(warning)
            
            if len(clean_df) < len(df):
                self.logger.info(f"After validation: {len(clean_df)} valid plants")
            
            return clean_df
            
        except FileNotFoundError:
            self.logger.error(f"CSV file '{self.csv_file}' not found!")
            return None
        except DataValidationError as e:
            self.logger.error(f"Data validation failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return None
    
    def generate_all_labels(self) -> bool:
        """Main method to generate all plant labels"""
        print("🌱 Plant Label STL Generator - Enhanced Version")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_openscad():
            return False
        
        if not self.check_template_file():
            return False
        
        # Load and validate data
        df = self.load_plant_data()
        if df is None or len(df) == 0:
            self.logger.error("No valid plant data to process")
            return False
        
        # Process each plant
        successful = 0
        failed = 0
        
        print(f"\nGenerating labels for {len(df)} plants...")
        print("-" * 60)
        
        for index, plant in df.iterrows():
            plant_name = plant['Common Name']
            print(f"\n[{index+1}/{len(df)}] Processing: {plant_name}")
            
            # Generate filename
            filename = self.sanitize_filename(plant_name)
            
            # Render STL directly using command-line parameters
            if self.render_stl(plant, filename):
                successful += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎉 Generation complete!")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"📁 STL files saved to: {self.output_dir}/")
        
        return successful > 0

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with all OpenSCAD parameters"""
    parser = argparse.ArgumentParser(
        description='Generate 3D printable plant labels from CSV data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plant_label_generator.py
  python plant_label_generator.py --csv my_plants.csv --template my_template.scad
  python plant_label_generator.py --label-width 100 --label-height 40
  python plant_label_generator.py --no-spike --no-holes --symbol-size 2.0
        """
    )
    
    # File options
    parser.add_argument('--csv', default='plant_list.csv', 
                       help='CSV file with plant data (default: plant_list.csv)')
    parser.add_argument('--template', default='enhanced_plant_labeler.scad', 
                       help='OpenSCAD template file (default: enhanced_plant_labeler.scad)')
    parser.add_argument('--output-dir', default='generated_labels', 
                       help='Output directory for STL files (default: generated_labels)')
    
    # Label dimensions
    parser.add_argument('--label-width', type=float, default=80,
                       help='Label width in mm (default: 80)')
    parser.add_argument('--label-height', type=float, default=30,
                       help='Label height in mm (default: 30)')
    parser.add_argument('--label-thickness', type=float, default=3,
                       help='Label thickness in mm (default: 3)')
    
    # Text appearance
    parser.add_argument('--text-height', type=float, default=1.5,
                       help='Height of raised text in mm (default: 1.5)')
    parser.add_argument('--text-size', type=float, default=1.0,
                       help='Text size multiplier (default: 1.0)')
    
    # Symbol appearance
    parser.add_argument('--symbol-size', type=float, default=1.0,
                       help='Symbol size multiplier (default: 1.0)')
    
    # Display options
    parser.add_argument('--no-plant-name', action='store_true',
                       help='Hide plant common name')
    parser.add_argument('--no-scientific-name', action='store_true',
                       help='Hide scientific name')
    parser.add_argument('--no-nickname', action='store_true',
                       help='Hide nickname')
    parser.add_argument('--no-water-symbols', action='store_true',
                       help='Hide water requirement symbols')
    parser.add_argument('--no-light-symbols', action='store_true',
                       help='Hide light requirement symbols')
    
    # Frame and border
    parser.add_argument('--no-frame', action='store_true',
                       help='Disable raised frame border')
    parser.add_argument('--corner-radius', type=float, default=3,
                       help='Radius for rounded corners (default: 3)')
    parser.add_argument('--frame-width', type=float, default=1.5,
                       help='Width of raised frame border (default: 1.5)')
    parser.add_argument('--frame-height', type=float, default=0.8,
                       help='Height of raised frame (default: 0.8)')
    
    # Spike options
    parser.add_argument('--no-spike', action='store_true',
                       help='Disable spike for all labels (overrides CSV)')
    parser.add_argument('--spike-length', type=float, default=40,
                       help='Length of spike in mm (default: 40)')
    parser.add_argument('--spike-width', type=float, default=6,
                       help='Width of spike at base in mm (default: 6)')
    parser.add_argument('--spike-taper', type=float, default=0.7,
                       help='Spike taper ratio (default: 0.7)')
    parser.add_argument('--spike-position', type=float, default=0,
                       help='Spike position along bottom edge -1=left, 0=center, 1=right (default: 0)')
    
    # Hanging holes
    parser.add_argument('--no-holes', action='store_true',
                       help='Disable hanging holes for all labels (overrides CSV)')
    parser.add_argument('--hole-diameter', type=float, default=3,
                       help='Diameter of hanging holes in mm (default: 3)')
    parser.add_argument('--hole-margin-x', type=float, default=4,
                       help='Horizontal distance from edge for holes (default: 4)')
    parser.add_argument('--hole-margin-y', type=float, default=4,
                       help='Vertical distance from edge for holes (default: 4)')
    
    # Advanced options
    parser.add_argument('--font', default='Liberation Sans',
                       help='Font for text rendering (default: Liberation Sans)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    return parser

def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create generator
    generator = PlantLabelGenerator(args.csv, args.template)
    generator.output_dir = args.output_dir
    
    # Update OpenSCAD parameters from command line arguments
    generator.openscad_params.update({
        'label_width': args.label_width,
        'label_height': args.label_height,
        'label_thickness': args.label_thickness,
        'text_height': args.text_height,
        'text_size_multiplier': args.text_size,
        'symbol_size_multiplier': args.symbol_size,
        'show_plant_name': not args.no_plant_name,
        'show_scientific_name': not args.no_scientific_name,
        'show_nickname': not args.no_nickname,
        'show_water_symbols': not args.no_water_symbols,
        'show_light_symbols': not args.no_light_symbols,
        'show_frame': not args.no_frame,
        'corner_radius': args.corner_radius,
        'frame_width': args.frame_width,
        'frame_height': args.frame_height,
        'spike_length': args.spike_length,
        'spike_width': args.spike_width,
        'spike_taper': args.spike_taper,
        'spike_position': args.spike_position,
        'spike_base_radius': 1.5,  # Keep default
        'hole_diameter': args.hole_diameter,
        'hole_margin_x': args.hole_margin_x,
        'hole_margin_y': args.hole_margin_y,
        'font_name': args.font
    })
    
    # Handle global overrides for spike and holes
    if hasattr(args, 'force_no_spike'):
        generator.force_no_spike = args.no_spike
    if hasattr(args, 'force_no_holes'):
        generator.force_no_holes = args.no_holes
    
    # Generate all labels
    success = generator.generate_all_labels()
    
    if success:
        print(f"\n🎯 Ready for 3D printing! Check the '{generator.output_dir}' folder.")
    else:
        print("\n❌ Generation failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()