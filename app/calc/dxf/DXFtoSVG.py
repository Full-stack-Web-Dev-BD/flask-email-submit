import os
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config

def convert_dxf_to_svg(filename):
    folder_path = "uploads/calc"
    dxf_path = os.path.join(folder_path, filename)
    
    if not os.path.exists(dxf_path):
        raise FileNotFoundError(f"DXF file not found: {dxf_path}")
    
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    context = RenderContext(doc)
    backend = svg.SVGBackend()

    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.BLACK
    )

    frontend = Frontend(context, backend, config=cfg)
    frontend.draw_layout(msp)

    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(10))
    svg_string = backend.get_string(page)

    svg_filename = filename.replace(".dxf", ".svg")
    svg_path = os.path.join(folder_path, svg_filename)

    with open(svg_path, "w", encoding="utf8") as svg_file:
        svg_file.write(svg_string)

    return svg_path  # Return the saved SVG file path

# Example usage
# svg_file = convert_dxf_to_svg("example.dxf")
# print(f"SVG file saved at: {svg_file}")
