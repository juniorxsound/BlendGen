<h1 align="center">BlendGen</h1>
<div align="center">
    <p>Generate synthetic data for machine learning with Blender ✨</p>
    <a href="https://drone.dv.nyt.net/nytimes/BlendGen" target="_blank"><img alt="Build Status" src="https://drone.dv.nyt.net/api/badges/nytimes/BlendGen/status.svg" /></a>
    <img alt="Python version" src="https://img.shields.io/badge/python-3.6-blue.svg" />
    <img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-yellow.svg" /><br/>
    <img width="750" src="https://github.com/nytimes/BlendGen/blob/dev/docs/assets/cover.gif" /><br/>
    •
    <a target="_blank" href="https://blendgen.xyz">Documentation</a> 📝
    •
    <a target="_blank" href="https://trello.com/b/lTahgAyc">Roadmap</a> 🛣
    •
    <a target="_blank" href="https://github.com/nytimes/BlendGen/tree/dev/examples">Examples</a> 🛠
    •
    <a target="_blank" href="https://github.com/nytimes/BlendGen/tree/dev/notebooks">Notebooks</a> 📓
    •
</div>

## Docker

The CPU image uses Ubuntu 24.04 LTS and its Blender 4.0 package. Both the base
image and Blender package are available natively for `linux/amd64` and
`linux/arm64`, so Docker Desktop on Apple Silicon does not need x86 emulation.

Build the image for the current machine and check the installed Blender version:

```sh
make build
docker run --rm blendgen:latest blender --version
```

Run the test suite or an example:

```sh
make test
make simple
```

Architecture-specific local builds are also available:

```sh
make build-arm64
make build-amd64
```

On a Linux host with `nvidia-smi`, the Makefile automatically selects the GPU
image and passes `--gpus all`. GPU acceleration requires the NVIDIA Container
Toolkit on the host. Docker Desktop on macOS cannot expose the Apple GPU to a
Linux container, so Apple Silicon uses native ARM CPU rendering.
