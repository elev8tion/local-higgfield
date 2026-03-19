# Open Higgsfield AI: Hardware Board

Last updated: 2026-03-18

This document translates the creator-focused feature board into practical GPU sizing guidance.

## How To Read This

- `Official / documented`:
  - directly stated by the model repo or Comfy docs
- `Practical target`:
  - the GPU class I would actually target for a smooth first deployment
- `Inference mode`:
  - the likely runner shape inside our pipeline

When exact numbers are not cleanly documented by the model authors, I mark them as practical targets instead of pretending they are hard guarantees.

## Recommended GPU Tiers

### Tier A: Bring-up / fast iteration

- GPU class:
  - `24GB`
- Best use:
  - `Wan2.2-TI2V-5B`
  - `LatentSync`
  - `MuseTalk`
  - `WhisperX`
  - lighter `LTX` workflows
- Good for:
  - proving the pipeline
  - creator-video experiments
  - captions / lyrics / lipsync services
- Not ideal for:
  - the heaviest premium Wan and Hunyuan video stacks

### Tier B: Serious single-GPU creator stack

- GPU class:
  - `48GB`
- Best use:
  - `Wan 2.2 Animate`
  - `Wan 2.2 S2V`
  - `Wan 2.1 VACE`
  - `LTX-2 / LTX-2.3`
- Good for:
  - premium creator-video features on one machine
  - extension and longer clip workflows

### Tier C: Top-tier premium deployment

- GPU class:
  - `80GB`
- Best use:
  - `Wan 2.2 14B family`
  - `HunyuanVideo`
  - heavier image/video combinations on one service
- Good for:
  - flagship deployment
  - fewer compromises on quality or offload tricks

### Tier D: Multi-GPU premium image system

- GPU class:
  - `3x80GB` minimum
- Best use:
  - `HunyuanImage-3.0`
- Good for:
  - highest-end image generation layer
- Important:
  - this is not the first rented machine unless image is your immediate main target

## Feature-to-Hardware Matrix

| Feature | Primary Model | Backup | Official / Documented | Practical Target | Inference Mode | Notes |
|---|---|---|---|---|---|---|
| Audio-driven creator video | `Wan 2.2 S2V 14B` | `LTX-2.3` | Comfy docs confirm `wan2.2_s2v_14B_fp8_scaled` and extension workflow support | `48GB` preferred, `80GB` premium | remote video runner / Comfy workflow API | Strong fit for music-video and creator-performance generation |
| Ultra-real image to creator video | `Wan 2.2 I2V 14B` | `LTX-2 / 2.3` | Wan 2.2 family officially supported in Comfy docs | `48GB` preferred, `80GB` premium | remote video runner / Comfy workflow API | Core path for still image -> creator clip |
| Character replacement | `Wan 2.2 Animate 14B` | `Wan 2.2 I2V` | Comfy docs confirm native workflow and extension support | `48GB` preferred | remote video runner / Comfy workflow API | Best match for automatic character replacement |
| Video extension | `Wan 2.2 Animate` | `Wan 2.2 S2V`, `LTX-Video` | Comfy docs confirm explicit extend nodes for Wan Animate and S2V | `48GB` preferred | remote video runner / Comfy workflow API | This should become future `video.extend` |
| First/last-frame controlled video | `Wan 2.1 FLF2V` | `LTX-Video` | Comfy docs confirm FLF2V workflow | `24GB-48GB` | remote video runner / Comfy workflow API | Strong for transitions and structured shot planning |
| General video editing / transform | `Wan 2.1 VACE` | `LTX-2`, `CogVideoX` | Comfy docs show VACE workflows and measured 4090 timings at 720x1280 and 640x640 | `48GB` preferred | remote video runner / Comfy workflow API | Best path for true `video.transform` evolution |
| Direct speech / creator lipsync | `LatentSync 1.6` | `MuseTalk`, `Wav2Lip` | Official repo states minimum inference VRAM: `18GB` for 1.6, `8GB` for 1.5 | `24GB` | remote lipsync runner / native Python runner | Best direct lipsync candidate |
| Portrait talking video | `MuseTalk` | `LatentSync`, `Wav2Lip` | Official repo says tested on `4GB` VRAM laptop GPU in fp16 mode | `8GB-16GB` | remote lipsync runner / native Python runner | Lighter, portrait-specific talking video path |
| Auto captions | `WhisperX` | `stable-ts` | WhisperX docs recommend reducing batch size/model size for memory; third-party self-hosting measurements place `large` + diarization around `14GB` | `12GB-24GB` | post-process runner | Treat as post pipeline, not generation model |
| Auto lyrics | `python-lyrics-transcriber` + `WhisperX` | `WhisperX` + custom alignment | Tool outputs `ASS`, `LRC`, review UI, and burn-in friendly subtitle assets | `CPU` or `8GB+ GPU` if using WhisperX on GPU | post-process runner | This is a render/alignment feature, not a video model |
| Premium image generation | `HunyuanImage-3.0` | `FLUX.1-dev` | Official repo states `≥3x80GB`, `4x80GB recommended` | `3x80GB+` | dedicated image runner | Heavy premium image layer |
| Premium image editing / revision | `FLUX.1-Kontext-dev` | `Qwen-Image-Edit` | No clean official VRAM figure found in this pass; FLUX.1-dev community discussion suggests ~`22GB` baseline at bf16/fp16 before offloading | `24GB-48GB` | dedicated image runner | Strong edit/revision layer; treat 24GB as floor |
| Unified practical video bring-up | `Wan2.2-TI2V-5B` | `LTX-2B distilled` | Comfy docs say Wan `TI2V-5B` fits well on `8GB` VRAM with native offloading | `24GB` for comfortable service deployment | remote video runner / Comfy workflow API | Best early all-in-one Wan deployment target |

