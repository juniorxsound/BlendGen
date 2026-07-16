"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType
from blendgen.renderers.base import RenderPassKind


class DepthPass(BaseRenderPass):
    kind = RenderPassKind.DEPTH
    def __init__(self,
                 prefix="",
                 map_values=False,
                 minimum=0,
                 maximum=255,
                 invert_values=False,
                 size=0.08,
                 output_type=ImageOutputType.PNG):
        super().__init__(prefix, output_type)
        self.__minimum = minimum
        self.__maximum = maximum
        self.__invert_values = invert_values
        self.__map_values = map_values
        self.__size = size

    def create_pass(self, source_socket):

        # Create range mapper node
        if self.__map_values:
            self.add_map_value(minimum=self.__minimum,
                               maximum=self.__maximum,
                               size=self.__size)

        # Create an invert node
        if self.__invert_values:
            self.add_invert()

        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(source_socket)
