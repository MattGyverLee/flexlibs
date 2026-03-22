#
#   test_lcm_contract.py
#
#   Pytest-based contract tests for flexlibs2 <-> liblcm compatibility.
#
#   These tests operate in two modes:
#
#   Mode 1 (runs anywhere, no deps):
#     - Extracts the expected contract from source via AST
#     - Validates contract structure and consistency
#     - Compares against a checked-in baseline snapshot
#     - Detects when flexlibs2 code changes introduce new LCM deps
#
#   Mode 2 (requires FieldWorks + pythonnet):
#     - Introspects installed liblcm assemblies
#     - Verifies every expected type/member actually exists
#     - Generates a new snapshot for regression tracking
#
#   Platform: Python 3.8+
#   Copyright 2025
#

"""
LibLCM contract tests.

Run with::

    # Mode 1: static analysis only (runs anywhere)
    pytest tests/contract/test_lcm_contract.py -m "not requires_liblcm"

    # Mode 2: full verification (requires FieldWorks)
    pytest tests/contract/test_lcm_contract.py

    # Verbose output with affected file details
    pytest tests/contract/test_lcm_contract.py -v -s
"""

import json
import os
import pytest
from pathlib import Path

from tests.contract.extract_lcm_contract import extract_contract

# Paths
CONTRACT_DIR = Path(__file__).parent
SNAPSHOTS_DIR = CONTRACT_DIR / "snapshots"
BASELINE_CONTRACT_PATH = SNAPSHOTS_DIR / "expected_contract.json"
BASELINE_SNAPSHOT_PATH = SNAPSHOTS_DIR / "liblcm_baseline.json"


# --- Markers ---

requires_liblcm = (
    pytest.mark.skipif(
        not _has_liblcm(),
        reason="Requires FieldWorks/liblcm (pythonnet + SIL.LCModel)",
    )
    if not callable
    else None
)  # defined below


def _has_liblcm():
    """Check if liblcm is available via pythonnet."""
    try:
        import clr

        clr.AddReference("SIL.LCModel")
        return True
    except Exception:
        return False


requires_liblcm = pytest.mark.skipif(
    not _has_liblcm(),
    reason="Requires FieldWorks/liblcm (pythonnet + SIL.LCModel)",
)


# --- Fixtures ---


@pytest.fixture(scope="session")
def expected_contract():
    """Extract the expected LCM contract from flexlibs2 source."""
    return extract_contract()


