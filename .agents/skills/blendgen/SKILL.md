---
name: blendgen
description: Author, run, inspect, and validate synthetic Blender datasets with BlendGen. Use when writing a BlendGen dataset Python file, choosing Cycles or Eevee, configuring color, alpha, depth, normals, optical-flow, or material-index passes, running BlendGen in Docker, diagnosing pass outputs, or verifying a rendered dataset.
---

# BlendGen Rendering

Use BlendGen's public `Session`, `Renderer`, backend, pass, and `Dataset` APIs. Keep scene-specific `bpy` changes in callbacks or the dataset file; do not replace BlendGen's render loop with ad hoc per-pass renders.

## Author a dataset

Read [references/api.md](references/api.md) for the current API and complete example. In the dataset file:

1. Select `CyclesBackend` or `EeveeBackend` explicitly.
2. Declare every pass and its `ImageOutputType`.
3. Create one `Renderer` with the active camera, resolution, background policy, output root, and pass list.
4. Create a `Dataset` index and a `Session` with explicit `frame_start` and `frame_length`.
5. Call `Session.run()` once. BlendGen renders all compatible passes together once per frame.

Use `RawMaterialIndexPass` for a full integer ID image. `MaterialIndexPass(index=...)` produces a mask for one ID.

## Run with Docker

GPU/Cycles:

```bash
docker run --rm --gpus all \
  -v "$PWD":/data -w /data blendgen:latest \
  blender --background --python-exit-code 1 /data/scene.blend \
  --python /data/dataset.py
```

CPU or Eevee:

```bash
docker run --rm \
  -v "$PWD":/data -w /data blendgen:latest \
  blender --background --python-exit-code 1 /data/scene.blend \
  --python /data/dataset.py
```

On Apple Silicon, add `--platform linux/amd64` for the Blender 5.1 image. In the dataset file, use `CyclesDevice.CPU` unless the container has NVIDIA GPU passthrough.

## Choose formats intentionally

- Use PNG/JPEG/TIFF for display-oriented color or masks.
- Use EXR for signed, high-dynamic-range, or metric data such as normals, flow, and depth.
- Keep alpha and depth separate: alpha is coverage; depth is camera-space Z.
- Treat videos and colorized previews as visualization, never authoritative training data.

BlendGen first asks Blender's File Output nodes for individual files. If Blender 5 emits none, BlendGen saves the existing Render Result once, extracts raw semantic channels to the configured individual files, and deletes the temporary multilayer EXR. This fallback does not invoke the renderer again.

Read [references/blender5.md](references/blender5.md) before changing compositor integration, channel extraction, or background/material semantics.

## Smoke test and validate

Before a long dataset:

1. Render one representative frame at low resolution.
2. Require one real file per requested pass; manifest entries alone are insufficient.
3. Check resolution, channels, dtype, finite values, and expected ranges.
4. Confirm flow is populated on a moving frame and material IDs belong to the recorded map.
5. Inspect color, alpha, depth, normals, flow, and IDs together for alignment.

Fail the run when an expected pass file is missing. Do not silently substitute stale files or re-render one pass at a time.

## Scene semantics

- `Background.ALPHA` provides transparent film but removes the visible world from Combined color.
- `Background.SKY` preserves the visible world but normally makes Combined alpha opaque.
- Native material indices describe authored shading coverage. Transparent, dithered, and volumetric materials can create stochastic background pixels even when every stored ID is an exact integer.
- A hard opaque material override changes render semantics and requires an explicitly separate render; never hide that cost behind the standard pass API.

Report unresolved textures, linked libraries, Alembic caches, volume objects, and missing cameras before claiming a dataset is complete.
