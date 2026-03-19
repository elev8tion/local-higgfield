# Open Higgsfield AI: Feature Board and Model Plan

Last updated: 2026-03-18

This document replaces the earlier generic feature-to-model sheet.

The new goal is not just “cover image, video, and lipsync.”
The goal is to support realistic creator-style output:

- ultra-real image -> creator video
- music-video style motion from stills
- UGC / TikTok style clips
- character replacement
- audio-driven performance
- direct lipsync where needed
- video continuation / extension

## Format Priority

Vertical creator output is a first-class requirement.

- default creator-video target aspect ratio: `9:16`
- every major creator-facing video feature should explicitly support `9:16`
- secondary aspect ratios:
  - `16:9`
  - `1:1`
- do not treat `9:16` as optional polish later; it is a primary format target

## Core Foundation

This is the actual foundation shortlist to build around first:

- `Wan 2.2 S2V`
- `Wan 2.2 Animate`
- `Wan 2.2 I2V`
- `Wan 2.1 VACE`
- `LTX-2 / LTX-2.3`
- `LatentSync`
- `MuseTalk`

These are the priority families because they map better to creator-style output than a generic “text-to-video only” stack.

## Feature Board

### 1. Audio-Driven Creator Video

- Goal:
  - drive human-looking video from audio
  - support music-video style performance
  - support expressive movement, not only mouth motion
- Primary:
  - `Wan 2.2 S2V`
- Backup:
  - `LTX-2.3`
- Why:
  - `Wan 2.2 S2V` is the strongest fit for audio-driven video generation
  - this is closer to your “real creator” goal than a plain lipsync model
- Extension support:
  - yes, confirmed via `Video S2V Extend`
- Implementation note:
  - this should eventually become its own typed feature, not be hidden under plain lipsync

### 2. Ultra-Real Image to Creator Video

- Goal:
  - start from a strong still image and animate it into a convincing creator-style clip
- Primary:
  - `Wan 2.2 I2V`
- Backup:
  - `LTX-2 / LTX-2.3`
- Why:
  - this is the direct path for turning your ultra-real images into clips
  - `LTX` stays valuable for faster iteration and controllable workflows
- Extension support:
  - partially, through Wan continuation / first-last-frame style workflows depending the exact setup
- Implementation note:
  - this maps most directly onto the current `video.animate_image` job type

### 3. Character Replacement / Character Performance

- Goal:
  - take motion/performance and remap it into a different character or creator identity
- Primary:
  - `Wan 2.2 Animate`
- Backup:
  - `Wan 2.2 I2V`
- Why:
  - this is the clearest fit for “automatic character replacement”
  - it matches your stated interest directly
- Extension support:
  - yes, confirmed via `Video Extend`
- Implementation note:
  - this likely deserves its own future typed job, not just a variant of image-to-video

### 4. Video Extension / Continuation

- Goal:
  - make clips longer
  - continue motion naturally
  - extend sequences for creator content and music videos
- Primary:
  - `Wan 2.2 Animate`
- Backup:
  - `Wan 2.2 S2V`
- Secondary backup:
  - `LTX-Video` multi-frame control
- Why:
  - Wan has the strongest confirmed explicit extend support in the current source pass
- Extension support:
  - yes, explicitly confirmed
- Implementation note:
  - this should become a future `video.extend` job type

### 4b. External Premium Extend Watchlist

- Candidate:
  - `Seedance 2.0 Extend`
- Why it matters:
  - it appears strong for coherent continuation and longer clip generation
  - it is a serious future premium API-backed extension path if quality is materially above the open stack
- Important distinction:
  - this is not part of the open/local foundation shortlist
  - treat it as an external premium integration target, not the base system
- Suggested use:
  - compare it later against `Wan 2.2 Animate` / `Wan 2.2 S2V` extension quality

### 5. First/Last-Frame Controlled Video

- Goal:
  - shape beginning and ending of a clip
  - create more intentional shots and transitions
- Primary:
  - `Wan 2.1 FLF2V`
- Backup:
  - `LTX-Video`
- Why:
  - this is the best path for controlled transitions and sequence design
- Extension support:
  - yes, by chaining controlled generation
- Implementation note:
  - ideal for building longer music-video or cinematic sequences from multiple shots

### 6. General Video Editing / Video Transformation

- Goal:
  - modify, restyle, clean, or transform source video
  - eventually support higher-level creator editing workflows
- Primary:
  - `Wan 2.1 VACE`
- Backup:
  - `LTX-2`
