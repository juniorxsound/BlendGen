# Getting started
To quickly get started clone the latest master branch 
```sh
git clone https://github.com/juniorxsound/BlendGen.git
```
Or [download the latest release](https://github.com/juniorxsound/BlendGen/releases/latest)

If you want to run BlendGen with GPU support make sure to [install Docker 19.03](https://docs.docker.com/install/) or newer and [nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-docker#quickstart). Otherwise, install [Docker 18 or newer](https://docs.docker.com/install/)

> GPU acceleration is not supported on macOS

# Installation
Once all that is done simply `cd` into the folder and run `make build`. If `make` is not available you can run the full `docker` command ([found](https://github.com/juniorxsound/BlendGen/blob/master/Makefile#L17) in the `Makefile`)
```sh
cd BlendGen && make build
```

If everything went well, you should be good to go and you can skip to [create a dataset](#create-a-dataset) 🚀

### Installing using Docker directly
If you are unable to run `make` or interested in using Docker directly you can use the following commands to install the container. `cd` into the folder and use:
For GPU support run
```sh
docker build -f docker/Dockerfile.gpu -t juniorxsound/blendgen:latest ./
```

Otherwise run
```sh
docker build -f docker/Dockerfile.cpu -t juniorxsound/blendgen:latest ./
```

# Create a dataset
Let's create some data. Think of BlendGen as a rendering pipeline for datasets therefore, we assume you have a 3D scene that could be rendered. In this section we will use the sample `.blend` files inside the examples folder, but you can use the same approach to load in files you have created in the same way.

> If you are looking for good Blender scenes to experiement with make sure you checkout [Blend Swap](https://www.blendswap.com/)

We start by importing the components of BlendGen we would need to generate a simple image
```python
from blendgen.session import Session
from blendgen.passes.color import ColorPass
from blendgen.image_attribute_props import ImageAttributeOutputType
```
- `Session` is used to manage the dataset creation pipeline
- `ColorPass` is used when we want to render out the camera's color image (for more see the [more options](#more-options) section)
- `ImageAttributeOutputType` is an enum that lets us choose which image file type we want to render

Next, we define the session and create the render pass we want to render out
```python
sess = Session(
    passes=[
        ColorPass(prefix="color",
                  output_type=ImageAttributeOutputType.PNG)
    ]
)
```
- `prefix` is used to prepend a subfolder in the dataset so we don't render all the images into the same folder
- `outout_type` is where we select the desired format (for options see [`ImageAttributeOutputType`](https://github.com/juniorxsound/BlendGen/blob/master/blendgen/image_attribute_props.py))

All we need to do now is to run the session
```python
sess.run()
```

If nothing blew up, you should have an image in `data/toy_dataset/color`


> Everything shown above can be found in the [`simple.py`](https://github.com/juniorxsound/BlendGen/blob/master/examples/simple.py) example. You can run that by calling `make simple`

For more BlendGen recepies [see the examples folder](https://github.com/juniorxsound/BlendGen/tree/master/examples)

## Selecting a renderer

`Renderer` accepts an explicit backend. Cycles is the default; its sample count
and device are configured only on `CyclesBackend`. Eevee has its own small,
engine-specific configuration surface:

```python
from blendgen.renderer import Renderer
from blendgen.renderers import EeveeBackend

renderer = Renderer(backend=EeveeBackend(samples=16), passes=[...])
```

The same color, alpha, depth, normal, and optical-flow pass classes work with
both backends. Material-index output is deliberately rejected for Eevee until
it can be reliably produced by the supported Blender runtime.

# More options

# Compatability
BlendGen was tested on:
- [x] macOS 10.13 / 10.14 using CPU acceleration
- [x] Ubuntu 16-18 using CPU acceleration
- [x] Ubuntu 16-18 using GPU 
> Since Blender and Docker support Windows you should be able to run BlendGen on Windows as well (contribution is wellcome)
