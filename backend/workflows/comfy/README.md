# Comfy Workflow Templates

These JSON files are starter placeholders for the Open Higgsfield `ComfyUI` runner.

## How they are used

- Each backend job type maps to one workflow JSON.
- The runner loads the mapped template, replaces `{{...}}` placeholders from the job payload, submits the rendered graph to a remote `ComfyUI` worker, polls `/history/<prompt_id>`, and downloads the first generated media output.

## Replace these files with real exported workflows

The files in this directory are not intended to be production-ready graphs. Replace each one with an API-exported workflow from your private `ComfyUI` template.

Supported template shapes:

1. Raw Comfy prompt graph:

```json
{
  "1": { "class_type": "SomeNode", "inputs": {} }
}
```

2. Wrapped template with metadata:

```json
{
  "metadata": {
    "output_node_ids": ["123"]
  },
  "prompt": {
    "123": { "class_type": "VHS_VideoCombine", "inputs": {} }
  }
}
```

## Available placeholders

- `{{prompt}}`
- `{{job_id}}`
- `{{job_type}}`
- `{{resolution}}`
- `{{aspect_ratio}}`
- `{{duration}}`
- `{{fps}}`
- `{{frame_count}}`
- `{{width}}`
- `{{height}}`
- `{{assets.image_path}}`
- `{{assets.video_path}}`
- `{{assets.audio_path}}`
- `{{assets.comfy_image_name}}`
- `{{assets.comfy_image_path}}`
- `{{assets.comfy_video_name}}`
- `{{assets.comfy_video_path}}`
- `{{assets.comfy_audio_name}}`
- `{{assets.comfy_audio_path}}`
- `{{output.path}}`
- `{{output.filename}}`
- `{{output.stem}}`
- `{{output.directory}}`
- `{{params.<name>}}`

Example:

```json
{
  "17": {
    "class_type": "LoadImage",
    "inputs": {
      "image": "{{assets.image_path}}"
    }
  }
}
```
