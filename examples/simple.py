from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.passes.alpha import AlphaPass
from blendgen.passes.base import ImageOutputType

'''
A simple example that shows how to render textures using BlendGen
To run this example use `make simple` or the docker command
Inside the Makefile
'''

# Create the session
sess = Session(
    # Define the render passes
    passes=[
        ColorPass(prefix="color",
                  output_type=ImageOutputType.PNG),
        AlphaPass(prefix="alpha")
    ],
    frame_length=1
)

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
