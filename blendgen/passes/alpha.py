"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType
from blendgen.renderers.base import RenderPassKind


class AlphaPass(BaseRenderPass):
    kind = RenderPassKind.ALPHA
    def __init__(self,
                 prefix="",
                 output_type=ImageOutputType.PNG):
        super().__init__(prefix, output_type)
