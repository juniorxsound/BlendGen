"""Helpers for reading Blender scene objects."""

import bpy


def select(name):
    """Return the Blender object with ``name``."""
    if not isinstance(name, str) or not name:
        raise ValueError("select() requires a non-empty object name")
    return bpy.data.objects[name]


def bounding_box_to_world_positions(obj):
    """Return an object's local bounding-box vertices as coordinate lists."""
    return [vertex[:] for vertex in obj.bound_box]


def clamp(value, minimum, maximum):
    """Constrain a numeric value to an inclusive range."""
    return max(minimum, min(value, maximum))
