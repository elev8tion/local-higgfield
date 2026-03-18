# Open Higgsfield AI: Technical Documentation & Context

This document serves as a comprehensive knowledge base for the Open Higgsfield AI project. It details the architecture, key components, execution model, and system design strategy.

---

## 1. Project Vision & Overview

**Open Higgsfield AI** is an ambitious open-source project dedicated to **building a fully self-hosted, high-performance AI generation platform** inspired by Higgsfield — but without external API dependency.

- **Core Goal:**  
  To create a **fully local, GPU-powered AI generation system** capable of image, video, and cinematic workflows — controlled through a modern, extensible UI.

- **Architectural Shift (Critical):**  
  The project is transitioning away from external APIs (MuAPI) toward a **self-managed inference pipeline**:
  - Local job system
  - GPU worker execution
  - Direct model integration (e.g., Wan, future video models)

- **Current State:**  
  - Fully functional **UI control plane**
  - Multi-studio system (Image, Video, Lip Sync, Cinema)
  - Prompt + parameter orchestration layer complete
  - Job-based execution model being implemented

- **Future Direction:**  
  - Local inference (Wan / video models)
  - Distributed GPU workers
  - Model abstraction layer (plug-and-play models)
  - Advanced cinematic workflows and automation

---

## 2. Architecture & System Design

The system is evolving into a **three-layer architecture**:

[ Frontend UI (Control Plane) ]
↓
[ Local API / Job System ]
↓
[ GPU Workers / Model Execution ]

### Key Principle

> The UI does not generate — it orchestrates.

---

## 3. Updated File Structure

```tree
src/
├── components/
│   ├── ImageStudio.js      # Prompt + model orchestration (t2i/i2i)
│   ├── VideoStudio.js      # Video orchestration (t2v/i2v)
│   ├── LipSyncStudio.js    # Audio-driven generation workflows
│   ├── CinemaStudio.js     # Cinematic control layer (camera abstraction)
│   ├── UploadPicker.js     # Asset management
│   ├── CameraControls.js   # Prompt-enhanced camera system
│   ├── Header.js
│   ├── AuthModal.js
│   ├── SettingsModal.js
│   └── Sidebar.js
│
├── lib/
│   ├── localApi.js         # NEW: Local job system client (replaces muapi.js)
│   ├── models.js           # Model definitions (now abstract, not API-bound)
│   ├── promptUtils.js      # Prompt construction logic
│   ├── pendingJobs.js      # Job tracking
│   └── uploadHistory.js    # Asset persistence
│
backend/
├── server.py               # Job system API (FastAPI)
│
workers/ (planned)
├── wan_worker.py           # Wan inference engine
├── queue.py                # Job queue system
└── runner.py               # Execution controller


⸻

4. Execution Model (Critical Change)

Previous (Deprecated)

UI → MuAPI → Result

New System
UI → Local API → Job Queue → GPU Worker → Result

5. Job System Design

All generation is now handled through a job-based architecture:

API Pattern
	•	POST /jobs → Create job
	•	GET /jobs/:id → Check status

Job Lifecycle

created → queued → processing → completed / failed

{
  "type": "image_to_video",
  "prompt": "cinematic close-up of a woman in neon rain",
  "image_url": "...",
  "resolution": "720p",
  "duration": 5
}

6. Key Components & Logic

UI = Control Plane

The frontend is responsible for:
	•	Prompt construction
	•	Model selection
	•	Input management (image/audio/video)
	•	Job submission
	•	Result rendering

localApi.js (New Core Layer)

Replaces muapi.js.

Handles:
	•	Job submission
	•	Status polling
	•	Backend communication

Backend (server.py)

Responsible for:
	•	Job creation
	•	Queue management
	•	Worker coordination
	•	Returning results

Workers (Planned)

Responsible for:
	•	Loading models (Wan, etc.)
	•	Running inference
	•	Saving outputs
	•	Updating job status

⸻

7. Model Strategy

Models are no longer API endpoints — they are:

Execution configurations

Each model defines:
	•	Input schema
	•	Required assets
	•	Execution pipeline
	•	Worker compatibility

⸻

8. Cinema System (Advanced Layer)

The Cinema Studio introduces a prompt abstraction system:
	•	Camera → prompt modifiers
	•	Lens → visual characteristics
	•	Aperture → depth of field
	•	Focal length → perspective

This enables:

Structured cinematic generation instead of raw prompting

⸻

9. UI & Styling
	•	Tailwind CSS v4
	•	Dark glassmorphism design
	•	Responsive multi-studio layout
	•	Real-time prompt + control feedback

⸻

10. Development Strategy (IMPORTANT)

Phase 1 — Control Plane (No GPU)
	•	Replace MuAPI
	•	Implement job system
	•	Simulate outputs
	•	Ensure full UI stability

Phase 2 — Execution Layer
	•	Integrate first local model (Wan)
	•	Validate pipeline end-to-end

Phase 3 — GPU Scaling
	•	Deploy workers on GPU infrastructure
	•	Optimize performance and batching


⸻

11. Key Principles
	•	No external API dependency
	•	UI ≠ execution
	•	Everything is a job
	•	Models are modular
	•	GPU is only used when system is stable

⸻

12. Future Roadmap
	•	Wan 2.1 / 2.2 integration
	•	Multi-model routing system
	•	Distributed GPU orchestration
	•	Storyboarding / “Popcorn” system
	•	Real-time generation pipelines
	•	Plugin architecture for models

⸻

13. Summary

Open Higgsfield AI is no longer just an interface for AI APIs.

It is becoming:

A fully self-hosted AI generation engine with a cinematic control system

⸻
---

# 🔥 What this does for you

- aligns your repo with your **new direction**
- removes confusion about MuAPI
- clearly defines **control vs execution**
- makes your project look like a **serious system (because it is)**

---

# Next step

After you paste + commit this:

👉 say **“phase 1 ready”**

and we’ll **wire your frontend to the new job system cleanly (no breakage)**