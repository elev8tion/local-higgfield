# Vast End-of-Night Backup

Use this when you must destroy the rented GPU instance.

It saves the small, high-value artifacts:
- workflow JSON files
- logs
- repo and custom-node commit SHAs
- model manifests
- pip freeze

It does **not** save huge model weights.

## On the worker

```bash
cd /workspace/Open-Higgsfield-AI
bash gpu/vast_end_of_night_backup.sh
```

## Copy the archive to your local machine

Replace the host and port with the current Vast SSH values.

```bash
scp -P <PORT> root@<HOST_IP>:/workspace/nightly_backups/open_higgsfield_<TIMESTAMP>.tar.gz ~/Downloads/
```

## Then destroy the instance

Only destroy the instance after the archive is copied off successfully.
