"""Eevee renderer configuration."""

from dataclasses import dataclass

from blendgen.renderers.base import (RenderPassKind, UnsupportedRenderPassError,
                                     resolve_socket, validate_known_passes)


@dataclass(frozen=True)
class EeveeBackend:
    """Configuration for Blender's Eevee engine."""

    samples: int = 16

    def __post_init__(self):
        if not isinstance(self.samples, int) or self.samples <= 0:
            raise ValueError("Eevee samples must be a positive integer")

    @property
    def name(self):
        """Return Blender's Eevee engine identifier."""
        return "BLENDER_EEVEE"

    def validate_passes(self, pass_kinds):
        """Ensure requested passes are reliable in Eevee."""
        if RenderPassKind.MATERIAL_INDEX in pass_kinds:
            raise UnsupportedRenderPassError(
                "Eevee does not reliably expose the material-index pass in Blender 5")
        validate_known_passes(pass_kinds)

    def configure_scene(self, scene, _blender):
        """Configure Eevee samples for one Blender scene."""
        scene.render.engine = self.name
        if not hasattr(scene, "eevee"):
            raise RuntimeError("This Blender version does not provide Eevee settings")
        scene.eevee.taa_render_samples = self.samples

    def bind_pass(self, pass_kind, view_layer, render_layers):
        """Enable and resolve one Eevee compositor pass."""
        flags = {
            RenderPassKind.DEPTH: "use_pass_z",
            RenderPassKind.NORMAL: "use_pass_normal",
            RenderPassKind.OPTICAL_FLOW: "use_pass_vector",
        }
        flag = flags.get(pass_kind)
        if flag and not hasattr(view_layer, flag):
            raise UnsupportedRenderPassError(
                f"Eevee does not support {pass_kind.value} in this Blender version")
        if flag:
            setattr(view_layer, flag, True)
        return resolve_socket(render_layers, pass_kind)
