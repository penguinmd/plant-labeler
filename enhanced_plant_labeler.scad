// OpenSCAD Script to generate plant labels with custom drawn symbols
//
// How to use:
// 1. Copy this code into OpenSCAD.
// 2. Use the Customizer (Window -> Customizer) to adjust settings.
// 3. Press F5 to preview (Render).
// 4. Press F6 to compile and render (this is required for export).
// 5. Go to File -> Export -> Export as STL... to save your 3D model.

/* [Plant Information] */
// Plant's common name
plant_name = "Golden Pothos";
// Scientific name
scientific_name = "Epipremnum aureum";
// Optional nickname (leave blank to skip)
nickname = "";

/* [What to Display] */
// Show plant common name
show_plant_name = true;
// Show scientific name
show_scientific_name = true;
// Show nickname (if provided)
show_nickname = true;
// Show water requirement symbols
show_water_symbols = true;
// Show light requirement symbols
show_light_symbols = true;
// Show cactus "water sparingly" reminder symbol
show_dry_soil_symbol = true;

/* [Plant Care Requirements] */
// Water requirement: 1 = low, 2 = medium, 3 = high, 4 = very high
water_drops = 2; // [1:4]
// Light requirement: 1 = low light, 2 = medium light, 3 = bright light, 4 = full sun
light_type = 2; // [1:4]

/* [Label Size] */
// Width of the label in mm
label_width = 80; // [40:5:150]
// Height of the label in mm
label_height = 30; // [20:5:80]
// Thickness of the label base in mm
label_thickness = 3; // [2:0.5:8]

/* [Text Appearance] */
// Height of the raised text in mm
text_height = 1.5; // [0.5:0.25:4.0]
// Text size multiplier
text_size_multiplier = 1.0; // [0.5:0.1:2.0]

/* [Symbol Appearance] */
// Symbol size multiplier (larger = easier to read when printed)
symbol_size_multiplier = 1.0; // [0.5:0.25:3.0]

/* [Border and Frame] */
// Show raised frame border
show_frame = true;
// Radius for rounded corners
corner_radius = 3; // [0:0.5:10]
// Width of the raised frame border
frame_width = 1.5; // [0.5:0.25:5]
// Height of the raised frame
frame_height = 0.8; // [0.2:0.1:2.0]

/* [Spike for Planting] */
// Enable spike for planting in soil
spike_enabled = true;
// Length of spike in mm
spike_length = 40; // [15:5:80]
// Width of spike at base in mm
spike_width = 6; // [3:0.5:12]
// Spike taper ratio (0.5 = half width at tip)
spike_taper = 0.7; // [0.3:0.1:1.0]
// Position along bottom edge (-1 = left, 0 = center, 1 = right)
spike_position = 0; // [-1:0.1:1]
// Size of triangular gussets at spike base
spike_base_radius = 1.5; // [0:0.25:4]

/* [Hanging Holes] */
// Enable hanging holes in the top corners
enable_hanging_holes = true;
// Diameter of the hanging holes in mm
hole_diameter = 3; // [2:0.5:10]
// Horizontal distance from the edge
hole_margin_x = 4; // [2:0.5:10]
// Vertical distance from the edge
hole_margin_y = 4; // [2:0.5:10]

/* [Advanced Options] */
// Font for text rendering
font_name = "Liberation Sans";

// --- INTERNAL CALCULATIONS (DO NOT MODIFY) ---

// Scaling factors (proportional to label size)
base_width = 80;
base_height = 30;
width_scale = label_width / base_width;
height_scale = label_height / base_height;
avg_scale = (width_scale + height_scale) / 2;

// Scaled dimensions
scaled_corner_radius = corner_radius * avg_scale;
scaled_frame_width = frame_width * avg_scale;
scaled_frame_height = frame_height * avg_scale;
scaled_text_height = text_height * avg_scale;
scaled_spike_length = spike_length * avg_scale;
scaled_spike_width = spike_width * avg_scale;
scaled_spike_thickness = label_thickness;
scaled_spike_gusset_size = spike_base_radius * avg_scale;

// Enhanced symbol settings
base_symbol_size = 4 * avg_scale * symbol_size_multiplier;
symbol_text_height = show_frame ? scaled_frame_height : scaled_text_height; // Match frame height or text height

