"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
import json
from enum import Enum
from datetime import datetime
import numpy as np  # pylint: disable=import-error


class DatasetOutputType(Enum):
    """Defines the type of dataset output file"""
    JSON = "JSON"
    NPY = "NPY"


class Dataset(object):
    """A wrapper class to define the dataset index file

    Raises:
        ValueError: When prefix is not set
        ValueError: When calling add_frame without a frame_num arg


    Returns:
        Dataset -- The instance of dataset created
    """

    def __init__(self,
                 prefix=None,
                 dataset_name="BlendGen toy dataset",
                 output_dir="data/toy_dataset/",
                 filename="blendgen_dataset",
                 output_type=None):
        """Create a dataset wrapper class

        Keyword Arguments:
            prefix {str} -- The folder prefix to prepand (default: {None})
            dataset_name {str} -- The name of the \
                dataset (default: {"BlendGen toy dataset"})
            output_dir {str} -- The base path \
                of the dataset (default: {"data/toy_dataset/"})
            filename {str} -- Name of dataset index file \
                without extension (default: {"blendgen_dataset"})
            output_type {DatasetOutputType} -- The type of output \
                file to save (default: {None})

        Raises:
            ValueError: when a prefix is not provided
        """
        if prefix is None:
            raise ValueError("Must provide a prefix value")

        self.__prefix = prefix
        self.__output_type = output_type
        self.__base_path = output_dir
        self.__file_name = filename
        self.__name = dataset_name
        self.__dataset = {
            "name": self.__name,
            "date": datetime.now().strftime("%m/%d/%Y,%H:%M:%S"),
            "data": None
        }
        self.__frames = []
        self.__single_frame_atrribtues = []

    def add_attribute(self, attribute_name=None, attribute_value=None):
        """A method to manually add an attribute to the dataset

        Keyword Arguments:
            attributeName {str} -- The name of the attribute (default: {None})
            attributeValue {any} -- Any value you want to add (default: {None})
        """
        val = attribute_value if attribute_value is not None else []

        self.__single_frame_atrribtues.append({
            attribute_name: val
        })

    def add_frame(self, frame_num=None, attributes=None, passes=None):
        """Add a frame to the dataset index file

        Keyword Arguments:
            frame_num {int} -- The current frame index (default: {None})
            attributes {list} -- List of attributes (default: {None})
            passes {list} -- List of render passes (default: {None})

        Raises:
            ValueError: when a frame number is not provided
        """

        atrrib = attributes if attributes is not None \
            else self.__single_frame_atrribtues
        render_passes = passes if passes is not None else []

        if frame_num is not None:
            self.__frames.append({
                "index": str(frame_num),
                "passes": render_passes,
                "attributes": atrrib})

            # Clear single frame attributes added manually
            self.__single_frame_atrribtues = []
        else:
            raise ValueError(
                "Must provide frame number when calling Dataset.add_frame")

    def save(self):
        """Save the dataset to file"""
        # Append the frames into the dataset ['data'] attributes
        self.__dataset["data"] = self.__frames

        # Serialize to JSON
        if self.__output_type is DatasetOutputType.JSON:
            with open("{}{}.{}".format(self.__base_path,
                                       self.__file_name,
                                       self.__output_type.value.lower()),
                      "w") as outfile:
                json.dump(self.__dataset, outfile)

        # Serialise to npy binary
        if self.__output_type is DatasetOutputType.NPY:
            np.save("{}{}.{}".format(self.__base_path,
                                     self.__file_name,
                                     self.__output_type.value.lower()),
                    np.array(self.__dataset)
                    )

    @property
    def name(self):
        """Dataset name getter

        Returns:
            str -- Name of the dataset
        """
        return self.__name

    @property
    def prefix(self):
        """Dataset prefix getter

        Returns:
            str -- The path prefix
        """
        return self.__prefix

    @property
    def output_type(self):
        """Getter for dataset file output type

        Returns:
            DatasetOutputType -- The type of output file
        """
        return self.__output_type

    @property
    def raw(self):
        """Dataset frames getter

        Returns:
            list -- The raw dataset frames list
        """
        return self.__frames
