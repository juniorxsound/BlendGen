from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.passes.alpha import AlphaPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType
from blendgen.util import get_pose_bone_world_matrix, get_screen_coords, select, get_camera_matrices

# Create the dataset
dataset = Dataset("",
                  dataset_name="Multicam - cam4",
                  output_dir="data/cam4/",
                  filename="attributes",
                  output_type=DatasetOutputType.JSON)

# Create the renderer
renderer = Renderer(
    output_base_path="data/cam4/",
    samples=256,
    resolution_x=1280,
    resolution_y=720,
    passes=[
        ColorPass(prefix="color",
                  output_type=ImageOutputType.PNG),
        AlphaPass(prefix="alpha",
                  output_type=ImageOutputType.PNG)
    ])


def on_before_new_frame(sess):
    pmatrix, imatrix, rt_matrix = get_camera_matrices(
        renderer)

    # Add it to the dataset
    dataset.add_attribute(
        attribute_name="intrinsic_matrix_3x3",
        attribute_value=[imatrix[0][0], imatrix[0][1], imatrix[0][2],
                         imatrix[1][0], imatrix[1][1], imatrix[1][2],
                         imatrix[2][0], imatrix[2][1], imatrix[2][2]])

    dataset.add_attribute(
        attribute_name="rt_matrix_3x4",
        attribute_value=[rt_matrix[0][0], rt_matrix[0][1], rt_matrix[0][2], rt_matrix[0][3],
                         rt_matrix[1][0], rt_matrix[1][1], rt_matrix[1][2], rt_matrix[1][3],
                         rt_matrix[2][0], rt_matrix[2][1], rt_matrix[2][2], rt_matrix[2][3]])

    dataset.add_attribute(
        attribute_name="projection_matrix_3x4",
        attribute_value=[pmatrix[0][0], pmatrix[0][1], pmatrix[0][2], pmatrix[0][3],
                         pmatrix[1][0], pmatrix[1][1], pmatrix[1][2], pmatrix[1][3],
                         pmatrix[2][0], pmatrix[2][1], pmatrix[2][2], pmatrix[2][3]])


# Create the session
sess = Session(
    dataset=dataset,
    renderer=renderer,
    output_dir="data/cam4/",
    frame_length=450,
    on_before_new_frame=on_before_new_frame
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
