"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
import unittest

# Components
from blendgen.dataset import Dataset, DatasetOutputType


class TestDataset(unittest.TestCase):
    def test_constructor_sets_prefix(self):
        dataset = Dataset(
            prefix="test", output_type=DatasetOutputType.JSON)
        self.assertEqual(dataset.prefix, "test")

    def test_constructor_sets_output_type(self):
        dataset = Dataset(
            prefix="test", output_type=DatasetOutputType.JSON)
        self.assertEqual(dataset.output_type, DatasetOutputType.JSON)

    def test_constructor_sets_dataset_name(self):
        dataset = Dataset(
            prefix="test",
            output_type=DatasetOutputType.JSON,
            dataset_name="Test Name")
        self.assertEqual(dataset.name, "Test Name")

    @unittest.expectedFailure
    def test_constructor_raises_error_without_prefix(self):
        dataset = Dataset(output_type=DatasetOutputType.JSON)

    def test_add_frame_adds_frame_dataset(self):
        dataset = Dataset(prefix="test",
                          output_type=DatasetOutputType.JSON)
        dataset.add_frame(frame_num=0, passes=[
                          {"ColorPass": "some/test/path"}])
        self.assertEqual(dataset.raw[0]["index"], str(0))
        self.assertEqual(dataset.raw[0]["passes"]
                         [0]["ColorPass"], "some/test/path")