// Text settings with multiplier
max_font_size_name = 7 * avg_scale * text_size_multiplier;
max_font_size_scientific = 5 * avg_scale * text_size_multiplier;
max_font_size_nickname = 5 * avg_scale * text_size_multiplier;
text_margin = 0.05;

// --- HELPER FUNCTIONS ---

function calc_font_size(text_length, max_font, available_width) = 
    min(max_font, available_width / (text_length * 0.6));

// Module for rounded rectangle
module rounded_cube(width, height, thickness, radius) {
    hull() {
        translate([radius, radius, 0])
            cylinder(h = thickness, r = radius, $fn = 32);
        translate([width - radius, radius, 0])
            cylinder(h = thickness, r = radius, $fn = 32);
        translate([radius, height - radius, 0])
            cylinder(h = thickness, r = radius, $fn = 32);
        translate([width - radius, height - radius, 0])
            cylinder(h = thickness, r = radius, $fn = 32);
    }
}

// Module for raised frame border
module raised_frame(width, height, frame_width, frame_height, corner_radius) {
    difference() {
        rounded_cube(width, height, frame_height, corner_radius);
        translate([frame_width, frame_width, -0.1])
            rounded_cube(width - 2*frame_width, height - 2*frame_width, frame_height + 0.2, corner_radius - frame_width);
    }
}

// Module for spike attachment with triangular gussets
module spike(length, width, thickness, taper_ratio, gusset_size = 0) {
    if (spike_enabled) {
        tip_width = width * taper_ratio;
        
        // Main tapered spike body
        linear_extrude(height = thickness) {
            polygon([
                [-width/2, 0],
                [width/2, 0],
                [tip_width/2, -length],
                [-tip_width/2, -length]
            ]);
        }
        
        // Add triangular gussets at base corners if gusset_size > 0
        if (gusset_size > 0.01) {
            for (side = [-1, 1]) {
                translate([side * width/2, 0, 0]) {
                    scale([side, 1, 1]) {
                        linear_extrude(height = thickness) {
                            polygon([
                                [0, 0],
                                [gusset_size * 1.5, 0],
                                [-gusset_size * 0.5, -gusset_size * 2]
                            ]);
                        }
                    }
                }
            }
        }
    }
}

// Enhanced water drop module - filled version
module water_drop_filled(size) {
    linear_extrude(height = symbol_text_height) {
        // Main teardrop body - completely filled
        hull() {
            // Bottom circle
            circle(r = size/2.5, $fn = 32);
            // Top point
            translate([0, size * 0.6, 0]) {
                circle(r = size/8, $fn = 16);
            }
        }
    }
}

// Enhanced water drop module - outlined version
module water_drop_outlined(size) {
    linear_extrude(height = symbol_text_height) {
        // Main teardrop outline only
        difference() {
            hull() {
                // Bottom circle
                circle(r = size/2.5, $fn = 32);
                // Top point
                translate([0, size * 0.6, 0]) {
                    circle(r = size/8, $fn = 16);
                }
            }
            // Remove inner area, leaving border
            hull() {
                // Bottom circle (smaller)
                circle(r = size/2.5 - 0.8, $fn = 32);
                // Top point (smaller)
                translate([0, size * 0.6, 0]) {
                    circle(r = max(size/8 - 0.4, 0.2), $fn = 16);
                }
            }
        }
    }
}

// Module for 4 water drops with progress bar style filling (left-aligned)
module water_drops(level, size, spacing) {
    if (show_water_symbols) {
        for (i = [0 : 3]) {
            translate([i * spacing, 0, 0]) {
                if (i < level) {
                    water_drop_filled(size);
                } else {
                    water_drop_outlined(size);
                }
            }
        }
    }
}

// Enhanced sun symbol - filled version
module sun_symbol_filled(size) {
    scale(0.7) {
        linear_extrude(height = symbol_text_height) {
            // Center circle
            circle(r = size/3, $fn = 32);
            
            // Sun rays - 8 triangular rays
            for (i = [0 : 7]) {
                rotate([0, 0, i * 45]) {
                    translate([size/2.2, 0, 0]) {
                        polygon([
                            [0, -size/8],
                            [size/3, 0],
                            [0, size/8]
                        ]);
                    }
                }
            }
        }
    }
}