## Source Notes

### Official / near-official figures used

- `Wan2.2-TI2V-5B`
  - Comfy docs: fits well on `8GB` VRAM with native offloading
  - Source: [Wan 2.2 docs](https://docs.comfy.org/tutorials/video/wan/wan2_2)
- `Wan2.2-S2V`
  - Comfy docs confirm native support, `14B fp8` workflow, and extension chunks of `77` frames
  - Source: [Wan 2.2 S2V docs](https://docs.comfy.org/tutorials/video/wan/wan2-2-s2v)
- `Wan2.2 Animate`
  - Comfy docs confirm native support and extension workflow
  - Source: [Wan 2.2 Animate docs](https://docs.comfy.org/tutorials/video/wan/wan2-2-animate)
- `Wan2.1 VACE`
  - Comfy docs provide example timings on `4090`
  - Source: [Wan 2.1 VACE docs](https://docs.comfy.org/tutorials/video/wan/vace)
- `LTX-Video`
  - ComfyUI wrapper mentions `32GB+ VRAM`
  - Source: [ComfyUI-LTXVideo](https://github.com/Lightricks/ComfyUI-LTXVideo)
- `HunyuanVideo`
  - official repo states minimum `60GB` for `720x1280x129f` and `45GB` for `544x960x129f`
  - Source: [HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo)
- `HunyuanVideo-1.5`
  - official repo states minimum `14GB` with offloading enabled
  - Source: [HunyuanVideo-1.5](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)
- `HunyuanImage-3.0`
  - official repo states `≥3x80GB`, `4x80GB recommended`
  - Source: [HunyuanImage-3.0](https://github.com/Tencent-Hunyuan/HunyuanImage-3.0)
- `LatentSync 1.6`
  - official repo states minimum inference VRAM `18GB`
  - Source: [LatentSync](https://github.com/bytedance/LatentSync)
- `MuseTalk`
  - official repo says tested on `4GB` VRAM laptop GPU
  - Source: [MuseTalk](https://github.com/TMElyralab/MuseTalk)
- `WhisperX`
  - official repo gives memory reduction guidance; third-party self-hosting measurements indicate about `14GB` for large models with diarization
  - Sources: [WhisperX](https://github.com/m-bain/whisperX), [whisperx-asr-service](https://github.com/murtaza-nasir/whisperx-asr-service)
- `python-lyrics-transcriber`
  - outputs `ASS`, `LRC`, and review UI
  - Source: [python-lyrics-transcriber](https://github.com/nomadkaraoke/python-lyrics-transcriber)

## Practical Rental Recommendation

If you want one serious first rented machine for your creator-first roadmap:

- Best first target:
  - `48GB` GPU
- Why:
  - enough headroom for serious Wan creator-video work
  - enough for `LatentSync`
  - enough for caption and lyric post-processing
  - avoids overcommitting to the extremely heavy premium image stack on day one

If you want the most aggressive flagship path:

- pair:
  - one `48GB-80GB` video machine
  - one separate heavy image machine later

If you want the cheapest realistic first deployment:

- start with:
  - `24GB` GPU
- and target:
  - `Wan2.2-TI2V-5B`
  - `LatentSync`
  - `MuseTalk`
  - `WhisperX`

## Immediate Next Action

Choose one of these deployment starting points:

1. `24GB bring-up tier`
2. `48GB creator-first tier`
3. `80GB premium video tier`
4. `multi-GPU premium image tier`
