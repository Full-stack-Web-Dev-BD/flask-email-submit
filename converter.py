import ezdxf
import svgwrite

def dxf_to_svg(dxf_path, svg_path):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    dwg = svgwrite.Drawing(svg_path)

    for entity in msp:
        if entity.dxftype() == "LINE":
            dwg.add(dwg.line(start=entity.dxf.start, end=entity.dxf.end, stroke="black"))

        elif entity.dxftype() == "CIRCLE":
            dwg.add(dwg.circle(center=entity.dxf.center, r=entity.dxf.radius, stroke="black", fill="none"))

        elif entity.dxftype() == "LWPOLYLINE":
            points = [(p[0], p[1]) for p in entity.get_points()]
            dwg.add(dwg.polyline(points, stroke="black", fill="none"))

    dwg.save()

# Example usage
dxf_to_svg("x.dxf", "output.svg")
