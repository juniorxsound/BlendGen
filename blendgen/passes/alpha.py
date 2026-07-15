"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType


class AlphaPass(BaseRenderPass):
    def __init__(self,
                 prefix="",
                 output_type=ImageOutputType.PNG):
        super().__init__(prefix, output_type)
        self.__output_type = output_type

    def init(self, scene, base_path, background):
        super().init(scene, base_path, background)

    def create_pass(self, input):
        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(input.outputs[1])