// Enhanced sun symbol - outlined version (rays only, no center circle)
module sun_symbol_outlined(size) {
    scale(0.7) {
        linear_extrude(height = symbol_text_height) {
            // Sun rays outline only - 8 triangular rays (no center circle)
            for (i = [0 : 7]) {
                rotate([0, 0, i * 45]) {
                    translate([size/2.2, 0, 0]) {
                        difference() {
                            polygon([
                                [0, -size/8],
                                [size/3, 0],
                                [0, size/8]
                            ]);
                            // Inner triangle to create outline
                            translate([size/12, 0, 0]) {
                                polygon([
                                    [0, -size/12],
                                    [size/5, 0],
                                    [0, size/12]
                                ]);
                            }
                        }
                    }
                }
            }
        }
    }
}


// Module for 4 light symbols with progress bar style filling (left-to-right)
module light_symbols(level, size, spacing) {
    if (show_light_symbols) {
        for (i = [0 : 3]) {
            translate([i * spacing, 0, 0]) {
                if (i < level) {
                    sun_symbol_filled(size);
                } else {
                    sun_symbol_outlined(size);
                }
            }
        }
    }
}

// Cactus symbol - "water sparingly/when dry" reminder (emoji style)
module cactus_symbol(size) {
    if (show_dry_soil_symbol) {
        linear_extrude(height = symbol_text_height) {
            // Main vertical stem (tall rectangle with rounded ends)
            hull() {
                translate([0, -size/3, 0]) {
                    circle(r = size/8, $fn = 32);
                }
                translate([0, size/3, 0]) {
                    circle(r = size/8, $fn = 32);
                }
            }
            
            // Left arm (curves up from middle-left)
            hull() {
                translate([-size/8, 0, 0]) {
                    circle(r = size/12, $fn = 32);
                }
                translate([-size/3, 0, 0]) {
                    circle(r = size/12, $fn = 32);
                }
                translate([-size/3, size/4, 0]) {
                    circle(r = size/12, $fn = 32);
                }
            }
            
            // Right arm (curves up from middle-right)
            hull() {
                translate([size/8, size/8, 0]) {
                    circle(r = size/12, $fn = 32);
                }
                translate([size/3, size/8, 0]) {
                    circle(r = size/12, $fn = 32);
                }
                translate([size/3, size/3, 0]) {
                    circle(r = size/12, $fn = 32);
                }
            }
        }
    }
}

// Enhanced text module with better base support
module enhanced_text(text_content, font_size, font_style, base_thickness_ratio = 0.3) {
    if (text_content != "" && len(text_content) > 0) {
        // Solid base under the text for better printing
        linear_extrude(height = scaled_text_height * base_thickness_ratio) {
            offset(r = 0.2) {
                text(text_content, 
                     size = font_size, 
                     font = str(font_name, ":", font_style), 
                     halign = "center", 
                     valign = "center"); 
            }
        }
        // Main text on top
        linear_extrude(height = scaled_text_height) {
            text(text_content, 
                 size = font_size, 
                 font = str(font_name, ":", font_style), 
                 halign = "center", 
                 valign = "center"); 
        }
    }
}

// --- MAIN LABEL GENERATION ---
module create_label(common_name, scientific, water_count, light_requirement, plant_nickname = "") {
    // Pre-calculate all dimensions to avoid scope issues
    frame_margin = show_frame ? (scaled_frame_width + 0.5) : 1.5;
    safety_margin = 3 * avg_scale;
    absolute_margin = 1; // 1mm absolute margin from edge/frame
    available_width_full = (label_width - 2 * frame_margin - 2 * safety_margin - 2 * absolute_margin) * (1 - 2 * text_margin);
    
    // Calculate usable area inside frame
    usable_height = label_height - 2 * frame_margin - 2 * absolute_margin;
    usable_top = usable_height / 2;
    usable_bottom = -usable_height / 2;
    
    // Text display flags
    has_nickname = show_nickname && len(str(plant_nickname)) > 0 && str(plant_nickname) != " " && str(plant_nickname) != "";
    display_common_name = show_plant_name && len(common_name) > 0;
    display_scientific = show_scientific_name && len(scientific) > 0;
    display_symbols = show_water_symbols || show_light_symbols || show_dry_soil_symbol;
    
