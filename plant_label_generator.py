#!/usr/bin/env python3
"""
Plant Label STL Generator

This script reads a CSV file containing plant information and automatically generates
STL files for 3D printable plant labels using OpenSCAD.

Requirements:
- Python 3.6+
- pandas library (pip install pandas)
- OpenSCAD installed and accessible from command line

Usage:
    python plant_label_generator.py

The script will:
1. Read 'plant_list.csv'
2. Generate individual .scad files for each plant
3. Use OpenSCAD to render .stl files for 3D printing
4. Clean up temporary .scad files (optional)

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
from pathlib import Path

class PlantLabelGenerator:
    def __init__(self, csv_file="plant_list.csv", template_file="Enhanced Plant Labeler.scad"):
        self.csv_file = csv_file
        self.template_file = template_file
        self.output_dir = "generated_labels"
        self.temp_dir = "temp_scad"
        
        # Create output directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(self.temp_dir).mkdir(exist_ok=True)
    
    def convert_boolean_to_openscad(self, value):
        """Convert TRUE/FALSE strings to OpenSCAD boolean values"""
        if pd.isna(value):
            return "false"
        
        value_str = str(value).strip().upper()
        if value_str == "TRUE":
            return "true"
        elif value_str == "FALSE":
            return "false"
        else:
            # Handle numeric values (1/0) for backward compatibility
            try:
                numeric_val = float(value)
                return "true" if numeric_val != 0 else "false"
            except (ValueError, TypeError):
                return "false"  # Default to false for invalid values
    
    def sanitize_filename(self, name):
        """Create a safe filename from plant name"""
        # Remove special characters and replace spaces with underscores
        filename = re.sub(r'[^\w\s-]', '', name)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename.strip('_')
    
    def load_template(self):
        """Load the OpenSCAD template file"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Template file '{self.template_file}' not found!")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading template file: {e}")
            sys.exit(1)
    
    def extract_nickname(self, common_name):
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
    
    def generate_scad_content(self, plant_data, template):
        """Generate OpenSCAD content for a specific plant"""
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
        spike = self.convert_boolean_to_openscad(plant_data['Spike'])
        holes = self.convert_boolean_to_openscad(plant_data['Holes'])
        
        # Get dimensions with defaults
        width = float(plant_data['Width']) if pd.notna(plant_data['Width']) else 80.0
        height = float(plant_data['Height']) if pd.notna(plant_data['Height']) else 30.0
        
        # Replace individual parameters in the template
        modified_content = template
        
        # Replace plant_name
        modified_content = re.sub(
            r'plant_name\s*=\s*"[^"]*";',
            f'plant_name = "{common_name}";',
            modified_content
        )
        
        # Replace scientific_name
        modified_content = re.sub(
            r'scientific_name\s*=\s*"[^"]*";',
            f'scientific_name = "{scientific_name}";',
            modified_content
        )
        
        # Replace nickname
        modified_content = re.sub(
            r'nickname\s*=\s*"[^"]*";',
            f'nickname = "{nickname}";',
            modified_content
        )
        
        # Replace water_drops (now supports 1-4 range)
        modified_content = re.sub(
            r'water_drops\s*=\s*\d+;',
            f'water_drops = {water_drops};',
            modified_content
        )
        
        # Replace light_type (now supports 1-4 range)
        modified_content = re.sub(
            r'light_type\s*=\s*\d+;',
            f'light_type = {light_type};',
            modified_content
        )
        
        # Replace show_dry_soil_symbol
        modified_content = re.sub(
            r'show_dry_soil_symbol\s*=\s*(true|false);',
            f'show_dry_soil_symbol = {dry_between_waterings};',
            modified_content
        )
        
        # Replace spike_enabled
        modified_content = re.sub(
            r'spike_enabled\s*=\s*(true|false);',
            f'spike_enabled = {spike};',
            modified_content
        )
        
        # Replace enable_hanging_holes
        modified_content = re.sub(
            r'enable_hanging_holes\s*=\s*(true|false);',
            f'enable_hanging_holes = {holes};',
            modified_content
        )
        
        # Replace label_width
        modified_content = re.sub(
            r'label_width\s*=\s*[\d.]+;',
            f'label_width = {width};',
            modified_content
        )
        
        # Replace label_height
        modified_content = re.sub(
            r'label_height\s*=\s*[\d.]+;',
            f'label_height = {height};',
            modified_content
        )
        
        # Replace symbol_size_multiplier to 1.0
        modified_content = re.sub(
            r'symbol_size_multiplier\s*=\s*[\d.]+;',
            f'symbol_size_multiplier = 1.0;',
            modified_content
        )
        
        return modified_content
    
    def generate_scad_file(self, plant_data, template):
        """Generate a .scad file for a specific plant"""
        filename = self.sanitize_filename(plant_data['Common Name'])
        scad_filename = f"{self.temp_dir}/{filename}.scad"
        
        content = self.generate_scad_content(plant_data, template)
        
        try:
            with open(scad_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return scad_filename, filename
        except Exception as e:
            print(f"Error writing SCAD file for {plant_data['Common Name']}: {e}")
            return None, None
    
    def render_stl(self, scad_file, output_filename):
        """Use OpenSCAD to render STL file"""
        stl_output = f"{self.output_dir}/{output_filename}.stl"
        
        try:
            # OpenSCAD command to render STL
            cmd = ["openscad", "-o", stl_output, scad_file]
            
            print(f"Rendering {output_filename}.stl...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✓ Successfully created {stl_output}")
                return True
            else:
                print(f"✗ Failed to render {output_filename}.stl")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout rendering {output_filename}.stl")
            return False
        except FileNotFoundError:
            print("✗ OpenSCAD not found! Please install OpenSCAD and make sure it's in your PATH.")
            print("Download from: https://openscad.org/downloads.html")
            return False
        except Exception as e:
            print(f"✗ Error rendering {output_filename}.stl: {e}")
            return False
    
    def check_openscad(self):
        """Check if OpenSCAD is available"""
        try:
            result = subprocess.run(["openscad", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"OpenSCAD found: {result.stdout.strip()}")
                return True
        except:
            pass
        
        print("⚠️  OpenSCAD not found in PATH!")
        print("Please install OpenSCAD from: https://openscad.org/downloads.html")
        print("Make sure it's accessible from command line.")
        return False
    
    def load_plant_data(self):
        """Load plant data from CSV file"""
        try:
            df = pd.read_csv(self.csv_file)
            print(f"Loaded {len(df)} plants from {self.csv_file}")
            
            # Verify required columns
            required_cols = ['Common Name', 'Scientific Name', 'Water', 'Light',
                           'Dry between Waterings', 'Spike', 'Holes']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Error: Missing required columns: {missing_cols}")
                print(f"Available columns: {list(df.columns)}")
                return None
            
            # Optional columns with defaults
            if 'Nickname' not in df.columns:
                print("Note: 'Nickname' column not found - will extract from Common Name")
            if 'Width' not in df.columns:
                print("Note: 'Width' column not found - will use default 80mm")
            if 'Height' not in df.columns:
                print("Note: 'Height' column not found - will use default 30mm")
            
            return df
        except FileNotFoundError:
            print(f"Error: CSV file '{self.csv_file}' not found!")
            return None
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    
    def cleanup_temp_files(self, keep_scad=False):
        """Clean up temporary SCAD files"""
        if not keep_scad:
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary files in {self.temp_dir}")
            except Exception as e:
                print(f"Warning: Could not clean up temp files: {e}")
    
    def generate_all_labels(self, keep_scad_files=False):
        """Main method to generate all plant labels"""
        print("🌱 Plant Label STL Generator")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_openscad():
            return False
        
        # Load data
        df = self.load_plant_data()
        if df is None:
            return False
        
        template = self.load_template()
        
        # Process each plant
        successful = 0
        failed = 0
        
        print(f"\nGenerating labels for {len(df)} plants...")
        print("-" * 50)
        
        for index, plant in df.iterrows():
            plant_name = plant['Common Name']
            print(f"\n[{index+1}/{len(df)}] Processing: {plant_name}")
            
            # Generate SCAD file
            scad_file, filename = self.generate_scad_file(plant, template)
            if scad_file is None:
                failed += 1
                continue
            
            # Render STL
            if self.render_stl(scad_file, filename):
                successful += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🎉 Generation complete!")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"📁 STL files saved to: {self.output_dir}/")
        
        if keep_scad_files:
            print(f"📁 SCAD files saved to: {self.temp_dir}/")
        else:
            self.cleanup_temp_files()
        
        return successful > 0

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate 3D printable plant labels from CSV data')
    parser.add_argument('--csv', default='plant list.csv', help='CSV file with plant data')
    parser.add_argument('--template', default='Enhanced Plant Labeler.scad', help='OpenSCAD template file')
    parser.add_argument('--keep-scad', action='store_true', help='Keep temporary SCAD files')
    parser.add_argument('--output-dir', default='generated_labels', help='Output directory for STL files')
    
    args = parser.parse_args()
    
    # Create generator
    generator = PlantLabelGenerator(args.csv, args.template)
    generator.output_dir = args.output_dir
    
    # Generate all labels
    success = generator.generate_all_labels(args.keep_scad)
    
    if success:
        print(f"\n🎯 Ready for 3D printing! Check the '{generator.output_dir}' folder.")
    else:
        print("\n❌ Generation failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()