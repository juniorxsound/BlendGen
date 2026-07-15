"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
import unittest

# Components
from blendgen.passes.base import BaseRenderPass, ImageOutputType


class TestBaseRenderPass(unittest.TestCase):
    def test_constructor_sets_prefix(self):
        base_pass = BaseRenderPass(
            prefix="test", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.prefix, "test")

    def test_constructor_sets_output_type(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.output_type, ImageOutputType.PNG)

    @unittest.expectedFailure
    def test_constructor_raises_value_error_when_no_prefix_provided(self):
        base_pass = BaseRenderPass(output_type=ImageOutputType.PNG)

    @unittest.expectedFailure
    def test_constructor_raises_value_error_when_no_output_type_provided(self):
        base_pass = BaseRenderPass(prefix="")

    def test_constructor_sets_PNG_file_extension_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.file_extension, ".png")

    def test_constructor_sets_PNG_output_type_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.output_type, ImageOutputType.PNG)

    def test_constructor_sets_EXR_file_extension_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.EXR)
        self.assertEqual(base_pass.file_extension, ".exr")

    def test_constructor_sets_EXR_output_type_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.EXR)
        self.assertEqual(base_pass.output_type, ImageOutputType.EXR)

    def test_constructor_sets_JPEG_file_extension_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.JPEG)
        self.assertEqual(base_pass.file_extension, ".jpeg")
    
    def test_constructor_sets_JPEG_output_type_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.JPEG)
        self.assertEqual(base_pass.output_type, ImageOutputType.JPEG)

    def test_constructor_sets_TIFF_file_extension_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.TIFF)
        self.assertEqual(base_pass.file_extension, ".tiff")

    def test_constructor_sets_TIFF_output_type_from_ImageOutputType(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.TIFF)
        self.assertEqual(base_pass.output_type, ImageOutputType.TIFF)

    def test_type_returns_base_type(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.type, BaseRenderPass.__name__)

    def test_base_path_returns_none_before_being_set(self):
        base_pass = BaseRenderPass(prefix="", output_type=ImageOutputType.PNG)
        self.assertEqual(base_pass.base_path, None)