    // Count active elements
    text_count = (has_nickname ? 1 : 0) + (display_common_name ? 1 : 0) + (display_scientific ? 1 : 0);
    total_elements = text_count + (display_symbols ? 1 : 0);
    
    // --- Dynamic Vertical Spacing Logic ---

    // Define vertical padding between elements as a factor of average scale
    vertical_padding = 1.5 * avg_scale;

    // 1. Calculate initial font sizes based on available WIDTH
    name_font_size_w = display_common_name ? calc_font_size(len(common_name), max_font_size_name, available_width_full) : 0;
    scientific_font_size_w = display_scientific ? calc_font_size(len(scientific), max_font_size_scientific, available_width_full) : 0;
    nickname_font_size_w = has_nickname ? calc_font_size(len(str(plant_nickname)), max_font_size_nickname, available_width_full) : 0;

    // 2. Calculate initial element heights from these font sizes
    nickname_h = has_nickname ? nickname_font_size_w * 1.2 : 0;
    name_h = display_common_name ? name_font_size_w * 1.2 : 0;
    scientific_h = display_scientific ? scientific_font_size_w * 1.2 : 0;
    // For symbols, use the base size as an initial height estimate
    symbol_h = display_symbols ? (4 * avg_scale * symbol_size_multiplier) * 0.8 : 0;

    // 3. Sum up initial heights and padding to get the total required vertical space
    total_content_height = nickname_h + name_h + scientific_h + symbol_h;
    total_padding = (total_elements > 1 ? (total_elements - 1) * vertical_padding : 0);
    required_total_height = total_content_height + total_padding;

    // 4. Calculate a scale-down factor if the content overflows the usable height
    height_scale_factor = min(1, usable_height / required_total_height);

    // 5. Apply the scale factor to get the FINAL SIZES for all elements and padding
    nickname_font_size = nickname_font_size_w * height_scale_factor;
    name_font_size = name_font_size_w * height_scale_factor;
    scientific_font_size = scientific_font_size_w * height_scale_factor;
    local_max_symbol_size = (4 * avg_scale * symbol_size_multiplier) * height_scale_factor;
    final_padding = vertical_padding * height_scale_factor;

    // 6. Calculate the FINAL heights of each element
    final_nickname_h = has_nickname ? nickname_font_size * 1.2 : 0;
    final_name_h = display_common_name ? name_font_size * 1.2 : 0;
    final_scientific_h = display_scientific ? scientific_font_size * 1.2 : 0;
    final_symbol_h = display_symbols ? local_max_symbol_size * 0.8 : 0;

    // 7. Calculate the total height of the final, scaled content block
    final_block_height = final_nickname_h + final_name_h + final_scientific_h + final_symbol_h + (total_elements > 1 ? (total_elements - 1) * final_padding : 0);

    // 8. Calculate Y position for each element, laying them out from the top of the now-centered block
    block_top_y = final_block_height / 2;

    nickname_y_offset = final_nickname_h / 2;
    nickname_y = has_nickname ? block_top_y - nickname_y_offset : 0;

    common_name_y_offset = (has_nickname ? final_nickname_h + final_padding : 0) + (final_name_h / 2);
    common_name_y = display_common_name ? block_top_y - common_name_y_offset : 0;

    scientific_y_offset = (has_nickname ? final_nickname_h + final_padding : 0) + (display_common_name ? final_name_h + final_padding : 0) + (final_scientific_h / 2);
    scientific_y = display_scientific ? block_top_y - scientific_y_offset : 0;

    symbol_y_offset = (has_nickname ? final_nickname_h + final_padding : 0) + (display_common_name ? final_name_h + final_padding : 0) + (display_scientific ? final_scientific_h + final_padding : 0) + (final_symbol_h / 2);
    symbol_y_position = display_symbols ? block_top_y - symbol_y_offset : 0;
    
