"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType


class MaterialIndexPass(BaseRenderPass):
    def __init__(self,
                 prefix="",
                 index=0,
                 output_type=ImageOutputType.PNG,
                 rgb=None):
        super().__init__(prefix, output_type)
        self.__output_type = output_type
        self.__index = index
        self.__rgb = rgb

    def init(self, scene, base_path, background):
        super().init(scene, base_path, background)

    def create_pass(self, input):
        # Create the id mask based on the index
        self.id_mask(self.__index, self.__rgb)

        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(input.outputs[15])
