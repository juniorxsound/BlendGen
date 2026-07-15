from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.passes.base import ImageOutputType

'''
A simple example that shows how to use session callbacks with BlendGen
To run this example use `make callbacks` or the docker command
Inside the Makefile
'''

# Create the session
sess = Session(
    # Define the render passes
    passes=[
        ColorPass(prefix="color",
                  output_type=ImageOutputType.PNG)
    ],
    frame_length=1
)


def start():
    print('Started creating the dataset')


def complete():
    print('Finished creating the dataset')


def before_render(sess):
    print('About to render a new frame')


def after_render(sess):
    print('Just rendered a new frame')


# Attach the callbacks to the session
sess.on_start = start
sess.on_complete = complete
sess.on_before_new_frame = before_render
sess.on_after_new_frame = after_render

# Pretty print the session information
print(sess.info)

# Run the session and render em' all
sess.run()
