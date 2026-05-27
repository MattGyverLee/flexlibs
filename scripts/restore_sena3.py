#
#   restore_sena3.py
#
#   Restore the Sena 3 fixture from tests/fixtures/Sena 3 *.fwbackup
#   into the user's FieldWorks projects directory, overwriting any
#   existing Sena 3 project.
#
#   Run before a live-DB test session to guarantee a clean baseline.
#   Re-run after any session to wipe accumulated test mutations.
#
#   Platform: Windows + Python (FieldWorks 9+ installed)
#
#   Copyright 2026
#

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path


_DEFAULT_TARGET = "Sena 3"
_REGISTRY_KEY = r"SOFTWARE\SIL\FieldWorks\9"


def find_fw_projects_dir():
    """Return the FieldWorks 9 projects directory as a Path, or None."""
    try:
        import winreg

        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, _REGISTRY_KEY) as key:
                    value, _ = winreg.QueryValueEx(key, "ProjectsDir")
                    if value and os.path.isdir(value):
                        return Path(value)
            except OSError:
                continue
    except ImportError:
        pass

    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidate = Path(local) / "SIL" / "FieldWorks" / "9" / "Projects"
        if candidate.exists():
            return candidate

    return None


def find_fwbackup(fixtures_dir, pattern="Sena 3*.fwbackup"):
    """Locate the most recent matching .fwbackup in fixtures_dir."""
    if not fixtures_dir.exists():
        return None
    matches = sorted(fixtures_dir.glob(pattern))
    return matches[-1] if matches else None


def restore_project(fwbackup_path, projects_dir, target_name=_DEFAULT_TARGET):
    """
    Unzip fwbackup_path and place its contents under projects_dir/target_name.
    Removes any existing target_dir first. Returns the target_dir.
    """
    fwbackup_path = Path(fwbackup_path)
    projects_dir = Path(projects_dir)
    target_dir = projects_dir / target_name

    if not fwbackup_path.exists():
        raise FileNotFoundError(f"Backup not found: {fwbackup_path}")
    if not projects_dir.exists():
        raise FileNotFoundError(f"Projects directory not found: {projects_dir}")

    if target_dir.exists():
        print(f"[INFO] Removing existing {target_dir}")
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True)
    print(f"[INFO] Unzipping {fwbackup_path.name} -> {target_dir}")
    with zipfile.ZipFile(fwbackup_path) as zf:
        zf.extractall(target_dir)

    fwdatas = list(target_dir.glob("*.fwdata"))
    if not fwdatas:
        raise RuntimeError(
            f"No .fwdata found after extraction into {target_dir}; "
            "backup file may be malformed."
        )

    print(f"[OK] Restored {target_name} -> {fwdatas[0]}")
    return target_dir


def check_state(projects_dir, target_name=_DEFAULT_TARGET):
    """Report current state of target project. Returns True if present."""
    target_dir = projects_dir / target_name
    if not target_dir.exists():
        print(f"[INFO] {target_name} not present in {projects_dir}")
        return False

    fwdatas = list(target_dir.glob("*.fwdata"))
    if not fwdatas:
        print(f"[WARN] {target_dir} exists but contains no .fwdata")
        return False

    print(f"[INFO] {target_name} present: {fwdatas[0]}")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Restore the Sena 3 .fwbackup fixture into the FieldWorks "
            "projects directory."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report current state without modifying anything.",
    )
    parser.add_argument(
        "--target",
        default=_DEFAULT_TARGET,
        help=f"Project name to restore as (default: {_DEFAULT_TARGET!r}).",
    )
    parser.add_argument(
        "--fixtures",
        default=None,
        help=(
            "Override path to fixtures directory "
            "(default: <repo>/tests/fixtures)."
        ),
    )
    parser.add_argument(
        "--projects-dir",
        default=None,
        help=(
            "Override FieldWorks projects directory "
            "(default: registry or %%LOCALAPPDATA%%\\SIL\\FieldWorks\\9\\Projects)."
        ),
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    fixtures_dir = (
        Path(args.fixtures) if args.fixtures else repo_root / "tests" / "fixtures"
    )
    projects_dir = (
        Path(args.projects_dir) if args.projects_dir else find_fw_projects_dir()
    )

    if projects_dir is None:
        print(
            "[ERROR] Could not locate FieldWorks projects directory. "
            "Pass --projects-dir to override.",
            file=sys.stderr,
        )
        return 2

    if args.check:
        check_state(projects_dir, args.target)
        return 0

    fwbackup = find_fwbackup(fixtures_dir)
    if fwbackup is None:
        print(
            f"[ERROR] No 'Sena 3*.fwbackup' found in {fixtures_dir}",
            file=sys.stderr,
        )
        return 2

    try:
        restore_project(fwbackup, projects_dir, args.target)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
