"""Shared render orchestration for all Blender render backends."""

from enum import Enum

import bpy

from blendgen.compositor import (compositor_tree, convert_temporary_output,
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
        if backend is None:
            backend = CyclesBackend()
        if not isinstance(background, Background):
            raise ValueError("background must be a Background")
        for name, value in (("resolution_percentage", resolution_percentage),
                            ("resolution_x", resolution_x),
                            ("resolution_y", resolution_y)):
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        required_backend_methods = ("name", "validate_passes", "configure_scene",
                                    "bind_pass")
        if not all(hasattr(backend, method) for method in required_backend_methods):
            raise ValueError("backend must implement the RenderBackend interface")

        self.__output_base_path = output_base_path
        self.__active_scene = bpy.context.scene
        self.__active_camera = bpy.context.scene.camera
        self.__camera_list = bpy.data.cameras
        self.__scene_list = bpy.data.scenes
        self.__passes = list(passes or [])
        self.__width = resolution_x
        self.__height = resolution_y
        self.__render_images = render_images
        self.__backend = backend

        pass_kinds = []
        for render_pass in self.__passes:
            kind = getattr(render_pass, "kind", None)
            if not isinstance(kind, RenderPassKind):
                raise ValueError("Every render pass must declare a RenderPassKind")
            pass_kinds.append(kind)
        backend.validate_passes(pass_kinds)

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

        compositor = compositor_tree(self.__active_scene, bpy)
        self.__render_layers = compositor.nodes.new("CompositorNodeRLayers")
        view_layer = self.__active_scene.view_layers[0]
        for render_pass in self.__passes:
            render_pass.init(self.__active_scene, self.__output_base_path, background)
            source_socket = backend.bind_pass(render_pass.kind, view_layer,
                                              self.__render_layers)
            render_pass.create_pass(source_socket)

    def render(self, current_frame):
        """Render a frame and return the existing dataset pass-path schema."""
        paths = []
        if self.__render_images:
            for render_pass in self.__passes:
                output_node = render_pass.output_node
                if not hasattr(output_node, "base_path"):
                    set_frame_filename(output_node, current_frame)

            bpy.ops.render.render(write_still=True)
            for render_pass in self.__passes:
                file_name = f"/Image{current_frame:0>4}{render_pass.file_extension}"
                output_node = render_pass.output_node
                if (not hasattr(output_node, "base_path")
                        and render_pass.file_extension != ".exr"):
                    convert_temporary_output(
                        output_node, render_pass.render_path + file_name,
                        display_transform=render_pass.display_transform)
                paths.append({render_pass.type: render_pass.render_path + file_name})
        return paths

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
