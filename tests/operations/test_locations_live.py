#
#   test_locations_live.py
#
#   Class: LocationOperations
#          Live-DB tests against Sena 3 covering all five phases of the
#          stabilization model:
#              A. read-only
#              B. create + delete in-place (TEST_ prefix, finally cleanup)
#              C. reorder (capture-restore)
#              D. modify (capture-restore)
#              E. delete in sandbox copy
#
#          Sena 3 ships with zero existing locations, which makes
#          LocationOperations the cleanest template -- Phases B-D have
#          no risk of collision with pre-existing data. Phase E uses
#          the shared sena3_sandbox fixture so destructive operations
#          never touch the user's real Sena 3.
#
#          This file is the canonical Cycle-2 template; replicate its
#          structure to test_persons_live.py, test_notes_live.py, etc.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


# Every test in this module opens a real .fwdata project via writable_project
# or sena3_sandbox.
pytestmark = pytest.mark.requires_live_project


# ---------------------------------------------------------------------------
# Live-project fixture (matches the canonical pattern from test_phonemes.py)
# ---------------------------------------------------------------------------

_CANDIDATE_PROJECTS = ("Sena 3", "Test", "SampleLexicon", "SampleLexicon3")


def _try_open_project(write_enabled):
    """Open the first candidate project that responds. None if none work."""
    try:
        from flexlibs2.code.FLExProject import FLExProject
    except Exception:
        return None

    project = FLExProject()
    for name in _CANDIDATE_PROJECTS:
        try:
            project.OpenProject(name, writeEnabled=write_enabled)
            return project
        except Exception:
            continue
    return None


@pytest.fixture(scope="module")
def writable_project():
    """
    Module-scoped, write-enabled real FLExProject. Skipped if SIL.LCModel
    isn't loaded or no candidate project opens.
    """
    if "SIL.LCModel" not in sys.modules:
        pytest.skip("Requires SIL.LCModel (FieldWorks installed)")

    project = _try_open_project(write_enabled=True)
    if project is None:
        pytest.skip(
            "No writable FieldWorks project available "
            f"(tried: {', '.join(_CANDIDATE_PROJECTS)})"
        )

    yield project

    try:
        project.CloseProject()
    except Exception:
        pass


def _delete_if_present(project, name):
    """Pre-clean a TEST_ location left from a crashed prior run."""
    existing = project.Location.Find(name)
    if existing is not None:
        try:
            project.Location.Delete(existing)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Phase A: read-only
# ---------------------------------------------------------------------------


class TestLocationsPhaseARead:
    """Phase A: getters return without raising, regardless of count."""

    @pytest.mark.live_phase("LocationOperations", "read")
    def test_get_all_returns_list(self, writable_project):
        """GetAll() returns a list (possibly empty) without raising."""
        locations = writable_project.Location.GetAll()
        assert isinstance(locations, list)

    @pytest.mark.live_phase("LocationOperations", "read")
    def test_find_returns_none_for_missing(self, writable_project):
        """Find() returns None for a name that cannot exist."""
        result = writable_project.Location.Find(
            "TEST_zzqxxx_nonexistent_for_phase_a"
        )
        assert result is None

    @pytest.mark.live_phase("LocationOperations", "read")
    def test_exists_returns_false_for_missing(self, writable_project):
        """Exists() returns False for a name that cannot exist."""
        assert (
            writable_project.Location.Exists(
                "TEST_zzqxxx_nonexistent_for_phase_a"
            )
            is False
        )


# ---------------------------------------------------------------------------
# Phase B: create + delete in-place (TEST_ prefix, finally cleanup)
# ---------------------------------------------------------------------------


class TestLocationsPhaseBAdd:
    """Phase B: create a TEST_ location, verify, delete in finally."""

    @pytest.mark.live_phase("LocationOperations", "add")
    def test_create_and_delete_roundtrip(self, writable_project):
        """Create -> assert name + Exists -> Delete -> assert absent."""
        name = "TEST_loc_phase_b_roundtrip"

        _delete_if_present(writable_project, name)

        location = writable_project.Location.Create(name)
        try:
            assert location is not None
            assert writable_project.Location.GetName(location) == name
            assert writable_project.Location.Exists(name) is True
        finally:
            try:
                writable_project.Location.Delete(location)
            except Exception:
                pass

        assert writable_project.Location.Find(name) is None

    @pytest.mark.live_phase("LocationOperations", "add")
    def test_create_with_alias(self, writable_project):
        """Create with alias -> verify both name and alias round-trip."""
        name = "TEST_loc_phase_b_alias"
        alias = "TBA"

        _delete_if_present(writable_project, name)

        location = writable_project.Location.Create(name, alias=alias)
        try:
            assert writable_project.Location.GetName(location) == name
            assert writable_project.Location.GetAlias(location) == alias
        finally:
            try:
                writable_project.Location.Delete(location)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Phase C: reorder (capture-restore)
