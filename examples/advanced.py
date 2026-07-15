from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.renderer import Renderer
from blendgen.passes.base import ImageOutputType

'''
A advanced example that shows how to use custom renderer, dataset and session
To run this example use `make advanced` or the docker command
Inside the Makefile
'''

# Create the dataset
dataset = Dataset("", output_type=DatasetOutputType.JSON)

# Create the renderer
renderer = Renderer(passes=[
    ColorPass(prefix="color",
              output_type=ImageOutputType.PNG)
])

# Create the session
sess = Session(
    dataset=dataset,
    renderer=renderer,
    frame_length=1
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
