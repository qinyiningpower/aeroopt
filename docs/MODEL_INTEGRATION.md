# Connecting the research model

The original research model is deliberately outside this repository. The runnable application consumes its exported results; no dummy predictor is presented as the real model.

## Recommended boundary

Keep model code in a separate research repository. Store checkpoints in an appropriate artifact repository or institutional storage, subject to the paper's release policy. This application needs a small export, not the training environment or the full dataset.

For each case, export:

1. Before and after VTP meshes with matching point correspondence, coordinates, and a scalar `pressure` point field.
2. Optional scalar displacement magnitude in `shape_displacement`; otherwise the processor computes Euclidean displacement.
3. Drag values with units/conventions, solver or predictor identity, dataset ID, checkpoint/version, and evaluation conditions recorded separately.
4. Before/after pressure and geometry PNGs rendered with consistent camera and color scales.

Run the optional processor:

```bash
pip install -r pipeline/requirements.txt
python pipeline/generate_region_data.py --before /path/before.vtp --after /path/after.vtp --output /path/export
```

The output contains `data/shape_regions.json`, `data/pressure_regions.json`, and `raw/vertex_displacement.npy`. It does not estimate drag, generate PNGs, or produce click maps. Assemble those artifacts using the contract in [API.md](API.md), then place them in `backend/data/models/model_XX/`. Add matching frontend images and a selection card if adding cases beyond the seven shipped examples.

## Scientific assumptions

The processor assumes x is vehicle length, z is height, and low x is the front. Front/rear use the outer 25% of the longitudinal extent, roof uses the upper 30% of height, and side contains the remaining points. Roof may overlap front/rear. Equal point counts do not establish mesh correspondence; verify vertex ordering upstream. Scalar field units must be consistent across before and after exports.

The UI's millimeter displacement display assumes input coordinates are meters. Verify that assumption before importing a new source. Pressure values retain their source units/normalization. Regional mean pressure changes are not force integration.

## Future live inference

A later integration can replace file loading with a job API that returns the same case contract. Add job IDs, progress, cancellation, input validation, checkpoint provenance, and explicit failure states. This is an extension plan, not implemented functionality.

You can keep weights private and still demonstrate engineering depth through the export contract, reproducible postprocessing, tests, and a documented example. Publish benchmark claims only once the evaluation setup and results can be independently checked.
