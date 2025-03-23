import argparse
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config

parser = argparse.ArgumentParser()
parser.add_argument("--dxf")
file = parser.parse_args().dxf

doc = ezdxf.readfile(file)

msp = doc.modelspace()

context = RenderContext(doc)
backend = svg.SVGBackend()

cfg = config.Configuration(
	background_policy=config.BackgroundPolicy.WHITE,
	color_policy=config.ColorPolicy.BLACK
)

frontend = Frontend(context, backend, config=cfg)

frontend.draw_layout(msp)

page = layout.Page( 0, 0, layout.Units.mm, margins=layout.Margins.all(10) )

svg_string = backend.get_string(page)

print("svg_string")

with open("image.svg", "wt", encoding="utf8") as fp:
    fp.write(svg_string)
