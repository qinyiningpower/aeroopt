# Dataset provenance

The project owner confirmed the [DrivAerNet collection on Harvard Dataverse](https://dataverse.harvard.edu/dataverse/DrivAerNet) as the dataset source. This collection link identifies the source collection; the exact dataset release, DOI, and per-case sample mapping remain to be documented. Harvard Dataverse is the hosting repository.

Source collection supplied by the project owner and related project references:

- [DrivAerNet collection — Harvard Dataverse](https://dataverse.harvard.edu/dataverse/DrivAerNet)
- [Official DrivAerNet project](https://github.com/Mohamedelrefaie/DrivAerNet)
- [DrivAerNet paper](https://arxiv.org/abs/2403.08055)
- [DrivAerNet++ paper](https://arxiv.org/abs/2406.09624)

The official project identifies DrivAerNet++ dataset terms as CC BY-NC 4.0. The exact release, dataset DOI, original sample mapping, and processing provenance for these local exports are not yet confirmed. Do not infer them from file names alone. Raw meshes and full datasets are excluded.

## Included artifacts

- `backend/data/models`: seven JSON case exports and pressure renderings copied from the supplied AI application.
- `frontend/images`: vehicle geometry and pressure renderings from the supplied frontend archive.
- `pipeline/generate_region_data.py`: consolidated from the first supplied case's processor, with configurable input paths and validation added for publication.

The frontend archive and backend export folders contain separately named images. Their pairing follows the supplied model indices; visual/physical equivalence has not been independently established. The third raw demo folder uses files named `4_before.vtp` and `4_after.vtp`, while backend model 03 has a different case identity. Accordingly, raw demo folders were not merged into the public application.

## Before using results in a paper or benchmark

Record the exact dataset DOI/version, original sample ID, transformations, units, mesh correspondence, model checkpoint, drag definition, and evaluation procedure. Compare rendered images against their source cases. Resolve team and image attribution before applying any broad license.

All displayed drag improvements are existing demo metadata. They are not a reproduced scientific result of this public release.
