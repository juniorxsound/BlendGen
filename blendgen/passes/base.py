"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
from enum import Enum


class ImageOutputType(Enum):
    """
    An enum to change output file type of a given pass in a session
    @todo Add FFMPEG video and npy binary options to BlendGen
    """
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    EXR = "OPEN_EXR"


class BaseRenderPass(object):
    def __init__(self, prefix=None, output_type=None):
        if prefix is None:
            raise ValueError("Must provide a prefix value")

        if output_type is None:
            raise ValueError("Must select an output type")

        self.__prefix = prefix
        self.__output_type = output_type
        self.output_node = None
        self.__scene = None
        self.__linker = None
        self.__node_manager = None
        self.__base_path = None
        self.__background = None
        self.__ops = []

    def init(self, scene, base_path, background):
        self.__scene = scene
        self.__linker = scene.node_tree.links
        self.__node_manager = scene.node_tree.nodes
        self.__base_path = base_path
        self.__background = background

    def map(self, min=0, max=255, size=0.08):
        # Create a map node
        range_mapper = self.node_manager.new(type="CompositorNodeMapValue")

        # Set all the mapper props
        range_mapper.size = [size]
        range_mapper.use_min = True
        range_mapper.min = [min]
        range_mapper.use_max = True
        range_mapper.max = [max]

        # Save the op so we can connect it
        self.__ops.append((range_mapper.inputs[0], range_mapper.outputs[0]))

    def invert(self):
        # Create an invert node
        invert = self.node_manager.new(type="CompositorNodeInvert")

        # Save the op so we can connect it
        self.__ops.append((invert.inputs[1], invert.outputs[0]))

    def id_mask(self, index, rgb):
        # Create the ID mask op
        id_mask = self.node_manager.new(type="CompositorNodeIDMask")

        # We always want to antialias the segmentation mask
        id_mask.use_antialiasing = True

        # Set the material index
        id_mask.index = index

        if rgb:
            """
            Weird naming convention here since it doesn't match the
            Blender UI but CompositorNodeMixRGB is the Add node
            """
            multiplier = self.node_manager.new(type="CompositorNodeMixRGB")
            multiplier.blend_type = "MULTIPLY"
            
            # Split the user provided rgb list - @todo add data validation
            r, g, b = rgb

            # Create RGB value in the graph
            rgb = self.node_manager.new(type="CompositorNodeRGB")
            
            # We only let you assign the R, G, B values, maybe in the future support alpha too?
            rgb.outputs[0].default_value = r, g, b, 1.0

            # Connect the id mask to both factor and the first image and the color outputs to the 2nd image
            self.__connect(id_mask.outputs[0], multiplier.inputs[0])
            self.__connect(id_mask.outputs[0], multiplier.inputs[1])
            self.__connect(rgb.outputs[0], multiplier.inputs[2])

            # Return the connection between the CompositorNodeIDMask's inputs and the multiplier's outputs
            return self.__ops.append((id_mask.inputs[0], multiplier.outputs[0]))


        # Otherwise just conncet the id_mask which would return a boolean image (i.e b&w)
        self.__ops.append((id_mask.inputs[0], id_mask.outputs[0]))

    def output(self):
        # Set the output node
        self.output_node = self.node_manager.new(
            type="CompositorNodeOutputFile")
        self.output_node.base_path = self.base_path + self.prefix
        self.output_node.format.file_format = self.output_type.value

        self.__ops.append((
            self.output_node.inputs[0],
            None
        ))

    def connect_nodes(self, layer_input):
        # If we have no ops just connect it - input to the output
        if len(self.__ops) == 0:
            self.connect(layer_input,
                         self.output_node.inputs[0])
        else:

            # First layer is set here
            last_output = layer_input

            # Iterate over all ops and get input and output
            for i, (input_op, output_op) in enumerate(self.__ops):
                # Link it
                self.__connect(
                    last_output,
                    input_op
                )

                # Store thre last output as input for the next node
                last_output = output_op

    def __connect(self, input_op, output_op):
        if output_op is not None:
            self.linker.new(input_op, output_op)

    @property
    def render_path(self):
        return self.base_path + self.prefix

    @property
    def ops(self):
        return self.__ops

    @property
    def linker(self):
        return self.__linker

    @property
    def node_manager(self):
        return self.__node_manager

    @property
    def prefix(self):
        return self.__prefix

    @property
    def base_path(self):
        return self.__base_path

    @property
    def output_type(self):
        return self.__output_type

    @property
    def file_extension(self):
        if self.__output_type is ImageOutputType.EXR:
            return '.exr'
        return '.{}'.format(self.__output_type.value.lower())

    @property
    def type(self):
        return type(self).__name__
