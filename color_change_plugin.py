#!/usr/bin/env python3
import argparse
import math
import re
import logging
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Prusa Slicer Color Change Plugin\n"
                    "Injects a color change command (default: M600) based on filament weight usage."
    )
    parser.add_argument('--input', required=True, help="Input G-code file path")
    parser.add_argument('--output', required=True, help="Output G-code file path")
    parser.add_argument('--spool_weight', type=float, default=None,
                        help="Filament spool weight in grams (e.g., 1000). "
                             "If not provided, the script will try to read it from the G-code header.")
    parser.add_argument('--filament_diameter', type=float, default=1.75,
                        help="Filament diameter in mm (default: 1.75)")
    parser.add_argument('--filament_density', type=float, default=1.25,
                        help="Filament density in g/cm^3 (default: 1.25)")
    parser.add_argument('--extrusion_mode', choices=['relative', 'absolute'], default='relative',
                        help="Extrusion mode: 'relative' or 'absolute' (default: relative)")
    parser.add_argument('--color_change_command', default='M600',
                        help="G-code command to trigger a color change (default: M600)")
    parser.add_argument('--safety_margin', type=float, default=0.03,
                        help="Fraction of spool weight to leave unused (default: 0.03, i.e. trigger at 97% usage)")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging output")
    parser.add_argument('--debug_interval', type=int, default=100,
                        help="Interval for debug log messages (default: 100 lines)")
    return parser.parse_args()

def setup_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    if debug:
        logging.debug("Debug mode enabled.")

def extract_extrusion_value(line):
    match = re.search(r'(?<=\sE)(-?\d+\.?\d*)', line)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0
    return 0.0

def extract_spool_weight_from_header(lines):
    for line in lines:
        if "spool weight" in line.lower():
            match = re.search(r'(\d+(\.\d+)?)', line)
            if match:
                weight = float(match.group(1))
                if 'kg' in line.lower():
                    weight *= 1000  # Convert kg to grams.
                logging.debug("Extracted spool weight: %sg from line: %s", weight, line.strip())
                return weight
    logging.debug("No spool weight found in header.")
    return None

def process_gcode(lines, spool_weight, conversion_factor, extrusion_mode, color_change_command, safety_margin, debug, debug_interval):
    new_lines = []
    cumulative_weight = 0.0
    trigger_weight = spool_weight * (1 - safety_margin)
    last_extrusion = 0.0  # Used for absolute mode

    for idx, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("G92") and "E" in stripped_line:
            e_value = extract_extrusion_value(stripped_line)
            last_extrusion = e_value
            logging.debug("G92 command at line %d: resetting last_extrusion to %.4f", idx, e_value)
            new_lines.append(line.rstrip('\n'))
            continue

        if stripped_line.startswith("G1") and "E" in stripped_line:
            e_value = extract_extrusion_value(stripped_line)
            extrusion_delta = 0.0
            if extrusion_mode == 'relative':
                extrusion_delta = e_value
            else:
                extrusion_delta = e_value - last_extrusion
                last_extrusion = e_value

            if extrusion_delta > 0:
                weight_delta = extrusion_delta * conversion_factor
                cumulative_weight += weight_delta

                if debug and (idx % debug_interval == 0):
                    logging.debug("Line %d: Extrusion delta: %.4f mm, Weight delta: %.6fg, Cumulative weight: %.2fg",
                                  idx, extrusion_delta, weight_delta, cumulative_weight)

                while cumulative_weight >= trigger_weight:
                    logging.debug("Inserting color change command at cumulative weight: %.2fg (Threshold: %.2fg)",
                                  cumulative_weight, trigger_weight)
                    new_lines.append(f"{color_change_command} ; Color change triggered after ~{trigger_weight:.2f}g used")
                    cumulative_weight -= trigger_weight

        new_lines.append(line.rstrip('\n'))
    if debug:
        logging.debug("Final cumulative weight: %.2fg", cumulative_weight)
    return new_lines

def main():
    try:
        args = parse_arguments()
        setup_logging(args.debug)

        with open(args.input, 'r') as f:
            lines = f.readlines()

        spool_weight = args.spool_weight
        if spool_weight is None:
            spool_weight = extract_spool_weight_from_header(lines)
            if spool_weight is None:
                logging.error("Spool weight not provided and not found in G-code header. Please supply --spool_weight.")
                sys.exit(2)

        area = math.pi * (args.filament_diameter / 2) ** 2
        conversion_factor = (area * args.filament_density) / 1000.0
        logging.debug("Calculated filament area: %.6f mm², Conversion factor: %.6f g/mm", area, conversion_factor)

        processed_lines = process_gcode(
            lines,
            spool_weight=spool_weight,
            conversion_factor=conversion_factor,
            extrusion_mode=args.extrusion_mode,
            color_change_command=args.color_change_command,
            safety_margin=args.safety_margin,
            debug=args.debug,
            debug_interval=args.debug_interval
        )

        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, 'w') as f:
            for line in processed_lines:
                f.write(line + "\n")

        logging.info("Processed G-code has been saved to %s", args.output)
    except Exception as e:
        logging.error("An error occurred: %s", e)
        sys.exit(2)

if __name__ == '__main__':
    main()