    // Debug output
    echo("=== LABEL SPACING DEBUG ===");
    echo(str("Usable height: ", usable_height, ", Usable top: ", usable_top));
    echo(str("Active elements: ", total_elements));
    if (has_nickname) echo(str("Nickname Y: ", nickname_y));
    if (display_common_name) echo(str("Common name Y: ", common_name_y));
    if (display_scientific) echo(str("Scientific Y: ", scientific_y));
    if (display_symbols) echo(str("Symbol Y: ", symbol_y_position));
    echo("=========================");
    
    // Symbol horizontal positioning
    symbol_offset_from_center = (label_width - 2 * frame_margin) / 3.5;
    safe_symbol_offset = min(symbol_offset_from_center, local_max_symbol_size * 1.8);
    
    // Create the main label body (base + frame) and subtract hanging holes
    difference() {
        union() {
            // Base of the label with rounded corners
            translate([-label_width/2, -label_height/2, 0]) {
                rounded_cube(label_width, label_height, label_thickness, scaled_corner_radius);
            }
            
            // Raised frame border (only if enabled)
            if (show_frame) {
                translate([-label_width/2, -label_height/2, label_thickness]) {
                    raised_frame(label_width, label_height, scaled_frame_width, scaled_frame_height, scaled_corner_radius);
                }
            }
        }
        
        // Add hanging holes if enabled
        if (enable_hanging_holes) {
            total_thickness = label_thickness + (show_frame ? scaled_frame_height : 0);
            hole_x = label_width/2 - hole_margin_x;
            hole_y = label_height/2 - hole_margin_y;
            
            // Left hole
            translate([-hole_x, hole_y, -0.1]) {
                cylinder(h = total_thickness + 0.2, r = hole_diameter/2, $fn=32);
            }
            
            // Right hole
            translate([hole_x, hole_y, -0.1]) {
                cylinder(h = total_thickness + 0.2, r = hole_diameter/2, $fn=32);
            }
        }
    }

    // Text elements (only if enabled)
    if (has_nickname) {
        translate([0, nickname_y, label_thickness]) {
            enhanced_text(str(plant_nickname), nickname_font_size, "style=Bold");
        }
    }

    if (display_common_name) {
        translate([0, common_name_y, label_thickness]) {
            enhanced_text(common_name, name_font_size, "style=Bold");
        }
    }

    if (display_scientific) {
        translate([0, scientific_y, label_thickness]) {
            enhanced_text(scientific, scientific_font_size, "style=Italic");
        }
    }

    // Symbols with proper spacing (only if symbols are enabled)
    if (display_symbols) {
        symbol_spacing = local_max_symbol_size * 1.4;
        
        // Water drops (left edge) - only if water symbols are enabled
        if (show_water_symbols) {
            // Position at left edge with margin from frame
            water_left_x = -label_width/2 + frame_margin + absolute_margin + local_max_symbol_size/2;
            // Adjust Y position so bottom of water drop aligns with bottom of sun
            water_y_offset = -local_max_symbol_size * 0.3; // Move down to align bottoms
            translate([water_left_x, symbol_y_position + water_y_offset, label_thickness]) {
                water_drops(water_count, local_max_symbol_size, symbol_spacing);
            }
        }

        // Light symbols (right edge) - only if light symbols are enabled
        if (show_light_symbols) {
            // Position at right edge with margin from frame, accounting for 4 symbols
            sun_right_x = label_width/2 - frame_margin - absolute_margin - (3 * symbol_spacing + local_max_symbol_size/2);
            translate([sun_right_x, symbol_y_position, label_thickness]) {
                light_symbols(light_requirement, local_max_symbol_size, symbol_spacing);
            }
        }
    }
    
    // Cactus symbol (center) - "water sparingly/when dry" reminder (independent of other symbols)
    if (show_dry_soil_symbol) {
        translate([0, symbol_y_position, label_thickness]) {
            cactus_symbol(local_max_symbol_size);
        }
    }
    
    // Add spike if enabled
    if (spike_enabled) {
        spike_x = spike_position * (label_width/2 - scaled_spike_width/2 - scaled_corner_radius);
        translate([spike_x, -label_height/2, 0]) {
            spike(scaled_spike_length, scaled_spike_width, scaled_spike_thickness, spike_taper, scaled_spike_gusset_size);
        }
    }
}

// Generate the label
create_label(plant_name, scientific_name, water_drops, light_type, nickname);