# app/calc/dxf/dxfparser.py
import os
import json
from datetime import datetime
import ezdxf

from metrics.path_length import *
from metrics.surface_area import *
from metrics.closed_loops import *

# List of supported DXF entity types
shapes = ('LINE', 'ARC', 'CIRCLE', 'SPLINE', 'POLYLINE', 'INSERT')

# Mapping of action + entity type to the appropriate function
methods = {
    'total_path_length_LINE': calc_length_line,
    'total_path_length_SPLINE': calc_length_spline,
    'total_path_length_POLYLINE': calc_length_polyline,
    'total_path_length_CIRCLE': calc_length_circle,
    'total_path_length_ARC': calc_length_arc,
    'total_path_length_INSERT': calc_length_insert,

    'surface_area_LINE': calc_extreme_points_line,
    'surface_area_SPLINE': calc_extreme_points_spline,
    'surface_area_POLYLINE': calc_extreme_points_polyline,
    'surface_area_CIRCLE': calc_extreme_points_circle,
    'surface_area_ARC': calc_extreme_points_arc,
    'surface_area_INSERT': calc_extreme_points_insert,

    'closed_loops_LINE': calc_closed_loops_line,
    'closed_loops_SPLINE': calc_closed_loops_spline,
    'closed_loops_POLYLINE': calc_closed_loops_polyline,
    'closed_loops_CIRCLE': calc_closed_loops_circle,
    'closed_loops_ARC': calc_closed_loops_arc,
    'closed_loops_INSERT': calc_closed_loops_insert
}

def process_dxf_file(dxf_file):
    """
    Process the given DXF file and return calculated metrics.
    """
    # Read the DXF file
    doc = ezdxf.readfile(dxf_file)

    def check_entity_type(kind):
        if kind in shapes:
            return True
        else:
            # msg = f'Unknown entity type - {kind}'
            # msg = f'Unknown entity type - {datetime.now()}\n\tName: {kind}\n\tFile: {dxf_file}\n\n'
            # print(msg)
            return False

    def perform_calculation(action):
        shp = 0
        for shape in doc.entities:
            if not check_entity_type(shape.dxftype()):
                print("Shape  is unknown ", shape)
                continue
            ref = action + '_' + shape.dxftype()
            methods[ref](shape)
            shp += 1
        print(f'Shapes total for {action}: {shp}')
        return shp

    # Run the calculations
    perform_calculation('total_path_length')
    perform_calculation('surface_area')
    perform_calculation('closed_loops')

    output = {
        'cutting_line': total_path_length(),
        'surface_area': surface_area(),
        'dimensions': dimensions(),
        'closed_loops': closed_loops()
    }
    reset_total_length()
    reset_surface_values()
    reset_loop()
    
    # print("dxf output>>>>", output)
    return output
