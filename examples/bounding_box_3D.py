from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType
from blendgen.utils.scene import bounding_box_to_world_positions, select

'''
An advanced example that shows how to store 3D (i.e world space) bounding box
To run this example use `make bb_3D` or the docker command
inside the Makefile
'''

# Create the dataset
dataset = Dataset("", output_type=DatasetOutputType.JSON)

# Create the renderer
renderer = Renderer(passes=[
    ColorPass(prefix="color",
              output_type=ImageOutputType.PNG)
])


def on_before_new_frame(sess):
    # Get the world coords of the bounding box corners
    world_coords = bounding_box_to_world_positions(select("CharacterMesh"))

    # Add the bone's world position and name to the dataset attributes
    dataset.add_attribute(
        attribute_name="bounding_box",
        attribute_value=world_coords)


# Create the session
sess = Session(
    dataset=dataset,
    renderer=renderer,
    frame_length=1,
    on_before_new_frame=on_before_new_frame
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
