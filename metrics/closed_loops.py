# Cloosed loops count calculation
from ezdxf.entities import Line, LWPolyline, Spline, Circle, Arc

loops = 0


def closed_loops():
	return loops


def reset_loop():
    global loops
    loops = 0


def increase_closed_loops(count = 1):
	global loops
	loops += count
	# print(f"[Closed loops:] {loops}")


def calc_closed_loops_line(shape):
	increase_closed_loops(0)
	

def calc_closed_loops_polyline(shape):
	increase_closed_loops(1 if shape.is_closed else 0)


def calc_closed_loops_spline(shape):
	increase_closed_loops(1 if shape.closed else 0)


def calc_closed_loops_circle(shape):
	increase_closed_loops()


def calc_closed_loops_arc(shape):
	increase_closed_loops(0)



def calc_closed_loops_insert(shape):
	increase_closed_loops()

