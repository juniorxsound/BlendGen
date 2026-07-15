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
        self.__index = index
        self.__rgb = rgb

    def create_pass(self, render_layers):
        # Create the id mask based on the index
        self.add_material_index_mask(self.__index, self.__rgb)

        # Create the output node
        self.output()

        # Connect all the nodes
        material_index = (render_layers.outputs.get("IndexMA")
                          or render_layers.outputs["Material Index"])
        self.connect_nodes(material_index)