- Secondary backup:
  - `CogVideoX` V2V path
- Why:
  - your current `video.transform` feature should evolve into a real general editing path
  - `Wan 2.1 VACE` is the strongest candidate for that direction
- Extension support:
  - not the main purpose
- Implementation note:
  - the current watermark-remover style placeholder should be treated as one use case inside this broader feature family

### 7. Direct Creator Speech / Lip Sync

- Goal:
  - accurate speech sync when direct mouth matching matters
  - use when the feature is specifically about speaking accuracy
- Primary:
  - `LatentSync`
- Backup:
  - `MuseTalk`
- Fallback:
  - `Wav2Lip`
- Why:
  - `LatentSync` is the stronger general lipsync candidate
  - `MuseTalk` remains excellent for portrait/talking-face cases
- Extension support:
  - not the main purpose
- Implementation note:
  - keep this separate from audio-driven creator-performance generation

### 8. Portrait Talking Video

- Goal:
  - generate a believable talking portrait from image + audio
- Primary:
  - `MuseTalk`
- Backup:
  - `LatentSync`
- Fallback:
  - `Wav2Lip`
- Why:
  - this is still useful, but it is no longer the center of the system
- Extension support:
  - not the main purpose
- Implementation note:
  - this remains a sub-feature, not the flagship direction

### 9. Auto Captions

- Goal:
  - generate clean burned-in or exportable captions automatically
  - support creator, UGC, and promo workflows
- Primary stack:
  - `WhisperX`
- Backup:
  - `stable-ts`
- Render layer:
  - `ffmpeg` subtitle burn-in or export to `SRT` / `ASS`
- Why:
  - captions are not a video-generation-model feature
  - they should be treated as a post-processing transcription pipeline
- Implementation note:
  - this should become a future post-processing job such as `caption.generate`

### 10. Auto Lyrics On Screen

- Goal:
  - generate timed lyric overlays for music-driven videos
  - support karaoke-style or styled lyric presentation
- Primary stack:
  - `python-lyrics-transcriber`
- Backup:
  - `WhisperX` or `stable-ts` plus custom lyric matching
- Render layer:
  - `ASS` subtitle generation, then burn-in via `ffmpeg`
- Why:
  - lyrics are a separate alignment/rendering problem, not just generic captions
  - creator music-video workflows need this as a first-class post feature
- Implementation note:
  - this should become a future post-processing job such as `lyrics.generate`

## Image Layer

Video is now the center of the feature plan, but the image layer still matters.

### 11. Premium Image Generation

- Primary:
  - `HunyuanImage-3.0`
- Backup:
  - `FLUX.1-dev`
- Why:
  - build ultra-real base images for downstream creator-video workflows

### 12. Premium Image Editing / Revision

- Primary:
  - `FLUX.1-Kontext-dev`
- Backup:
  - `Qwen-Image-Edit`
- Why:
  - revise, restyle, and clean source images before they enter the video pipeline

## What This Means for Your App

The app should no longer be thought of as:

- image studio
- video studio
- lipsync studio

It should eventually become:

- creator motion from image
- audio-driven creator performance
- character replacement
- video continuation
- controlled transition generation
- direct speech sync
- auto captions
- auto lyrics
- video editing / cleanup

The current studio layout can stay for now, but the model plan is moving toward these capability buckets.

## Suggested Rollout Order

1. `Wan 2.2 I2V`
2. `Wan 2.2 S2V`
3. `Wan 2.2 Animate`
4. `LatentSync`
5. `Wan 2.1 VACE`
6. `LTX-2 / LTX-2.3`
7. `WhisperX` caption pipeline
8. `python-lyrics-transcriber` lyric pipeline
9. `HunyuanImage-3.0`
10. `FLUX.1-Kontext-dev`

Why this order:

- it prioritizes creator-style output first
- it prioritizes audio-driven and image-driven video first
- it adds captions and lyrics as real creator deliverables, not afterthoughts
- it delays generic image work behind the more important creator-video pipeline

## Confirmed Model/Workflow Notes

- `Wan 2.2 Animate`
  - confirmed extension support
- `Wan 2.2 S2V`
  - confirmed audio-driven generation and extend support
- `Wan 2.1 FLF2V`
  - confirmed first/last-frame workflow
- `LTX-Video`
  - confirmed multi-frame control support

## Immediate Next Planning Step

Create the hardware board:

- feature
- primary model
- backup model
- VRAM target
- likely runner type
- deployment risk
- best first rented GPU shape
