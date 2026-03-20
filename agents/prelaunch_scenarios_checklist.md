# Open Higgsfield AI: Prelaunch Scenarios Checklist

Last updated: 2026-03-19

This checklist is the "did we miss anything important before launch?" pass for the first private Vast `ComfyUI` worker.

## Covered Scenarios

### 1. GPU / image compatibility

- `RTX 5090` compatibility risk checked
- Vast 5-series guidance checked
- launch plan now assumes Vast's recommended `ComfyUI` template and automatic image versioning

### 2. Instance type risk

- `On-demand` selected as the default
- `Interruptible` explicitly excluded for first bring-up

### 3. Persistence risk

- container storage persistence vs destruction behavior checked
- volume survival constraints checked
- plan now assumes container storage survives stop, not destroy

### 4. Environment variable visibility

- Vast docs confirm SSH/Jupyter sessions may not automatically see custom env vars
- provisioning script now exports key values into `/etc/environment`

### 5. Port / access path risk

- Vast `OPEN_BUTTON_PORT` path checked
- plan now standardizes on internal `18188` for `ComfyUI`

### 6. Provisioning path

- Vast `PROVISIONING_SCRIPT` path checked
- first-wave provisioning script created

### 7. Workflow export format

- Comfy docs checked for workflow JSON / API format behavior
- bridge expects exported API prompt JSON, not arbitrary frontend state dumps

### 8. Output retrieval behavior

- current bridge assumptions documented:
  - first output only
  - media keys only
  - no subtitle/text artifact handling yet

### 8b. First-wave deployment topology

- first-wave proof path now standardized:
  - backend on worker
  - `ComfyUI` on same worker
  - frontend can stay separate
- split backend/worker topology deferred until after first-wave validation

### 9. First-wave feature fit

- first-wave workflows chosen to match the current bridge:
  - `video.animate_image`
  - `lipsync.video_audio`

### 10. Second-wave feature risk

- explicitly deferred:
  - `lipsync.image_audio`
  - `video.extend`
  - captions
  - lyrics
  - `Wan 2.2 S2V`
  - `Wan 2.2 Animate`
  - `Wan 2.1 VACE`

### 11. Third-party custom node drift

- acknowledged as a real risk
- controlled by keeping first-wave scope small
- not fully solvable before launch because upstream repos can change

### 12. Model auth / gated downloads

- `HF_TOKEN` called out as optional but likely needed in some cases

## Remaining Launch-Dependent Scenarios

These cannot be fully settled before the instance is live:

1. whether the chosen first-wave custom node repos load cleanly on the current Vast template version
2. whether each first-wave workflow runs directly in raw `ComfyUI`
3. whether each exported API workflow still matches the current bridge placeholders cleanly
4. whether any chosen model download requires authentication or extra helper assets not yet installed

## Launch Rule

Do not treat the template as ready until these 3 are all true:

1. first-wave nodes load
2. first-wave workflows run directly in `ComfyUI`
3. first-wave workflows run through the backend bridge from the existing app
