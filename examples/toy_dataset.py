from blendgen.session import Session
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.color import ColorPass
from blendgen.passes.alpha import AlphaPass
from blendgen.passes.depth import DepthPass
from blendgen.passes.normal import NormalPass
from blendgen.passes.opticalflow import OpticalFlowPass
from blendgen.passes.index import MaterialIndexPass
from blendgen.passes.base import ImageOutputType
from blendgen.util import *

'''
A render pass example that shows how to render different passes using BlendGen
To run this example use `make render_pass` or the docker command
Inside the Makefile
'''

# Create the dataset
dataset = Dataset("", output_type=DatasetOutputType.JSON)

# Create the renderer
renderer = Renderer(passes=[
    ColorPass(prefix="color",
              output_type=ImageOutputType.PNG),
    DepthPass(prefix="depth",
              output_type=ImageOutputType.EXR),
    NormalPass(prefix="normal"),
    OpticalFlowPass(prefix="opticalflow",
                    output_type=ImageOutputType.EXR),
    AlphaPass(prefix="alpha",
              output_type=ImageOutputType.PNG),
    MaterialIndexPass(prefix="index", index=0)
])


def on_before_new_frame(sess):
    # Get the world coords of the bounding box corners
    screen_coords = camera_view_bounds_2d(renderer.scene,
                                          renderer.camera,
                                          select("Model"))

    # Add the bone's world position and name to the dataset attributes
    dataset.add_attribute(
        attribute_name="bounding_box",
        attribute_value=screen_coords)

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
    renderer=renderer,
    dataset=dataset,
    frame_length=10,
    on_before_new_frame=on_before_new_frame
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
