"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
from enum import Enum

from blendgen.compositor import compositor_tree, create_output_node
from blendgen.passes import operations
from blendgen.renderers.base import RenderPassKind


class ImageOutputType(Enum):
    """
    An enum to change output file type of a given pass in a session
    @todo Add FFMPEG video and npy binary options to BlendGen
    """
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    EXR = "OPEN_EXR"


class BaseRenderPass:
    kind = None
    def __init__(self, prefix=None, output_type=None, display_transform=False):
        if prefix is None:
            raise ValueError("Must provide a prefix value")

        if output_type is None:
            raise ValueError("Must select an output type")

        self.__prefix = prefix
        self.__output_type = output_type
        self.__display_transform = display_transform
        self.output_node = None
        self.__scene = None
        self.__linker = None
        self.__node_manager = None
        self.__base_path = None
        self.__background = None
        self.__operations = []

    def init(self, scene, base_path, background):
        self.__scene = scene
        node_tree = compositor_tree(scene)
        self.__linker = node_tree.links
        self.__node_manager = node_tree.nodes
        self.__base_path = base_path
        self.__background = background

    def add_map_value(self, minimum=0, maximum=255, size=0.08):
        """Add a clamped Map Value compositor operation."""
        self.__operations.append(operations.map_value(
            self.node_manager, minimum, maximum, size))

    def add_invert(self):
        """Add an image invert compositor operation."""
        self.__operations.append(operations.invert(self.node_manager))

    def add_material_index_mask(self, index, color=None):
        """Add a material-index mask, optionally colored with RGB values."""
        self.__operations.append(operations.material_index_mask(
            self.node_manager, self.linker, index, color))

    def output(self):
        """Create this pass's File Output node."""
        self.output_node = create_output_node(
            self.node_manager, self.render_path, self.output_type)
        self.__operations.append(operations.OperationSockets(
            self.output_node.inputs[0], None))

    def connect_nodes(self, layer_input):
        # If we have no ops just connect it - input to the output
        if not self.__operations:
            self.connect(layer_input,
                         self.output_node.inputs[0])
        else:

            # First layer is set here
            last_output = layer_input

            # Iterate over all ops and get input and output
            for operation in self.__operations:
                self.__connect(last_output, operation.input_socket)
                last_output = operation.output_socket

    def create_pass(self, source_socket):
        """Build this pass from a backend-resolved compositor socket."""
        self.output()
        self.connect_nodes(source_socket)

    def __connect(self, input_op, output_op):
        if output_op is not None:
            self.linker.new(input_op, output_op)

    @property
    def render_path(self):
        return self.base_path + self.prefix

    @property
    def ops(self):
        return self.__operations

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

    @property
    def display_transform(self):
        """Whether non-EXR output should be converted to sRGB for display."""
        return self.__display_transform
