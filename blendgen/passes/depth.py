"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType


class DepthPass(BaseRenderPass):
    def __init__(self,
                 prefix="",
                 map=False,
                 min=0,
                 max=255,
                 invert=False,
                 size=0.08,
                 output_type=ImageOutputType.PNG):
        super().__init__(prefix, output_type)
        self.__min = min
        self.__max = max
        self.__invert = invert
        self.___map = map
        self.__output_type = output_type
        self.__size = size

    def init(self, scene, base_path, background):
        super().init(scene, base_path, background)

    def create_pass(self, input):

        # Create range mapper node
        if self.___map is True:
            self.map(min=self.__min,
                     max=self.__max,
                     size=self.__size)

        # Create an invert node
        if self.__invert is True:
            self.invert()

        # Create the output node
        self.output()

        # Connect all the nodes
        self.connect_nodes(input.outputs[2])
