# Blender 5 compatibility and pass semantics

## Compositor output

Blender 5.1 uses `scene.compositing_node_group` when `scene.node_tree` is unavailable. The node group needs an output interface socket and an active `NodeGroupOutput`; otherwise File Output nodes may not evaluate.

BlendGen uses this order:

1. Enable all requested view-layer passes.
2. Create and connect all File Output nodes.
3. Render once.
4. Use the individual files when every File Output item exists.
5. If files are absent and the passes are raw, save the existing Render Result as one temporary multilayer EXR, extract each configured individual output with OpenImageIO, and delete the temporary file.

Do not choose the fallback merely because the scene uses Blender 5's group compositor. Direct output works for many scenes and both Cycles and Eevee.

The fallback deliberately rejects passes containing compositor transformations. Replaying arbitrary compositor graphs during channel extraction could silently change semantics.

## Raw channel schema

Match channel suffixes rather than assuming a view-layer name:

- Color: `Combined.R`, `.G`, `.B`, `.A`
- Alpha: `Combined.A`
- Depth: `Depth.Z`
- Normal: `Normal.X`, `.Y`, `.Z`
- Optical flow: `Vector.X`, `.Y`, `.Z`, `.W`
- Material ID: `Material Index.X`

Normals and vectors are signed floats. Material IDs are integral values stored in float channels. Metric depth normally uses a large background sentinel.

## Alpha and background

`Background.ALPHA` enables useful Combined alpha but makes the world transparent. `Background.SKY` keeps the visible world but normally makes Combined alpha opaque.

Choose the desired semantics explicitly. Surface presence can be derived from valid Z for opaque geometry, but this is not volumetric transmittance alpha.

## Material indices

Native `Material Index` follows authored ray coverage. Transparent, dithered, and volumetric materials may alternate between exact ID zero and exact positive IDs. Rounding or denoising does not correct that semantic coverage.

Opaque replacement materials provide hard labels but change the scene and require a separate, explicit render. Never present that as a standard pass obtained from the beauty integration.

## Optical-flow boundaries

Vector-pass semantics depend on adjacent frames. Render guard frames when downstream code needs centered temporal support at the requested range boundaries. Store XYZW losslessly; colorized XY flow is only a preview.

## Verification

- Require every manifest path to exist.
- Check expected resolution and channel count.
- Confirm temporary fallback EXRs are removed after successful extraction.
- Verify transformed passes used the direct compositor path.
- Inspect a moving frame for nonzero flow.
- Inspect transparent or volumetric regions before accepting material and alpha semantics.
