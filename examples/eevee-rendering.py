"""Render color and metric depth with Blender Eevee.

Run with ``make eevee-rendering``.
"""

from blendgen.passes.base import ImageOutputType
from blendgen.passes.color import ColorPass
from blendgen.passes.depth import DepthPass
from blendgen.renderer import Renderer
from blendgen.renderers import EeveeBackend
from blendgen.session import Session


renderer = Renderer(
    backend=EeveeBackend(samples=16),
    resolution_x=1920,
    resolution_y=1080,
    resolution_percentage=100,
    passes=[
        ColorPass(prefix="color"),
        DepthPass(prefix="depth", output_type=ImageOutputType.EXR),
    ],
)

session = Session(renderer=renderer, frame_length=1)
print(session.info)
session.run()
