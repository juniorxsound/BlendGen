from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType
from blendgen.util import get_pose_bone_world_matrix
from blendgen.utils.scene import select

'''
An advanced example that shows how to store 3D (i.e world space) pose bone positions
To run this example use `make pose_3D` or the docker command
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

    # Iterate over all bones in the pose
    for bone in select("Character").data.bones:

        # Get the world position of each bone
        world_matrix = get_pose_bone_world_matrix(
            select("Character"), bone.name)
        world_pos, world_rot, world_scale = world_matrix.decompose()

        # Add it to the dataset
        dataset.add_attribute(
            attribute_name=bone.name,
            attribute_value=[
                world_pos[0],
                world_pos[1],
                world_pos[2]
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
