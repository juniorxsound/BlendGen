# BlendGen dataset API

## Complete dataset file

```python
from pathlib import Path

import bpy

from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.passes.alpha import AlphaPass
from blendgen.passes.base import ImageOutputType
from blendgen.passes.color import ColorPass
from blendgen.passes.depth import DepthPass
from blendgen.passes.index import RawMaterialIndexPass
from blendgen.passes.normal import NormalPass
from blendgen.passes.opticalflow import OpticalFlowPass
from blendgen.renderer import Background, Renderer
from blendgen.renderers import CyclesBackend, CyclesDevice
from blendgen.session import Session


OUTPUT = "/data/output/"

if bpy.context.scene.camera is None:
    raise RuntimeError("The scene has no active camera")
Path(OUTPUT).mkdir(parents=True, exist_ok=True)

passes = [
    ColorPass(prefix="color", output_type=ImageOutputType.PNG),
    AlphaPass(prefix="alpha", output_type=ImageOutputType.PNG),
    DepthPass(prefix="depth", output_type=ImageOutputType.EXR),
    NormalPass(prefix="normal", output_type=ImageOutputType.EXR),
    OpticalFlowPass(prefix="flow", output_type=ImageOutputType.EXR),
    RawMaterialIndexPass(
        prefix="material_index", output_type=ImageOutputType.EXR
    ),
]

renderer = Renderer(
    backend=CyclesBackend(samples=8, device=CyclesDevice.GPU),
    background=Background.ALPHA,
    resolution_x=640,
    resolution_y=360,
    resolution_percentage=100,
    output_base_path=OUTPUT,
    passes=passes,
)

dataset = Dataset(
    prefix="",
    dataset_name="My BlendGen dataset",
    output_dir=OUTPUT,
    filename="blendgen_dataset",
    output_type=DatasetOutputType.JSON,
)

session = Session(
    renderer=renderer,
    dataset=dataset,
    output_dir=OUTPUT,
    frame_start=1,
    frame_length=192,
)

print(session.info)
session.run()
```

The scene loaded by Blender supplies the active camera.

## Backends

Use `CyclesBackend(samples=..., device=CyclesDevice.GPU)` with Docker `--gpus all`. Use `CyclesDevice.CPU` without NVIDIA passthrough.

Use `EeveeBackend(samples=...)` for Eevee-supported passes. The current Blender 5 backend rejects material-index passes because Eevee does not expose them reliably.

## Pass formats

`ImageOutputType` supports `PNG`, `JPEG`, `TIFF`, and `EXR`.

- `ColorPass`: PNG for display color; EXR for scene-linear RGBA.
- `AlphaPass`: PNG or EXR.
- `DepthPass`: EXR for unmodified metric Z. Mapping/inversion options are visualization transforms.
- `NormalPass`: EXR because components are signed.
- `OpticalFlowPass`: EXR because components are signed and may exceed one.
- `RawMaterialIndexPass`: EXR for exact unmodified numeric IDs.
- `MaterialIndexPass`: a compositor-generated mask for one selected material ID.

## Callbacks and attributes

Use `Session` callbacks for procedural changes:

- `on_start`
- `on_before_new_frame`
- `on_after_new_frame`
- `on_complete`

Use `Dataset.add_attribute()` during a frame callback to attach annotations to the next frame record. Keep rendering in `Session.run()` so every declared pass stays synchronized.

## Output contract

Each frame record contains the final individual path for every pass. BlendGen verifies the file exists before adding it to the dataset index. On Blender 5, raw passes may use an internal multilayer Render Result fallback; the temporary bridge is deleted after successful extraction and is never a second render.
