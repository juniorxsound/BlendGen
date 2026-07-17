"""Shared render orchestration for all Blender render backends."""

from enum import Enum
from os import makedirs, remove
from os.path import exists, join

import bpy

from blendgen.compositor import (compositor_tree, convert_temporary_output,
                                 extract_multilayer_output,
                                 set_frame_filename)
from blendgen.renderers import CyclesBackend, RenderPassKind


class Background(Enum):
    """Background behavior for color rendering."""

    ALPHA = "TRANSPARENT"
    SKY = "SKY"


class Renderer:
    """Render requested semantic passes using an explicit backend."""

    def __init__(self, *, backend=None, background=Background.ALPHA,
                 resolution_percentage=100, resolution_x=1920,
                 resolution_y=1080, output_base_path="data/toy_dataset/",
                 passes=None, render_images=True):
        backend = backend or CyclesBackend()
        render_passes = list(passes or [])
        self.__validate_configuration(
            backend, background, resolution_percentage,
            resolution_x, resolution_y, render_passes)

        self.__output_base_path = output_base_path
        self.__active_scene = bpy.context.scene
        self.__active_camera = bpy.context.scene.camera
        self.__camera_list = bpy.data.cameras
        self.__scene_list = bpy.data.scenes
        self.__passes = render_passes
        self.__width = resolution_x
        self.__height = resolution_y
        self.__render_images = render_images
        self.__backend = backend

        self.__configure_scenes(
            backend, background, resolution_percentage,
            resolution_x, resolution_y)
        self.__configure_passes(backend, background)

    @staticmethod
    def __validate_configuration(backend, background, resolution_percentage,
                                 resolution_x, resolution_y, render_passes):
        """Validate renderer options before mutating the active Blender file."""
        if not isinstance(background, Background):
            raise ValueError("background must be a Background")
        for name, value in (("resolution_percentage", resolution_percentage),
                            ("resolution_x", resolution_x),
                            ("resolution_y", resolution_y)):
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

        required_methods = ("name", "validate_passes", "configure_scene",
                            "bind_pass")
        if not all(hasattr(backend, method) for method in required_methods):
            raise ValueError("backend must implement the RenderBackend interface")

        pass_kinds = []
        for render_pass in render_passes:
            kind = getattr(render_pass, "kind", None)
            if not isinstance(kind, RenderPassKind):
                raise ValueError("Every render pass must declare a RenderPassKind")
            pass_kinds.append(kind)
        backend.validate_passes(pass_kinds)

    def __configure_scenes(self, backend, background, resolution_percentage,
                           resolution_x, resolution_y):
        """Apply shared output settings and backend configuration to scenes."""
        for scene in self.__scene_list:
            scene.use_nodes = True
            scene.unit_settings.system = "METRIC"
            compositor_tree(scene, bpy).nodes.clear()
            scene.render.film_transparent = background is Background.ALPHA
            scene.render.use_file_extension = True
            scene.render.image_settings.color_mode = "RGBA"
            scene.render.resolution_percentage = resolution_percentage
            scene.render.resolution_x = resolution_x
            scene.render.resolution_y = resolution_y
            backend.configure_scene(scene, bpy)

    def __configure_passes(self, backend, background):
        """Build the compositor inputs and bind all requested semantic passes."""
        compositor = compositor_tree(self.__active_scene, bpy)
        self.__render_layers = compositor.nodes.new("CompositorNodeRLayers")
        final_input = self.__create_final_output(compositor)
        compositor.links.new(self.__render_layers.outputs["Image"], final_input)
        view_layer = self.__active_scene.view_layers[0]
        for render_pass in self.__passes:
            render_pass.init(self.__active_scene, self.__output_base_path, background)
            source_socket = backend.bind_pass(render_pass.kind, view_layer,
                                              self.__render_layers)
            render_pass.create_pass(source_socket)

    @staticmethod
    def __create_final_output(compositor):
        """Create the active final output required to evaluate the compositor."""
        # Blender skips compositor evaluation when the tree has no active
        # final output, even when File Output nodes are present. Blender 5's
        # scene compositor is a node group and uses Group Output; older
        # versions use the legacy Composite node.
        try:
            final_output = compositor.nodes.new("CompositorNodeComposite")
            final_input = final_output.inputs["Image"]
        except RuntimeError:
            compositor.interface.new_socket(
                name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
            final_output = compositor.nodes.new("NodeGroupOutput")
            final_output.is_active_output = True
            final_input = final_output.inputs["Image"]
        return final_input

    def render(self, current_frame):
        """Render a frame and return the existing dataset pass-path schema."""
        paths = []
        if self.__render_images:
            for render_pass in self.__passes:
                output_node = render_pass.output_node
                if not hasattr(output_node, "base_path"):
                    set_frame_filename(output_node, current_frame)

            bpy.ops.render.render()
            direct_outputs_exist = all(
                exists(self.__direct_output_path(render_pass, current_frame))
                for render_pass in self.__passes
            )
            if not direct_outputs_exist:
                return self.__extract_render_result(current_frame)

            for render_pass in self.__passes:
                file_name = f"/Image{current_frame:0>4}{render_pass.file_extension}"
                output_node = render_pass.output_node
                if (not hasattr(output_node, "base_path")
                        and render_pass.file_extension != ".exr"):
                    convert_temporary_output(
                        output_node, render_pass.render_path + file_name,
                        display_transform=render_pass.display_transform)
                output_path = render_pass.render_path + file_name
                if not exists(output_path):
                    raise RuntimeError(
                        f"Render pass did not create its expected file: {output_path}")
                paths.append({render_pass.type: output_path})
        return paths

    @staticmethod
    def __direct_output_path(render_pass, current_frame):
        output_node = render_pass.output_node
        if not hasattr(output_node, "base_path"):
            return join(output_node.directory,
                        output_node.file_name + ".exr")
        return (render_pass.render_path
                + f"/Image{current_frame:0>4}{render_pass.file_extension}")

    def __extract_render_result(self, current_frame):
        """Split the existing Render Result when File Output nodes emit nothing."""
        for render_pass in self.__passes:
            if len(render_pass.ops) != 1:
                raise RuntimeError(
                    "Multilayer fallback only supports raw semantic passes; "
                    f"{render_pass.type} contains compositor transformations")

        temporary_dir = join(self.__output_base_path, ".blendgen")
        makedirs(temporary_dir, exist_ok=True)
        multilayer_path = join(
            temporary_dir, f"Image{current_frame:0>4}.exr")
        settings = self.__active_scene.render.image_settings
        original = (settings.file_format, settings.color_mode,
                    settings.color_depth, settings.exr_codec)
        try:
            settings.file_format = "OPEN_EXR_MULTILAYER"
            settings.color_mode = "RGBA"
            settings.color_depth = "32"
            settings.exr_codec = "ZIP"
            bpy.data.images["Render Result"].save_render(
                multilayer_path, scene=self.__active_scene)
            if not exists(multilayer_path):
                raise RuntimeError(
                    f"Blender did not create fallback output: {multilayer_path}")

            paths = []
            for render_pass in self.__passes:
                target_path = (render_pass.render_path
                               + f"/Image{current_frame:0>4}"
                               + render_pass.file_extension)
                extract_multilayer_output(
                    multilayer_path, render_pass.kind, target_path,
                    display_transform=render_pass.display_transform)
                if not exists(target_path):
                    raise RuntimeError(
                        f"Fallback did not create expected pass: {target_path}")
                paths.append({render_pass.type: target_path})
            return paths
        finally:
            settings.file_format, settings.color_mode, settings.color_depth, \
                settings.exr_codec = original
            if exists(multilayer_path):
                remove(multilayer_path)

    @property
    def backend(self):
        """The explicit backend configuration used by this renderer."""
        return self.__backend

    @property
    def cameras(self):
        """Return the cameras available in the current Blender project."""
        return self.__camera_list

    @property
    def scenes(self):
        """Return the scenes available in the current Blender project."""
        return self.__scene_list

    @property
    def camera(self):
        """Return the active camera."""
        return self.__active_camera

    @property
    def scene(self):
        """Return the active scene."""
        return self.__active_scene

    @property
    def width(self):
        """Return the configured render width in pixels."""
        return self.__width

    @property
    def height(self):
        """Return the configured render height in pixels."""
        return self.__height
