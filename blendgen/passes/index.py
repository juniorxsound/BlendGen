"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType
from blendgen.renderers.base import RenderPassKind


class MaterialIndexPass(BaseRenderPass):
    kind = RenderPassKind.MATERIAL_INDEX
    def __init__(self,
                 prefix="",
                 index=0,
                 output_type=ImageOutputType.PNG,
                 rgb=None):
        super().__init__(prefix, output_type)
        self.__index = index
        self.__rgb = rgb

    def create_pass(self, source_socket):
        # Create the id mask based on the index
        self.add_material_index_mask(self.__index, self.__rgb)

        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(source_socket)


class RawMaterialIndexPass(BaseRenderPass):
    """Write Blender's unmodified per-pixel material index pass."""

    kind = RenderPassKind.MATERIAL_INDEX

    def __init__(self, prefix="", output_type=ImageOutputType.EXR):
        super().__init__(prefix, output_type)
