from __future__ import annotations

import argparse
from pathlib import Path


PROFILE_DIR = Path(__file__).resolve().parent / "runtime_profiles"
TARGET_CONFIG = Path(__file__).resolve().parent / "runtime_config.env"


def available_profiles() -> list[str]:
    return sorted(path.stem for path in PROFILE_DIR.glob("*.env"))


def apply_profile(profile: str) -> Path:
    profile_path = PROFILE_DIR / f"{profile}.env"
    if not profile_path.exists():
        raise FileNotFoundError(f"Unknown runtime profile: {profile}")

    TARGET_CONFIG.write_text(profile_path.read_text(encoding="utf-8"), encoding="utf-8")
    return TARGET_CONFIG


def main() -> int:
    parser = argparse.ArgumentParser(description="Switch Open Higgsfield backend runtime profiles")
    parser.add_argument("profile", nargs="?", help="Profile name to apply")
    parser.add_argument("--list", action="store_true", help="List available runtime profiles")
    args = parser.parse_args()

    if args.list:
        for profile in available_profiles():
            print(profile)
        return 0

    if not args.profile:
        parser.error("profile is required unless --list is used")

    target = apply_profile(args.profile)
    print(f"Applied runtime profile '{args.profile}' to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
