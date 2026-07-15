"""Blender compositor compatibility and output helpers."""

from os import remove
from os.path import join

try:
    import OpenImageIO as oiio
except ImportError:
    oiio = None

try:
    import bpy
except ImportError:
    bpy = None


def compositor_tree(scene, bpy_module=None):
    """Return the compositor node tree for supported Blender versions."""
    if hasattr(scene, "node_tree"):
        return scene.node_tree

    bpy_module = bpy_module or bpy
    if bpy_module is None:
        raise RuntimeError("Blender's Python API is required for compositor setup")

    if scene.compositing_node_group is None:
        scene.compositing_node_group = bpy_module.data.node_groups.new(
            "BlendGen Compositor", "CompositorNodeTree")
    return scene.compositing_node_group


def create_output_node(nodes, output_path, output_type):
    """Create and configure a File Output node for one render pass."""
    output_node = nodes.new(type="CompositorNodeOutputFile")
    if hasattr(output_node, "base_path"):
        output_node.base_path = output_path
        output_node.format.file_format = output_type.value
        return output_node

    output_node.directory = output_path
    output_node.file_name = "Image"
    output_item = output_node.file_output_items.new("RGBA", "Image")
    output_item.override_node_format = True
    output_item.format.file_format = output_type.value
    return output_node


def set_frame_filename(output_node, frame_number):
    """Set Blender 5's explicit output filename for a frame."""
    if not hasattr(output_node, "base_path"):
        output_node.file_name = f"Image{frame_number:0>4}"


def convert_temporary_output(output_node, target_path, display_transform=False):
    """Convert Blender 5's temporary EXR compositor result to a target file.

    Color images are scene-linear in Blender's compositor. Apply the sRGB
    display transform only when producing a viewable color image; data passes
    such as depth, normals, and segmentation indices remain unmodified.
    """
    if oiio is None:
        raise RuntimeError("OpenImageIO is required to convert compositor output")
    source_path = join(output_node.directory, output_node.file_name + ".exr")
    image = oiio.ImageBuf(source_path)
    if display_transform:
        source_color_space = image.spec().get_string_attribute(
            "oiio:ColorSpace", "lin_rec709_scene")
        image = oiio.ImageBufAlgo.colorconvert(
            image, source_color_space, "sRGB")
    if not image.write(target_path):
        raise RuntimeError(
            f"Could not convert compositor output: {image.geterror()}")
    remove(source_path)
