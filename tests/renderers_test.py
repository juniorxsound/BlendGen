"""Fast tests for renderer backend configuration and pass capability checks."""

import unittest

from blendgen.passes.alpha import AlphaPass
from blendgen.passes.color import ColorPass
from blendgen.passes.depth import DepthPass
from blendgen.passes.index import MaterialIndexPass, RawMaterialIndexPass
from blendgen.passes.normal import NormalPass
from blendgen.passes.opticalflow import OpticalFlowPass
from blendgen.renderers import (CyclesBackend, CyclesDevice, EeveeBackend,
                                 RenderPassKind, UnsupportedRenderPassError)


class TestBackendConfiguration(unittest.TestCase):
    def test_cycles_defaults(self):
        backend = CyclesBackend()
        self.assertEqual(backend.name, "CYCLES")
        self.assertEqual(backend.device, CyclesDevice.CPU)

    def test_eevee_defaults(self):
        backend = EeveeBackend()
        self.assertEqual(backend.name, "BLENDER_EEVEE")
        self.assertEqual(backend.samples, 16)

    def test_rejects_non_positive_samples(self):
        with self.assertRaises(ValueError):
            CyclesBackend(samples=0)
        with self.assertRaises(ValueError):
            EeveeBackend(samples=-1)

    def test_eevee_rejects_material_index(self):
        with self.assertRaises(UnsupportedRenderPassError):
            EeveeBackend().validate_passes([RenderPassKind.MATERIAL_INDEX])

    def test_eevee_accepts_shared_passes(self):
        EeveeBackend().validate_passes([
            RenderPassKind.COLOR, RenderPassKind.ALPHA, RenderPassKind.DEPTH,
            RenderPassKind.NORMAL, RenderPassKind.OPTICAL_FLOW,
        ])

    def test_public_passes_declare_semantic_kinds(self):
        self.assertEqual(ColorPass().kind, RenderPassKind.COLOR)
        self.assertEqual(AlphaPass().kind, RenderPassKind.ALPHA)
        self.assertEqual(DepthPass().kind, RenderPassKind.DEPTH)
        self.assertEqual(NormalPass().kind, RenderPassKind.NORMAL)
        self.assertEqual(OpticalFlowPass().kind, RenderPassKind.OPTICAL_FLOW)
        self.assertEqual(MaterialIndexPass().kind, RenderPassKind.MATERIAL_INDEX)
        self.assertEqual(RawMaterialIndexPass().kind,
                         RenderPassKind.MATERIAL_INDEX)
