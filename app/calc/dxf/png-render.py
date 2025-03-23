import argparse
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout, config

parser = argparse.ArgumentParser()
parser.add_argument("--dxf")
file = parser.parse_args().dxf

doc = ezdxf.readfile(file)
msp = doc.modelspace()

context = RenderContext(doc)
backend = pymupdf.PyMuPdfBackend()

cfg = config.Configuration(
	background_policy=config.BackgroundPolicy.WHITE,
	color_policy=config.ColorPolicy.BLACK
)
frontend = Frontend(context, backend, config=cfg)
frontend.draw_layout(msp)

page = layout.Page( 0, 0, layout.Units.mm, margins=layout.Margins.all(10) )

png = backend.get_pixmap_bytes(page, fmt="png", dpi=96)

file =  file.replace('laser_uploads', 'laser_uploads/_tmp')  +  '.png'

with open (file, "wb") as fp:
	fp.write(png)

print(file)
