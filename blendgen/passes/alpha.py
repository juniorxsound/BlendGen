"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType


class AlphaPass(BaseRenderPass):
    def __init__(self,
                 prefix="",
                 output_type=ImageOutputType.PNG):
        super().__init__(prefix, output_type)
    def create_pass(self, render_layers):
        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(render_layers.outputs["Alpha"])
