import ezdxf
# Workpiece surface area calculation

from ezdxf.math import ConstructionPolyline

surface_edges = {
	'x_min': None,
	'x_max': None,
	'y_min': None,
	'y_max': None
}

area = 0
a = 0
b = 0


def reset_surface_values():
    global area, a, b, surface_edges
    area = 0
    a = 0
    b = 0
    surface_edges = {
        'x_min': None,
        'x_max': None,
        'y_min': None,
        'y_max': None
    }


def surface_area():
	if not None in surface_edges.values():
		calc_surface_area()
	return area


def dimensions():
	return a, b


def calc_surface_area():
	global area
	global a
	global b

	a = surface_edges['x_max'] - surface_edges['x_min']
	b = surface_edges['y_max'] - surface_edges['y_min']
	area = a * b
	# area = (surface_edges['x_max'] - surface_edges['x_min']) * (surface_edges['y_max'] - surface_edges['y_min'])


def determine_most_extreme_points(points):
	global surface_edges

	first_shape = None in surface_edges.values()

	surface_edges = {
		'x_min': min(points['x']) if first_shape else min( surface_edges['x_min'], min(points['x']) ),
		'x_max': max(points['x']) if first_shape else max( surface_edges['x_max'], max(points['x']) ),
		'y_min': min(points['y']) if first_shape else min( surface_edges['y_min'], min(points['y']) ),
		'y_max': max(points['y']) if first_shape else max( surface_edges['y_max'], max(points['y']) ),
	}

	#print('[Most extreme points:]', surface_edges)


def calc_extreme_points_line(shape):
	points = {
		'x': [shape.dxf.start.x, shape.dxf.end.x],
		'y': [shape.dxf.start.y, shape.dxf.end.y]
	}
	#print(shape, points)
	determine_most_extreme_points(points)


def calc_extreme_points_polyline(shape):
	points = {
		'x': [],
		'y': []
	}
	for pnt in shape.points():
		points['x'].append(pnt.x)
		points['y'].append(pnt.y)

	#print(shape, points)
	determine_most_extreme_points(points)
	

def calc_extreme_points_spline(shape):
	points = {
		'x': [],
		'y': []
	}
	approx_curve = shape.flattening(0.1)
	polyline = ConstructionPolyline(vertices = approx_curve, close = shape.closed)
	for pnt in polyline:
		points['x'].append(pnt.x)
		points['y'].append(pnt.y)

	#print(shape, shape.closed, points)
	determine_most_extreme_points(points)


def calc_extreme_points_circle(shape):
	points ={
		'x': [shape.dxf.center.x - shape.dxf.radius, shape.dxf.center.x + shape.dxf.radius],
		'y': [shape.dxf.center.y - shape.dxf.radius, shape.dxf.center.y + shape.dxf.radius]
	}
	#print(shape, shape.dxf.center, shape.dxf.radius, points)
	determine_most_extreme_points(points)


def calc_extreme_points_arc(shape):
	#print(shape)
	points ={
		'x': [],
		'y': []
	}
	spline = shape.to_spline()
	#print('spline', spline)
	approx_curve = spline.flattening(0.01)
	polyline = ConstructionPolyline(vertices = approx_curve, close = spline.closed)
	for pnt in polyline:
		points['x'].append(pnt.x)
		points['y'].append(pnt.y)

	#print( points)
	determine_most_extreme_points(points)

def calc_extreme_points_insert(shape):
    """
    Handles the 'INSERT' type DXF entities for calculating surface area.
    This function calculates the extreme points of the inserted block
    by accessing the block reference name and its entities directly.
    It works similarly to other shape handling functions.
    """
    block_name = shape.dxf.name  # Block name from INSERT entity
    block = shape.doc.blocks.get(block_name)  # Get the block object using its name from the shape's doc

    points = {
        'x': [],
        'y': []
    }

    # Loop through all entities in the block and collect points
    for entity in block:
        if isinstance(entity, ezdxf.entities.Line):
            points['x'].extend([entity.dxf.start.x, entity.dxf.end.x])
            points['y'].extend([entity.dxf.start.y, entity.dxf.end.y])
        elif isinstance(entity, ezdxf.entities.LWPolyline):
            for pnt in entity.points():
                points['x'].append(pnt[0])
                points['y'].append(pnt[1])
        elif isinstance(entity, ezdxf.entities.Spline):
            approx_curve = entity.flattening(0.1)
            polyline = ConstructionPolyline(vertices=approx_curve, close=entity.closed)
            for pnt in polyline:
                points['x'].append(pnt.x)
                points['y'].append(pnt.y)
        elif isinstance(entity, ezdxf.entities.Circle):
            points['x'].extend([entity.dxf.center.x - entity.dxf.radius, entity.dxf.center.x + entity.dxf.radius])
            points['y'].extend([entity.dxf.center.y - entity.dxf.radius, entity.dxf.center.y + entity.dxf.radius])
        elif isinstance(entity, ezdxf.entities.Arc):
            spline = entity.to_spline()
            approx_curve = spline.flattening(0.01)
            polyline = ConstructionPolyline(vertices=approx_curve, close=spline.closed)
            for pnt in polyline:
                points['x'].append(pnt.x)
                points['y'].append(pnt.y)

    # Calculate the extreme points based on the collected points
    determine_most_extreme_points(points)
