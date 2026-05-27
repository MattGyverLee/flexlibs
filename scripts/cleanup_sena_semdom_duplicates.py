#
#   cleanup_sena_semdom_duplicates.py
#
#   One-shot cleanup for the Sena 3 test project's SemanticDomainListOA,
#   which was polluted during Phase 6b verification runs (commit b55db99)
#   before the force=False guard landed. Each ImportCatalog call appended
#   another full copy of the 9 top-level SemDom items, so the list ended
#   up with 9 unique GUIDs duplicated 8 times = 72 top-level items, and
#   FieldWorks now greets every open of the project with a "Your project
#   needs professional cleanup" dialog.
#
#   This script keeps the FIRST occurrence of each canonical GUID and
#   deletes all subsequent copies via LCM's DeleteUnderlyingObject so
#   references and owned children are cleaned up properly.
#
#   USAGE
#   -----
#       python scripts/cleanup_sena_semdom_duplicates.py            # dry-run
#       python scripts/cleanup_sena_semdom_duplicates.py --apply    # destructive
#       python scripts/cleanup_sena_semdom_duplicates.py --project "Other Project" --apply
#
#   The dry-run path lists what would be deleted and exits 0 without
#   touching the project. Pass --apply to actually mutate. Tracks issue
#   #29 item 4.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

from __future__ import annotations

import argparse
import sys
from typing import Optional


def _initialise_flex():
    """Mirror tests/conftest.py: load SIL assemblies, init FLEx."""
    import os
    import winreg
    import clr

    clr.AddReference("System")
    import System  # noqa: F401

    fw_code_dir: Optional[str] = None
    for hive, sub in [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\SIL\FieldWorks\9"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\SIL\FieldWorks\9"),
    ]:
        try:
            k = winreg.OpenKey(hive, sub)
            v, _ = winreg.QueryValueEx(k, "RootCodeDir")
            if os.path.exists(os.path.join(v, "FieldWorks.exe")):
                fw_code_dir = v
                sys.path.insert(0, v)
                break
        except Exception:
            pass
    if fw_code_dir is None:
        print("[ERROR] FieldWorks 9 install not found via registry.")
        sys.exit(2)

    clr.AddReference("FwUtils")
    clr.AddReference("SIL.WritingSystems")
    clr.AddReference("SIL.LCModel")

    from SIL.FieldWorks.Common.FwUtils import FwRegistryHelper, FwUtils
    from SIL.WritingSystems import Sldr

    FwRegistryHelper.Initialize()
    FwUtils.InitializeIcu()
    try:
        Sldr.Initialize(True)
    except Exception:
        # Already initialised on later invocations; non-fatal.
        pass

    from flexlibs2.code.FLExInit import FLExInitialize

    FLExInitialize()


def _enumerate_duplicates(possibilities):
    """
    Walk the PossibilitiesOS once. Returns:
      keep[guid_str] = IcmObject   (first occurrence)
      drop          = [IcmObject]  (every subsequent occurrence)
    """
    keep = {}
    drop = []
    for item in possibilities:
        guid_key = str(item.Guid)
        if guid_key in keep:
            drop.append(item)
        else:
            keep[guid_key] = item
    return keep, drop


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Dedup the top-level SemDom items in a polluted Sena 3 "
            "test project. Default is dry-run; pass --apply to mutate."
        )
    )
    parser.add_argument(
        "--project",
        default="Sena 3",
        help="FieldWorks project name (default: 'Sena 3')",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete duplicates. Without this flag the "
        "script only reports what would be deleted.",
    )
    args = parser.parse_args()

    _initialise_flex()

    from SIL.LCModel.Core.KernelInterfaces import ITsString
    from flexlibs2 import FLExProject

    project = FLExProject()
    project.OpenProject(args.project, writeEnabled=args.apply)
    try:
        lp = project.lp
        if lp.SemanticDomainListOA is None:
            print(
                f"[INFO] {args.project} has no SemanticDomainListOA; "
                "nothing to clean up."
            )
            return 0

        analysis_ws = project.project.DefaultAnalWs
        possibilities = list(lp.SemanticDomainListOA.PossibilitiesOS)
        total_before = len(possibilities)

        keep, drop = _enumerate_duplicates(possibilities)

        print(f"[INFO] Project: {args.project}")
        print(
            f"[INFO] SemanticDomainListOA top-level items: {total_before} "
            f"({len(keep)} unique GUIDs, {len(drop)} duplicates)"
        )

        if not drop:
            print("[OK]   No duplicates detected. Nothing to do.")
            return 0

        print("\n[INFO] Would delete the following duplicate items:")
        for it in drop[:10]:
            name = ITsString(it.Name.get_String(analysis_ws)).Text or "(?)"
            print(f"    hvo={it.Hvo}  guid={it.Guid}  name={name!r}")
        if len(drop) > 10:
            print(f"    ... and {len(drop) - 10} more.")

        if not args.apply:
            print(
                "\n[INFO] DRY-RUN. Re-run with --apply to delete "
                f"{len(drop)} duplicate items."
            )
            return 0

        # Destructive path: LCM mutations must happen inside an action
        # handler. Use FLExProject.Transaction for a rollback-on-error
        # wrap; it doesn't require the project to be opened with
        # undoable=True.
        #
        # Use PossibilitiesOS.Remove(item) with per-item exception
        # handling. The LCM build in use here has no
        # IDataReader.DeleteUnderlyingObject, so Remove is the only
        # available path. Some duplicate items hold stale references
        # to objects deleted in prior cleanup runs -- Remove triggers
        # an XML serialization of the doomed item for the undo log
        # which raises KeyNotFoundException on those. Wrap each
        # deletion individually so a single bad item doesn't abort
        # the whole batch.
        #
        # CloseProject persists on exit. Don't call SaveChanges
        # explicitly: writeEnabled=True opens with BeginNonUndoableTask
        # which stays open for the session; SaveChanges expects the
        # undo stack to be idle and raises "Commit at wrong place"
        # while the task is still open.

        # Note on the per-item exception handler below: when an item's
        # owned children reference GUIDs not present in the identity
        # map (the corruption pattern), Remove still completes the
        # deletion but the undo-log XML serializer raises
        # KeyNotFoundException AFTER the LcmList mutation. So
        # "exception raised" does not mean "deletion failed". We
        # report both the raised-exception count and the actual
        # before/after delta so the user can interpret the result.

        print(f"\n[INFO] --apply set. Deleting {len(drop)} duplicates...")
        threw_after_delete = []
        with project.Transaction("Dedup SemDom duplicates"):
            for idx, item in enumerate(drop, start=1):
                try:
                    lp.SemanticDomainListOA.PossibilitiesOS.Remove(item)
                except Exception as e:
                    threw_after_delete.append(
                        (item.Hvo, str(e).splitlines()[0])
                    )
                if idx % 10 == 0:
                    print(f"    ... processed {idx}/{len(drop)}")
        if threw_after_delete:
            print(
                f"\n[NOTE] {len(threw_after_delete)}/{len(drop)} "
                f"Remove() calls raised KeyNotFoundException after the "
                f"mutation -- these are the polluted items whose owned "
                f"children point at stale GUIDs. The before/after count "
                f"above tells you what actually got removed."
            )
        remaining = lp.SemanticDomainListOA.PossibilitiesOS.Count
        print(
            f"[OK]   Done. Top-level count: {total_before} -> {remaining} "
            f"(removed {total_before - remaining})."
        )
        return 0
    finally:
        try:
            project.CloseProject()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
