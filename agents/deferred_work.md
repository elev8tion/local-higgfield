# Open Higgsfield AI: Deferred Work

Last updated: 2026-03-18

This file is for work intentionally deferred to save time right now.

## GPU / Template Deferred

- add full lyric toolchain into the first private template
- pre-bake large model families into a heavier second template
- create a dedicated image-focused template for `HunyuanImage-3.0`
- create a separate premium video template for heavier `Wan 14B` and `VACE`

## Backend Deferred

- persistent job store
- queue semantics
- true packaged backend supervision from Electron
- backend-owned full model registry replacing `src/lib/models.js`
- dedicated post-process job types for:
  - `caption.generate`
  - `lyrics.generate`
  - `video.extend`
  - character replacement as its own explicit feature job

## Model / Feature Deferred

- `Seedance 2.0 Extend` premium comparison pass
- full `Wan 2.2 14B` family deployment
- `Wan 2.1 VACE` deployment after first video wave
- `LTX-2 / LTX-2.3` secondary workflow deployment
- `MuseTalk` secondary portrait path if `LatentSync` covers the first need
- premium image system with `HunyuanImage-3.0`

## Operational Deferred

- template automation / image build script
- machine bootstrap script
- formal service manager layout on the rented box
- model download manifest with checksums
- recovery and cleanup scripts for model cache / outputs
