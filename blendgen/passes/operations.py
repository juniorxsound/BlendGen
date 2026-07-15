"""Composable Blender compositor operations used by render passes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationSockets:
    """The input and output sockets of one compositor operation."""

    input_socket: object
    output_socket: object


def map_value(nodes, minimum=0, maximum=255, size=0.08):
    """Create a clamped Map Value operation."""
    mapper = nodes.new(type="CompositorNodeMapValue")
    mapper.size = [size]
    mapper.use_min = True
    mapper.min = [minimum]
    mapper.use_max = True
    mapper.max = [maximum]
    return OperationSockets(mapper.inputs[0], mapper.outputs[0])


def invert(nodes):
    """Create an image invert operation."""
    inverter = nodes.new(type="CompositorNodeInvert")
    return OperationSockets(inverter.inputs[1], inverter.outputs[0])


def material_index_mask(nodes, links, index, color=None):
    """Create a material-index mask, optionally colored with an RGB value."""
    mask = nodes.new(type="CompositorNodeIDMask")
    if hasattr(mask, "use_antialiasing"):
        mask.use_antialiasing = True
        mask.index = index
    else:
        mask.inputs["Anti-Alias"].default_value = True
        mask.inputs["Index"].default_value = index

    if color is None:
        return OperationSockets(mask.inputs[0], mask.outputs[0])

    red, green, blue = color
    multiplier = nodes.new(type="CompositorNodeMixRGB")
    multiplier.blend_type = "MULTIPLY"
    color_node = nodes.new(type="CompositorNodeRGB")
    color_node.outputs[0].default_value = red, green, blue, 1.0
    links.new(mask.outputs[0], multiplier.inputs[0])
    links.new(mask.outputs[0], multiplier.inputs[1])
    links.new(color_node.outputs[0], multiplier.inputs[2])
    return OperationSockets(mask.inputs[0], multiplier.outputs[0])