@pytest.fixture(scope="session")
def baseline_contract():
    """Load the checked-in baseline contract, if it exists."""
    if not BASELINE_CONTRACT_PATH.exists():
        pytest.skip(
            "No baseline contract snapshot found. Run: "
            "python -m tests.contract.extract_lcm_contract "
            f"-o {BASELINE_CONTRACT_PATH}"
        )
    return json.loads(BASELINE_CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def baseline_snapshot():
    """Load the checked-in liblcm baseline snapshot, if it exists."""
    if not BASELINE_SNAPSHOT_PATH.exists():
        pytest.skip("No liblcm baseline snapshot found. Generate one on a " "machine with FieldWorks installed.")
    return json.loads(BASELINE_SNAPSHOT_PATH.read_text(encoding="utf-8"))


# ============================================================
# MODE 1: Static analysis tests (run anywhere)
# ============================================================


class TestContractExtraction:
    """Verify that the contract extractor works and produces valid output."""

    def test_contract_has_imports(self, expected_contract):
        """Contract should find SIL.LCModel imports."""
        imports = expected_contract["imports"]
        assert len(imports) > 0, "No SIL imports found"
        assert "SIL.LCModel" in imports, "SIL.LCModel not in imports"

    def test_contract_has_files(self, expected_contract):
        """Contract should cover multiple source files."""
        files = expected_contract["files"]
        assert len(files) > 30, f"Expected 30+ files with LCM deps, found {len(files)}"

    def test_contract_has_factories(self, expected_contract):
        """Contract should identify factory types."""
        factories = expected_contract["factories"]
        assert len(factories) > 10, f"Expected 10+ factories, found {len(factories)}"

    def test_contract_has_repositories(self, expected_contract):
        """Contract should identify repository types."""
        repos = expected_contract["repositories"]
        assert len(repos) > 5, f"Expected 5+ repositories, found {len(repos)}"

    def test_contract_has_interfaces(self, expected_contract):
        """Contract should identify interface types (I-prefixed)."""
        interfaces = expected_contract["interfaces"]
        assert len(interfaces) > 20, f"Expected 20+ interfaces, found {len(interfaces)}"

    def test_critical_types_present(self, expected_contract):
        """
        The most critical LCM types must appear in the contract.
        If these are missing, the extractor is broken.
        """
        all_names = set()
        for names in expected_contract["imports"].values():
            all_names.update(names)

        critical = [
            "ITsString",
            "TsStringUtils",
            "ILexEntry",
            "ILexSense",
            "IPartOfSpeech",
        ]
        for name in critical:
            assert name in all_names, f"Critical type {name} not found in contract"

    def test_summary_is_consistent(self, expected_contract):
        """Summary counts should match actual data."""
        s = expected_contract["summary"]
        assert s["total_files_with_lcm_deps"] == len(expected_contract["files"])
        assert s["total_factories"] == len(expected_contract["factories"])
        assert s["total_repositories"] == len(expected_contract["repositories"])


class TestContractStability:
    """
    Compare current contract against the checked-in baseline.
    Detects when code changes introduce new LCM dependencies.
    """

    def test_no_new_type_dependencies(self, expected_contract, baseline_contract):
        """
        New LCM type imports should be deliberate.
        Fails if flexlibs2 code now imports types not in the baseline.
        """
        current_names = set()
        for names in expected_contract["imports"].values():
            current_names.update(names)

        baseline_names = set()
        for names in baseline_contract["imports"].values():
            baseline_names.update(names)

        new_deps = current_names - baseline_names
        if new_deps:
            pytest.fail(
                f"New LCM type dependencies detected (update baseline if intentional):\n"
                + "\n".join(f"  + {n}" for n in sorted(new_deps))
            )

    def test_no_removed_type_dependencies(self, expected_contract, baseline_contract):
        """
        Detect when LCM imports are removed (might indicate refactoring).
        This is informational -- removal is usually fine.
        """
        current_names = set()
        for names in expected_contract["imports"].values():
            current_names.update(names)

        baseline_names = set()
        for names in baseline_contract["imports"].values():
            baseline_names.update(names)

        removed = baseline_names - current_names
        if removed:
            # This is a warning, not a failure
            import warnings

            warnings.warn(
                f"LCM type dependencies removed (update baseline):\n" + "\n".join(f"  - {n}" for n in sorted(removed))
            )

    def test_file_count_not_dramatically_changed(self, expected_contract, baseline_contract):
        """
        Sanity check: file count shouldn't change by more than 20%
        without updating the baseline.
        """
        current = expected_contract["summary"]["total_files_with_lcm_deps"]
        baseline = baseline_contract["summary"]["total_files_with_lcm_deps"]
        diff_pct = abs(current - baseline) / max(baseline, 1) * 100

        assert diff_pct < 20, (
            f"File count changed by {diff_pct:.0f}% "
            f"(baseline={baseline}, current={current}). "
            "Update baseline if this is expected."
        )


# ============================================================
# MODE 2: Live liblcm verification (requires deps)
# ============================================================


@requires_liblcm
class TestLiveContractVerification:
    """
    Verify the expected contract against the installed liblcm.
    Only runs when FieldWorks/pythonnet is available.
    """

    @pytest.fixture(scope="class")
    def liblcm_snapshot(self, expected_contract):
        """Generate a live snapshot from installed liblcm."""
        from tests.contract.generate_lcm_snapshot import generate_snapshot

        return generate_snapshot(expected_contract)

    def test_all_types_found(self, liblcm_snapshot):
        """Every type flexlibs2 imports should exist in liblcm."""
        missing = liblcm_snapshot.get("missing_types", [])
        if missing:
            lines = [f"  - {t}" for t in missing]
            pytest.fail(f"{len(missing)} types not found in liblcm:\n" + "\n".join(lines))

    def test_no_missing_members(self, expected_contract, liblcm_snapshot):
        """
        Every property/method flexlibs2 uses should exist on the type.
        """
        from tests.contract.compare_contracts import compare

        report = compare(expected_contract, liblcm_snapshot)

        missing = report["missing_members"]
        if missing:
            lines = [f"  - {mm['type']}.{mm['member']} ({mm['kind']})" for mm in missing]
            pytest.fail(f"{len(missing)} missing members:\n" + "\n".join(lines))

    def test_compatibility_score(self, expected_contract, liblcm_snapshot):
        """Compatibility score should be 100%."""
        from tests.contract.compare_contracts import compare

        report = compare(expected_contract, liblcm_snapshot)
        score = report["summary"]["compatibility_score"]
        assert score == 100.0, f"Compatibility score: {score}% (expected 100%)"

    def test_save_snapshot_for_regression(self, liblcm_snapshot, tmp_path):
        """
        Save the live snapshot so it can be committed as a new baseline.
        """
        from tests.contract.generate_lcm_snapshot import save_snapshot

        version = liblcm_snapshot["metadata"]["liblcm_version"]
        output = SNAPSHOTS_DIR / f"liblcm_{version}.json"

        # Only save if snapshots dir exists
        if SNAPSHOTS_DIR.exists():
            save_snapshot(liblcm_snapshot, output)


@requires_liblcm
class TestLiveRegressionCheck:
    """
    Compare live liblcm against the baseline snapshot.
    Detects when a liblcm upgrade removes types/members.
    """

    @pytest.fixture(scope="class")
    def liblcm_snapshot(self, expected_contract):
        from tests.contract.generate_lcm_snapshot import generate_snapshot

        return generate_snapshot(expected_contract)

    def test_no_regressions_from_baseline(self, liblcm_snapshot, baseline_snapshot):
        """
        No types or members should disappear compared to baseline.
        """
        from tests.contract.compare_contracts import compare_snapshots

        report = compare_snapshots(baseline_snapshot, liblcm_snapshot)

        regressions = report["regressions"]
        if regressions:
            lines = [f"  - {r['detail']}" for r in regressions]
            pytest.fail(f"{len(regressions)} regressions from baseline:\n" + "\n".join(lines))


# ============================================================
# Utility: per-file impact tests
# ============================================================


class TestPerFileImpact:
    """
    When a baseline snapshot exists, verify which specific files
    would break with the current liblcm.
    """

    def test_report_affected_files(self, expected_contract, baseline_snapshot):
        """
        Generate and print the full impact report.
        This test always passes but prints the report for visibility.
        """
        from tests.contract.compare_contracts import compare, format_report

        report = compare(expected_contract, baseline_snapshot)
        text = format_report(report, verbose=True)
        print("\n" + text)

        # Store report as test artifact
        report_path = SNAPSHOTS_DIR / "latest_report.json"
        if SNAPSHOTS_DIR.exists():
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
