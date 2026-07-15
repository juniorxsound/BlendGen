"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
from os import getenv
from enum import Enum
import bpy  # pylint: disable=import-error


class Background(Enum):
    """An enum to define the background of a rendered scene"""
    alpha = "TRANSPARENT"
    sky = "SKY"


class RendererType(Enum):
    """An enum to globally define renderer type"""
    cycles = "CYCLES"


class Renderer(object):
    """A renderer wrapper class used for rendering different passes"""

    def __init__(self,
                 renderer_type=RendererType.cycles,
                 background=Background.alpha,
                 use_full_sample=True,
                 samples=2,
                 resolution_percentage=100,
                 resolution_x=1920,
                 resolution_y=1080,
                 hardware_acceleration=getenv("HW"),
                 output_base_path="data/toy_dataset/",
                 passes=None,
                 render_images=True):
        """Creates a renderer wrapper class used for a rendering passes

        Keyword Arguments:
            renderer_type {RendererType} -- The type of Blender \
                rendering backend (default: {RendererType.cycles})
            background {Background} -- The type of background \
                for color rendering (default: {Background.alpha})
            use_full_sample {bool} -- Wheter we are \
                rendering full samples (default: {True})
            samples {int} -- Rendering samples used \
                for ray tracing (default: {2})
            resolution_percentage {int} -- Percentage of the \
                resolution used for rendering (default: {100})
            resolution_x {int} -- Width in pixels (default: {1920})
            resolution_y {int} -- Height in pixels (default: {1080})
            hardware_acceleration {str} -- Type of hardware \
                acceleration (default: {getenv("HW")})
            output_base_path {str} -- The base path for \
                the dataset (default: {"data/toy_dataset/"})
            passes {list} -- List of rendering passes (default: {None})
            render_images {bool} -- Should the session render images or not (default: {True})
        """

        print("[BlendGen] Starting renderer with {} acceleration"
              .format(hardware_acceleration))

        # Save paths
        self.__output_base_path = output_base_path

        # Store a list of all the cameras in the scene
        self.__active_scene = bpy.context.scene
        self.__active_camera = bpy.context.scene.camera
        self.__camera_list = bpy.data.cameras
        self.__scene_list = bpy.data.scenes
        self.__passes = []
        self.__width = resolution_x
        self.__height = resolution_y
        self.__render_images = render_images
        for scene in self.__scene_list:
            # Set cycles to use nodes and clean all the configurations
            scene.use_nodes = True
            scene.cycles.samples = samples
            scene.unit_settings.system = 'METRIC'

            scene.node_tree.nodes.clear()

            if background is Background.alpha:
                scene.render.film_transparent = True

            # Activate all the passes we support
            scene.view_layers[0].use_pass_normal = True
            scene.view_layers[0].use_pass_vector = True
            scene.view_layers[0].use_pass_z = True
            scene.view_layers[0].use_pass_object_index = True
            scene.view_layers[0].use_pass_uv = True
            scene.view_layers[0].use_pass_material_index = True
            if hasattr(scene.view_layers[0], "use_ao"):
                scene.view_layers[0].use_ao = True

            # Set rendering props
            scene.render.use_file_extension = True
            scene.render.image_settings.color_mode = 'RGBA'  # Enumrate this
            if hasattr(scene.render, "use_full_sample"):
                scene.render.use_full_sample = use_full_sample
            scene.render.resolution_percentage = resolution_percentage
            scene.render.resolution_x = resolution_x
            scene.render.resolution_y = resolution_y

        self.__init_renderer_type(renderer_type)

        # Create the render layer compositor
        self.__render_layers = self.__active_scene.node_tree.nodes.new(
            'CompositorNodeRLayers'
        )

        # Create all the render passes if we have any
        if (passes):
            for render_pass in passes:
                render_pass.init(self.__active_scene,
                                 self.__output_base_path,
                                 background)
                render_pass.create_pass(self.__render_layers)
                self.__passes.append(render_pass)

        # If we are on a GPU machine make sure all scenes are set to it
        if hardware_acceleration == "GPU":
            self.__init_gpu_renderer()

    def render(self, current_frame):
        """A method for rendering all passes of a single frame

        Arguments:
            current_frame {int} -- The current frame index

        Returns:
            list -- A list of strings with all the paths \
                of the rendering passes
        """
        # Assmble all the paths that we want to render
        paths = []

        # Only render image if not otherwise specified in constructor
        if (self.__render_images):
            bpy.ops.render.render(write_still=True)
            for render_pass in self.__passes:
                file_name = "/Image{:0>4}{}".format(current_frame,
                                                    render_pass.file_extension)
                paths.append(
                    {render_pass.type: render_pass.render_path + file_name})

        return paths

    def __init_renderer_type(self, renderer_type):
        """Assigns all the scenes in a project with a certain renderer type

        Arguments:
            renderer_type {RendererType} -- The type of rendering backend
        """
        for scene in self.__scene_list:
            scene.render.engine = renderer_type.value

    def __init_gpu_renderer(self):
        """Init the use of GPU accelerated processing"""
        for scene in self.__scene_list:
            scene.cycles.device = 'GPU'

        prefs = bpy.context.preferences
        cprefs = prefs.addons['cycles'].preferences

        # Calling this purges the device list so we need it
        cuda_devices, opencl_devices = cprefs.get_devices()  # pylint: disable=unused-variable

        # Attempt to set GPU device types if available
        for compute_device_type in ('CUDA', 'OPENCL'):
            try:
                cprefs.compute_device_type = compute_device_type
                break
            except TypeError:
                pass

        # Enable all CPU and GPU devices
        for device in cprefs.devices:
            device.use = True

    @property
    def cameras(self):
        """Get a list of all cameras in the project

        Returns:
            list -- Get the list of all cameras
        """
        return self.__camera_list

    @property
    def scenes(self):
        """Get a list of all the scenes in a project

        Returns:
            list -- A list of scenes in the project
        """
        return self.__scene_list

    @property
    def camera(self):
        """Get the active camera

        Returns:
            bpy.types.Camera -- The active camera
        """
        return self.__active_camera

    @property
    def scene(self):
        """Get the active scene

        Returns:
            bpy.types.Scene -- The active scene
        """
        return self.__active_scene

    @property
    def width(self):
        """Get the width of the renderer

        Returns:
            int -- Width in pixels
        """
        return self.__width

    @property
    def height(self):
        """Get the height of the renderer

        Returns:
            int -- Height in pixels
        """
        return self.__height
