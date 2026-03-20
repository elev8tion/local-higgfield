# Open Higgsfield AI: Comfy Compatibility Matrix

Last updated: 2026-03-19

This document answers one practical question:

- which target workflows can already run through the current `ComfyUI` bridge
- which ones need small adaptation
- which ones need backend changes before they are worth wiring in

The current bridge means:

- backend job -> runner command -> `ComfyUI /prompt`
- poll `ComfyUI /history/<prompt_id>`
- download the first returned `video`, `gif`, or `image`
- save that as the primary backend result

Source of truth for the current bridge:

- [backend/runners/comfy_media_runner.py](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/runners/comfy_media_runner.py)
- [backend/workflows/comfy/README.md](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/workflows/comfy/README.md)

## Current Bridge Capabilities

The current bridge already supports:

- one workflow template per job type
- exported API workflow JSON
- placeholder substitution for:
  - prompt
  - resolution
  - aspect ratio
  - width / height
  - image path
  - video path
  - audio path
  - output filename/path
  - arbitrary `params.<name>`
- polling remote `ComfyUI` completion
- downloading the first media output

The current bridge does not yet natively support:

- multiple outputs we care about in one job
- multi-asset upload into Comfy input folders
- websocket progress streaming
- explicit queue cancellation
- dedicated typed jobs for `video.extend`, captions, lyrics, or character replacement
- post-process text assets like `srt`, `ass`, `json`

## Compatibility Scale

- `Works Now`
  - can be wired to the current bridge with exported workflow JSON and current payload shape
- `Small Adapter`
  - current bridge is close, but needs a minor backend addition or cleaner payload mapping
- `Needs Backend Work`
  - would be awkward or fragile without adding new job types, extra asset handling, or richer result handling

## Matrix

| Feature / Workflow | Primary Model Family | Current Job Mapping | Bridge Status | Why |
| --- | --- | --- | --- | --- |
| Text-to-video | `Wan 2.2 TI2V-5B`, `Wan 2.2 T2V`, `LTX-2` | `video.generate` | `Works Now` | Prompt-only workflows fit the current bridge well. |
| Image-to-video | `Wan 2.2 I2V`, `LTX-2`, `LTX-2.3` | `video.animate_image` | `Works Now` | Current payload already provides image asset + prompt. |
| Video-to-video / transform | `Wan 2.1 VACE`, `LTX-2`, `CogVideoX` | `video.transform` | `Works Now` | Current payload supports a source video and prompt. |
| Portrait lipsync | `MuseTalk` | `lipsync.image_audio` | `Works Now` | Image + audio input shape already exists. |
| Video lipsync | `LatentSync` | `lipsync.video_audio` | `Works Now` | Video + audio input shape already exists. |
| Audio-driven video | `Wan 2.2 S2V` | temporary `video.generate` or `video.animate_image` | `Small Adapter` | Needs a clean feature contract for audio-driven generation, but can start with `params` + audio path. |
| Character replacement | `Wan 2.2 Animate` | temporary `video.animate_image` or `video.transform` | `Small Adapter` | Likely needs more than one input/control asset, but a first exported workflow can still be tested. |
| First/last-frame control | `Wan 2.1 FLF2V`, `LTX` | none yet | `Small Adapter` | Current bridge can pass params, but we need typed support for start/end frame assets or extra image slots. |
| Video extension | `Wan 2.2 Animate Extend`, `Wan 2.2 S2V Extend` | none yet | `Needs Backend Work` | This should become explicit `video.extend` with previous clip + continuation settings. |
| Audio-driven creator video from still image | `Wan 2.2 S2V` | hybrid | `Small Adapter` | Needs image + audio + prompt, which the bridge can handle if we add a clearer mapping. |
| Captions generation | `WhisperX` | none yet | `Needs Backend Work` | Output is text/subtitle assets, not just a media file. |
| Lyrics on screen | `WhisperX` + lyric alignment + render | none yet | `Needs Backend Work` | Needs subtitle/text artifacts and likely a render pass with extra outputs. |
| Character-performance remap | `Wan 2.2 Animate` | none yet | `Needs Backend Work` | Better as its own typed feature instead of hiding it under generic `video.transform`. |

## Target Workflow Decisions

### 1. Start Here

These are the best first Comfy-backed workflows because they already fit the current bridge cleanly:

- `video.animate_image`
  - first target: `Wan 2.2 I2V`
- `lipsync.video_audio`
  - first target: `LatentSync`
- `lipsync.image_audio`
  - first target: `MuseTalk`
- `video.transform`
  - first target: `Wan 2.1 VACE` or an easier temporary transform workflow

### 2. Second Wave

These are good next steps once the first wave is stable:

- audio-driven creator video
  - `Wan 2.2 S2V`
- character replacement
  - `Wan 2.2 Animate`
- first/last-frame controlled generation
  - `Wan 2.1 FLF2V`

These likely need only modest payload and workflow-template improvements, not a full architecture change.

### 3. New Typed Features

These should not be forced into current generic job types long-term:

- `video.extend`
- `caption.generate`
- `lyrics.generate`
- character replacement as an explicit feature
- audio-driven creator video as an explicit feature

## What A Workflow Must Do To Work Now

A workflow is a good fit for the current bridge if:

1. it can be exported from `ComfyUI` as API JSON
2. it can accept inputs through placeholder-filled node values
3. it produces one main media output in Comfy history
4. we only need one primary output file for the current backend result

If a workflow requires:

- multiple separately-managed outputs
- several uploaded side assets
- text/subtitle outputs
- custom progress reporting
- cancellation semantics

then it should be treated as either `Small Adapter` or `Needs Backend Work`.

## Required Backend Additions For Broader Coverage

### Small additions

- richer placeholder set for multiple image/reference slots
- clearer `params` conventions for seeds, guidance, duration, fps, and model toggles
- optional selection of a preferred output node per workflow
- optional additional downloaded assets from Comfy history

### Bigger additions

- new typed jobs:
  - `video.extend`
  - `caption.generate`
  - `lyrics.generate`
  - character replacement
  - audio-driven creator video
- subtitle/text asset support in `JobResult`
- optional upload-to-Comfy-input-folder flow instead of only local-file-path substitution
- websocket progress and cancellation support

## Recommended Implementation Order

1. Export and wire one real `Wan 2.2 I2V` workflow to `video.animate_image`
2. Export and wire one real `LatentSync` workflow to `lipsync.video_audio`
3. Export and wire one real `MuseTalk` workflow to `lipsync.image_audio`
4. Add a first `Wan 2.2 S2V` workflow using a temporary mapping
5. Add typed `video.extend`
6. Add typed captions and lyrics jobs

## Bottom Line

Using `ComfyUI` this way is the right choice for now because:

- it avoids repeated native-model build pain on rented GPUs
- it lets one private template hold models and custom nodes
- it keeps your chat interface as the only user-facing UI
- it is already a clean fit for your first wave of workflows

It is not universal yet.

The current bridge is best understood as:

- excellent for first-wave single-output media workflows
- expandable for second-wave creator workflows
- not yet the finished contract for every future feature
