"""Blender compositor compatibility and output helpers."""

from os import remove
from os.path import join

try:
    import OpenImageIO as oiio
except ImportError:
    oiio = None

try:
    import numpy as np
except ImportError:
    np = None

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


MULTILAYER_CHANNEL_SUFFIXES = {
    "color": ("Combined.R", "Combined.G", "Combined.B", "Combined.A"),
    "alpha": ("Combined.A",),
    "depth": ("Depth.Z",),
    "normal": ("Normal.X", "Normal.Y", "Normal.Z"),
    "optical_flow": ("Vector.X", "Vector.Y", "Vector.Z", "Vector.W"),
    "material_index": ("Material Index.X",),
}


def extract_multilayer_output(multilayer_path, pass_kind, target_path,
                              display_transform=False):
    """Write one raw semantic pass from a multilayer EXR to ``target_path``."""
    if oiio is None or np is None:
        raise RuntimeError(
            "OpenImageIO and NumPy are required to extract multilayer output")

    image_input = oiio.ImageInput.open(multilayer_path)
    if image_input is None:
        raise RuntimeError(f"Could not open multilayer output: {multilayer_path}")
    try:
        spec = image_input.spec()
        channel_names = list(spec.channelnames)
        indices = []
        for suffix in MULTILAYER_CHANNEL_SUFFIXES[pass_kind.value]:
            matches = [index for index, name in enumerate(channel_names)
                       if name.endswith(suffix)]
            if len(matches) != 1:
                raise RuntimeError(
                    f"Expected one channel ending in {suffix!r}, found {matches}")
            indices.append(matches[0])
        pixels = image_input.read_image()
    finally:
        image_input.close()

    output = oiio.ImageBuf(np.ascontiguousarray(pixels[..., indices]))
    if display_transform:
        output = oiio.ImageBufAlgo.colorconvert(
            output, "lin_rec709_scene", "sRGB")
    if not output.write(target_path):
        raise RuntimeError(
            f"Could not write extracted pass {target_path}: {output.geterror()}")