# ---------------------------------------------------------------------------


class TestLocationsPhaseCReorder:
    """
    Phase C: capture original order, perform a swap on the OS list,
    restore. The PossibilitiesOS ordered sequence has no MoveUp helper
    on LocationOperations, so the test manipulates the sequence directly
    -- exercises Insert/Remove/IndexOf semantics.
    """

    @pytest.mark.live_phase("LocationOperations", "reorder")
    def test_swap_two_temp_locations(self, writable_project):
        """Create two locations, swap their positions, restore."""
        name_a = "TEST_loc_phase_c_swap_a"
        name_b = "TEST_loc_phase_c_swap_b"

        _delete_if_present(writable_project, name_a)
        _delete_if_present(writable_project, name_b)

        loc_a = writable_project.Location.Create(name_a)
        loc_b = writable_project.Location.Create(name_b)
        try:
            possibilities = writable_project.lp.LocationsOA.PossibilitiesOS

            idx_a_initial = possibilities.IndexOf(loc_a)
            idx_b_initial = possibilities.IndexOf(loc_b)
            assert idx_a_initial >= 0
            assert idx_b_initial >= 0
            assert idx_a_initial != idx_b_initial

            # Reorder: move loc_a past loc_b
            possibilities.Remove(loc_a)
            idx_b_now = possibilities.IndexOf(loc_b)
            possibilities.Insert(idx_b_now + 1, loc_a)
            assert possibilities.IndexOf(loc_a) > possibilities.IndexOf(loc_b)

            # Restore: put loc_a back at original index
            possibilities.Remove(loc_a)
            possibilities.Insert(idx_a_initial, loc_a)
            assert possibilities.IndexOf(loc_a) == idx_a_initial
        finally:
            for loc in (loc_a, loc_b):
                try:
                    writable_project.Location.Delete(loc)
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Phase D: modify + restore (capture-restore name change)
# ---------------------------------------------------------------------------


class TestLocationsPhaseDModify:
    """
    Phase D: capture name, set new value, assert change, restore
    original. Note: DateModified is auto-bumped by LCM on any write, so
    the location is XML-dirty even though the user-visible name returned
    to the captured value. Accepted (see CLAUDE.md Phase D note);
    scripts/restore_sena3.py wipes the churn between sessions.
    """

    @pytest.mark.live_phase("LocationOperations", "modify")
    def test_name_capture_modify_restore(self, writable_project):
        """SetName(new) then SetName(captured) round-trips the value."""
        name = "TEST_loc_phase_d_modify"
        new_name = "TEST_loc_phase_d_modified"

        _delete_if_present(writable_project, name)
        _delete_if_present(writable_project, new_name)

        location = writable_project.Location.Create(name)
        try:
            captured = writable_project.Location.GetName(location)
            assert captured == name

            writable_project.Location.SetName(location, new_name)
            assert writable_project.Location.GetName(location) == new_name

            writable_project.Location.SetName(location, captured)
            assert writable_project.Location.GetName(location) == name
        finally:
            try:
                writable_project.Location.Delete(location)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Phase E: delete in sandbox (destructive, isolated)
# ---------------------------------------------------------------------------


class TestLocationsPhaseEDelete:
    """
    Phase E: destructive delete in an isolated sandbox copy of Sena 3.

    Sena 3 has zero pre-existing locations, so "delete a pre-existing"
    is not a meaningful test for LocationOperations specifically. This
    test instead exercises the destructive path inside the sandbox --
    creating an object and deleting it without touching the user's real
    project. When this template is replicated to a class with existing
    items (PersonOperations: 6 entries), Phase E should be strengthened
    to truly delete a pre-existing object.
    """

    @pytest.mark.live_phase("LocationOperations", "delete")
    def test_create_then_delete_in_sandbox(self, sena3_sandbox):
        """In a sandbox copy, create and delete a location."""
        name = "TEST_loc_phase_e_sandbox"

        location = sena3_sandbox.Location.Create(name)
        assert sena3_sandbox.Location.Exists(name) is True

        sena3_sandbox.Location.Delete(location)
        assert sena3_sandbox.Location.Find(name) is None
