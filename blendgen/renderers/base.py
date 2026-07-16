"""Renderer backend contracts and shared render-pass semantics."""

from enum import Enum
from abc import abstractmethod
from typing import Protocol


class RenderPassKind(Enum):
    """Semantic passes exposed by BlendGen, independent of Blender sockets."""

    COLOR = "color"
    ALPHA = "alpha"
    DEPTH = "depth"
    NORMAL = "normal"
    OPTICAL_FLOW = "optical_flow"
    MATERIAL_INDEX = "material_index"


class UnsupportedRenderPassError(ValueError):
    """Raised when a backend cannot reliably produce a requested pass."""


class RenderBackend(Protocol):
    """The small interface used by :class:`blendgen.renderer.Renderer`."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the Blender engine identifier."""
        raise NotImplementedError

    @abstractmethod
    def validate_passes(self, pass_kinds) -> None:
        """Reject semantic passes unsupported by this backend."""
        raise NotImplementedError

    @abstractmethod
    def configure_scene(self, scene, blender) -> None:
        """Apply this backend's settings to one Blender scene."""
        raise NotImplementedError

    @abstractmethod
    def bind_pass(self, pass_kind, view_layer, render_layers):
        """Enable and return the compositor source for a semantic pass."""
        raise NotImplementedError


SOCKET_ALIASES = {
    RenderPassKind.COLOR: ("Image",),
    RenderPassKind.ALPHA: ("Alpha",),
    RenderPassKind.DEPTH: ("Depth", "Z"),
    RenderPassKind.NORMAL: ("Normal",),
    RenderPassKind.OPTICAL_FLOW: ("Vector",),
    RenderPassKind.MATERIAL_INDEX: ("IndexMA", "Material Index"),
}


def resolve_socket(render_layers, pass_kind):
    """Resolve a compositor socket with compatibility aliases."""
    for name in SOCKET_ALIASES[pass_kind]:
        socket = render_layers.outputs.get(name)
        if socket is not None:
            return socket
    aliases = ", ".join(SOCKET_ALIASES[pass_kind])
    raise UnsupportedRenderPassError(
        f"Blender did not expose a {pass_kind.value} socket (tried: {aliases})")


def validate_known_passes(pass_kinds):
    """Raise when a backend receives a pass outside BlendGen's semantics."""
    unsupported = set(pass_kinds) - set(RenderPassKind)
    if unsupported:
        raise UnsupportedRenderPassError(
            f"Unsupported render passes: {unsupported}")
