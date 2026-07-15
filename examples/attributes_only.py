from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType
from blendgen.util import select

'''
A simple example that shows how to store attributes only without rendering images at all. 
In essence creating an attributes only datasets which are also very fast to make!

To run this example use `make attributes_only` or the docker command
inside the Makefile
'''

# Create the dataset
dataset = Dataset("", output_type=DatasetOutputType.JSON)

# Create the renderer
renderer = Renderer(render_images=False)


def on_before_new_frame(sess):
    # Get the model's position
    x, y, z, w = select("Model").rotation_quaternion

    # Add the model's world position and name to the dataset attributes
    dataset.add_attribute(
        attribute_name="rotation",
        attribute_value=[x, y, z, w])


# Create the session
sess = Session(
    dataset=dataset,
    renderer=renderer,
    frame_length=100,
    on_before_new_frame=on_before_new_frame
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
