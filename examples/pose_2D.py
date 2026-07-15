from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType
from blendgen.util import get_pose_bone_world_matrix, get_screen_coords, select

'''
An advanced example that shows how to store 2D (i.e screen space) pose bone psotion
To run this example use `make pose_2D` or the docker command
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

    for bone in select("Armature").data.bones:

        # Get the world position of each bone
        world_matrix = get_pose_bone_world_matrix(
            select("Armature"), bone.name)
        world_pos, world_rot, world_scale = world_matrix.decompose()

        # Get the screen position from each world position
        screen_x, screen_y = get_screen_coords(world_pos, renderer)

        # Add it to the dataset
        dataset.add_attribute(
            attribute_name=bone.name,
            attribute_value=[
                screen_x, screen_y
            ])


# Create the session
sess = Session(
    dataset=dataset,
    renderer=renderer,
    frame_length=5,
    on_before_new_frame=on_before_new_frame
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
