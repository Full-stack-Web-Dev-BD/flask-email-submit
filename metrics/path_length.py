# Total cutting path length calculation

import math
from ezdxf.math import ConstructionPolyline


total_length = 0

def reset_total_length():
    global total_length
    total_length = 0

def total_path_length():
	return total_length


def increase_path_length(length):
	global total_length
	total_length += length
	# print(f"[Total path length:] {total_length}")


def calc_length_line(shape):
	length = shape.dxf.start.distance(shape.dxf.end)
	# print(shape, length, shape.dxf.start, shape.dxf.end)
	increase_path_length(length)


def calc_length_polyline(shape):
	# print(shape, shape.is_closed)
	points = [point for point in shape.points()]
	poly_length = 0
	for indx, point in enumerate(points):
		if not shape.is_closed and indx == 0:
			# print(indx, point)
			continue
		else:
			length = point.distance(points[indx - 1])
			poly_length += length
		# print(indx, point, length, poly_length)

	increase_path_length(poly_length)


def calc_length_spline(shape):
	approx_curve = shape.flattening( 0.1 )
	polyline = ConstructionPolyline(vertices = approx_curve, close = shape.closed)
	spline_length = polyline.length
	# print(shape, shape.closed, spline_length)
	increase_path_length(spline_length)


def calc_length_circle(shape):
	circumference = 2 * math.pi * shape.dxf.radius
	# print(shape, circumference, shape.dxf.center, shape.dxf.radius)
	increase_path_length(circumference)


def calc_length_arc(shape):
	if shape.dxf.start_angle > shape.dxf.end_angle:
		alfa = 360 - shape.dxf.start_angle + shape.dxf.end_angle
	else:
		alfa = shape.dxf.end_angle - shape.dxf.start_angle
	arc_length = math.pi * shape.dxf.radius * alfa / 180
	# print(shape, arc_length, shape.dxf.center, shape.dxf.radius, shape.dxf.start_angle, shape.dxf.end_angle)
	increase_path_length(arc_length)


def calc_length_insert(shape):
    # Get the block reference name from the shape
    block_name = shape.dxf.name  # The block name of the INSERT entity

    # Retrieve the block definition using the block name
    block_definition = shape.doc.blocks.get(block_name)

    # Iterate through each entity in the block definition
    for entity in block_definition:
        # Print the entity type
        print(f"Processing entity type: {entity.dxftype()}")

        # Check the entity type and call the respective length calculation function
        if entity.dxftype() == 'LINE':
            calc_length_line(entity)
        elif entity.dxftype() == 'LWPOLYLINE' or entity.dxftype() == 'POLYLINE':
            calc_length_polyline(entity)
        elif entity.dxftype() == 'SPLINE':
            calc_length_spline(entity)
        elif entity.dxftype() == 'CIRCLE':
            calc_length_circle(entity)
        elif entity.dxftype() == 'ARC':
            calc_length_arc(entity)

    # The total length will be updated in the global variable `total_length`
