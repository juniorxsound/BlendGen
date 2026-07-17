"""Cycles renderer configuration."""

from dataclasses import dataclass
from enum import Enum

from blendgen.renderers.base import (RenderPassKind, UnsupportedRenderPassError,
                                     resolve_socket, validate_known_passes)


class CyclesDevice(Enum):
    """Cycles rendering device choices."""

    CPU = "CPU"
    GPU = "GPU"


@dataclass(frozen=True)
class CyclesBackend:
    """Configuration for Blender's Cycles render engine."""

    samples: int = 2
    device: CyclesDevice = CyclesDevice.CPU

    def __post_init__(self):
        if not isinstance(self.samples, int) or self.samples <= 0:
            raise ValueError("Cycles samples must be a positive integer")
        if not isinstance(self.device, CyclesDevice):
            raise ValueError("device must be a CyclesDevice")

    @property
    def name(self):
        """Return Blender's Cycles engine identifier."""
        return "CYCLES"

    def validate_passes(self, pass_kinds):
        """Ensure all requested passes are known to BlendGen."""
        validate_known_passes(pass_kinds)

    def configure_scene(self, scene, blender):
        """Configure Cycles and, when requested, its GPU preferences."""
        scene.render.engine = self.name
        scene.cycles.samples = self.samples
        scene.cycles.device = self.device.value
        if self.device is CyclesDevice.GPU:
            self._configure_gpu(blender)

    def bind_pass(self, pass_kind, view_layer, render_layers):
        """Enable and resolve one Cycles compositor pass."""
        self._enable_pass(pass_kind, view_layer)
        return resolve_socket(render_layers, pass_kind)

    @staticmethod
    def _enable_pass(pass_kind, view_layer):
        flags = {
            RenderPassKind.DEPTH: "use_pass_z",
            RenderPassKind.NORMAL: "use_pass_normal",
            RenderPassKind.OPTICAL_FLOW: "use_pass_vector",
            RenderPassKind.MATERIAL_INDEX: "use_pass_material_index",
        }
        flag = flags.get(pass_kind)
        if flag and not hasattr(view_layer, flag):
            raise UnsupportedRenderPassError(
                f"Cycles does not expose {pass_kind.value} in this Blender version")
        if flag:
            setattr(view_layer, flag, True)

    @staticmethod
    def _configure_gpu(blender):
        try:
            preferences = blender.context.preferences.addons["cycles"].preferences
        except KeyError as error:
            raise RuntimeError("Cycles GPU support is not available") from error
        preferences.get_devices()
        selected_device_type = None
        for device_type in ("CUDA", "OPTIX", "HIP", "METAL", "ONEAPI"):
            try:
                preferences.compute_device_type = device_type
                selected_device_type = device_type
                break
            except TypeError:
                continue
        if selected_device_type is None:
            raise RuntimeError("Cycles did not expose a supported GPU backend")
        enabled = 0
        for device in preferences.devices:
            device.use = device.type == selected_device_type
            enabled += int(device.use)
        if enabled == 0:
            raise RuntimeError(
                f"Cycles exposed no {selected_device_type} render devices")
