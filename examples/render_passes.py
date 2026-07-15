from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.passes.alpha import AlphaPass
from blendgen.passes.depth import DepthPass
from blendgen.passes.normal import NormalPass
from blendgen.passes.opticalflow import OpticalFlowPass
from blendgen.passes.index import MaterialIndexPass
from blendgen.passes.base import ImageOutputType

'''
A render pass example that shows how to render different passes using BlendGen
To run this example use `make render_pass` or the docker command
Inside the Makefile
'''


# Create the session
sess = Session(
    # Define the render passes
    passes=[
        ColorPass(prefix="color",
                  output_type=ImageOutputType.PNG),
        DepthPass(prefix="depth",
                  output_type=ImageOutputType.EXR),
        NormalPass(prefix="normal"),
        OpticalFlowPass(prefix="opticalflow",
                        output_type=ImageOutputType.EXR),
        AlphaPass(prefix="alpha",
                  output_type=ImageOutputType.PNG),
        MaterialIndexPass(prefix="index", index=1, rgb=[1.0, 0.25, 0])
    ],
    frame_length=5
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
