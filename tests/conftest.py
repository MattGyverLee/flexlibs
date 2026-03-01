#
# conftest.py
#
# Pytest configuration and fixtures for FlexLibs2 validation test suite
#
# Provides:
# - Mock FLExProject fixture with write-enabled flags
# - Mock operations class instances
# - Assertion helpers for validation errors
# - Sample data generators
# - Test categorization markers
#
# Platform: Python.NET
#           FieldWorks Version 9+
#
# Copyright 2025
#

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# ========== INITIALIZE FIELDWORKS BEFORE ANYTHING ELSE ==========
# This MUST happen BEFORE importing any flexlibs2 modules
# flexlibs2/__init__.py imports all Operations classes which depend on SIL.LCModel
# We must set up the FieldWorks path FIRST

print("[INFO] Initializing FieldWorks for tests...")
try:
    # Step 1: Set up Windows registry access and FW paths DIRECTLY
    # (without importing any flexlibs modules)
    import clr
    import sys
    import os
    from System import Environment
    from Microsoft.Win32 import Registry

    # Get FieldWorks installation path from registry (manually, without importing FLExGlobals)
    RegKey = r"SOFTWARE\SIL\FieldWorks\9"
    try:
        rKey = Registry.LocalMachine.OpenSubKey(RegKey)
        if rKey is None:
            rKey = Registry.CurrentUser.OpenSubKey(RegKey)

        if rKey:
            fw_code_dir = rKey.GetValue("RootCodeDir")
            if fw_code_dir and os.path.exists(os.path.join(fw_code_dir, "FieldWorks.exe")):
                sys.path.append(fw_code_dir)
                print(f"[INFO] Added to path: {fw_code_dir}")
    except Exception as e:
        print(f"[WARN] Could not read registry: {e}")

    # Step 2: Now load SIL assemblies
    print("[INFO] Loading SIL assemblies...")
    clr.AddReference("FwUtils")
    clr.AddReference("SIL.WritingSystems")
    clr.AddReference("SIL.LCModel")
    print("[OK] SIL assemblies loaded")

    # Step 3: Initialize FLEx services
    print("[INFO] Initializing FLEx services...")
    from SIL.FieldWorks.Common.FwUtils import FwRegistryHelper, FwUtils
    from SIL.WritingSystems import Sldr

    FwRegistryHelper.Initialize()
    FwUtils.InitializeIcu()
    Sldr.Initialize(True)
    print("[OK] FieldWorks fully initialized")

    # Step 4: Initialize FLEx using the proper initialization function
    # FLExInitialize() does more complete setup than just InitialiseFWGlobals()
    print("[INFO] Running FLExInitialize()...")
    from flexlibs2.code.FLExInit import FLExInitialize
    FLExInitialize()
    print("[OK] FLEx fully initialized")

    # Step 5: Now that FLEx is fully initialized, import and reload flexlibs2
    # We may have a partially initialized module in sys.modules, so reload it
    print("[INFO] Importing flexlibs2 package...")
    import sys
    import importlib
    if 'flexlibs2' in sys.modules:
        print("[DEBUG] flexlibs2 already in sys.modules, reloading...")
        flexlibs2 = importlib.reload(sys.modules['flexlibs2'])
    else:
        import flexlibs2
        flexlibs2 = sys.modules.get('flexlibs2')
    print("[OK] flexlibs2 imported successfully")

    # DEBUG: Check what's actually in flexlibs2 namespace
    if flexlibs2:
        attrs_before = set(dir(flexlibs2))
        ops_found = sorted([x for x in attrs_before if 'Operations' in x])
        print(f"[DEBUG] Found {len(ops_found)} operations in flexlibs2")
        if ops_found:
            print(f"[DEBUG] Sample operations: {ops_found[:3]}")

    # Step 6: Pre-cache all operations modules in sys.modules
    # This prevents dynamic imports during tests from re-triggering circular imports
    print("[INFO] Pre-caching operations modules...")

    # First get list of all operations classes that should be available
    # These are defined in __init__.py but may not be in namespace yet
    operations_to_load = [
        # Grammar
        'POSOperations', 'PhonemeOperations', 'NaturalClassOperations',
        'EnvironmentOperations', 'PhonologicalRuleOperations', 'MorphRuleOperations',
        'GramCatOperations', 'InflectionFeatureOperations',
        # Lexicon
        'LexEntryOperations', 'LexSenseOperations', 'ExampleOperations',
        'LexReferenceOperations', 'VariantOperations', 'PronunciationOperations',
        'SemanticDomainOperations', 'ReversalOperations', 'EtymologyOperations',
        'AllomorphOperations',
        # TextsWords
        'TextOperations', 'WordformOperations', 'WfiAnalysisOperations',
        'ParagraphOperations', 'SegmentOperations', 'WfiGlossOperations',
        'WfiMorphBundleOperations', 'DiscourseOperations',
        # Notebook
        'NoteOperations', 'PersonOperations', 'LocationOperations',
        'AnthropologyOperations', 'DataNotebookOperations',
        # Lists
        'PublicationOperations', 'AgentOperations', 'ConfidenceOperations',
        'OverlayOperations', 'TranslationTypeOperations', 'PossibilityListOperations',
        # System
        'WritingSystemOperations', 'ProjectSettingsOperations', 'AnnotationDefOperations',
        'CheckOperations', 'CustomFieldOperations',
        # Shared
        'MediaOperations', 'FilterOperations',
    ]

    cached_count = 0
    for ops_name in operations_to_load:
        try:
            ops_class = getattr(flexlibs2, ops_name, None)
            if ops_class is not None:
                cached_count += 1
            else:
                print(f"[WARN] {ops_name} not found in flexlibs2 namespace")
        except Exception as e:
            print(f"[WARN] Could not access {ops_name}: {e}")

    print(f"[OK] Pre-cached {cached_count}/{len(operations_to_load)} operations modules")

except Exception as e:
    print(f"[WARN] Could not initialize FieldWorks: {e}")
    import traceback
    traceback.print_exc()


# ========== PYTEST CONFIGURATION ==========

def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line(
        "markers", "validation: mark test as validation test"
    )
    config.addinivalue_line(
        "markers", "phase2: mark test as Phase 2 (TextsWords, Grammar basics)"
    )
    config.addinivalue_line(
        "markers", "phase3: mark test as Phase 3 (Lexicon, more Grammar)"
    )
    config.addinivalue_line(
        "markers", "phase4: mark test as Phase 4 (all other categories)"
    )
    config.addinivalue_line(
        "markers", "write_enabled: mark test for write-enabled functionality"
    )
    config.addinivalue_line(
        "markers", "read_only: mark test for read-only project behavior"
    )
    config.addinivalue_line(
        "markers", "parameter_validation: mark test for parameter validation"
    )
    config.addinivalue_line(
        "markers", "type_checking: mark test for type validation"
    )
    config.addinivalue_line(
        "markers", "bounds_checking: mark test for bounds validation"
    )
    config.addinivalue_line(
        "markers", "string_validation: mark test for string validation"
    )


# ========== MOCK PROJECT FIXTURE ==========

class MockFLExProject:
    """
    Mock FLExProject for testing validation without actual database.

    Simulates write-enabled/read-only states and CanModify() behavior.
    """

    def __init__(self, write_enabled=True):
        """
        Initialize mock project.

        Args:
            write_enabled: If True, project can be modified. If False, read-only.
        """
        self.write_enabled = write_enabled
        self._can_modify = write_enabled
        self.project = Mock()

    def CanModify(self):
        """Return whether project can be modified."""
        return self._can_modify

    def set_write_enabled(self, enabled):
        """Change write-enabled state."""
        self.write_enabled = enabled
        self._can_modify = enabled

    def set_can_modify(self, can_modify):
        """Set CanModify() return value."""
        self._can_modify = can_modify


@pytest.fixture
def mock_project_write_enabled():
    """
    Fixture: Mock FLExProject with write enabled.

    Used for testing modification operations that require write access.
    """
    return MockFLExProject(write_enabled=True)


@pytest.fixture
def mock_project_read_only():
    """
    Fixture: Mock FLExProject in read-only mode.

    Used for testing behavior when write access is disabled.
    """
    return MockFLExProject(write_enabled=False)


@pytest.fixture
def mock_project():
    """
    Fixture: Default mock project (write-enabled).

    Convenience fixture for most tests.
    """
    return MockFLExProject(write_enabled=True)


# ========== MOCK OBJECT FIXTURES ==========

@pytest.fixture
def mock_lex_entry():
    """Fixture: Mock ILexEntry object."""
    entry = Mock()
    entry.Id = "guid-12345"
    entry.Hvo = 1001
    entry.SensesOS = Mock()
    entry.SensesOS.Count = 3
    entry.AlternateFormsOS = Mock()
    entry.AlternateFormsOS.Count = 2
    entry.Owner = None  # Will be set by test if needed
    return entry


@pytest.fixture
def mock_lex_sense():
    """Fixture: Mock ILexSense object."""
    sense = Mock()
    sense.Id = "guid-67890"
    sense.Hvo = 1002
    sense.Gloss = Mock()
    sense.Definition = Mock()
    sense.ExamplesOS = Mock()
    sense.ExamplesOS.Count = 2
    sense.Owner = None  # Will be set to entry by test if needed
    return sense


@pytest.fixture
def mock_writing_system():
    """Fixture: Mock IWritingSystemDefinition object."""
    ws = Mock()
    ws.Id = "en"
    ws.Handle = 1  # Writing system handle
    ws.LanguageName = "English"
    return ws


@pytest.fixture
def mock_allomorph():
    """Fixture: Mock IMoAllomorph object."""
    allo = Mock()
    allo.Id = "guid-allo-123"
    allo.Hvo = 1003
    allo.Form = Mock()
    allo.Owner = None  # Will be set to entry by test
    return allo


# ========== MOCK OPERATIONS FIXTURES ==========

@pytest.fixture
def mock_operations_class(mock_project_write_enabled):
    """
    Fixture: Mock operations class with validation methods.

    Simulates any operation class inheriting from BaseOperations.
    """
    class MockOperations:
        """Mock operations class with all validation methods."""

        def __init__(self, project):
            self.project = project

        def _EnsureWriteEnabled(self):
            """Ensure write is enabled (from BaseOperations)."""
            if not self.project.CanModify():
                raise Exception(
                    "Project is read-only or not open. "
                    "Cannot perform modifications. "
                    "Open the project with writeEnabled=True."
                )

        def _ValidateParam(self, param, param_name="parameter"):
            """Validate parameter is not None."""
            if param is None:
                raise Exception(f"{param_name} cannot be None")

        def _ValidateParamNotEmpty(self, param, param_name="parameter"):
            """Validate parameter is not None and not empty."""
            if param is None:
                raise Exception(f"{param_name} cannot be None")
            if len(param) == 0:
                raise Exception(f"{param_name} cannot be empty")

        def _ValidateInstanceOf(self, obj, expected_type, param_name="object"):
            """Validate object is instance of expected type."""
            if not isinstance(obj, expected_type):
                if isinstance(expected_type, tuple):
                    type_names = " or ".join(t.__name__ for t in expected_type)
                else:
                    type_names = expected_type.__name__
                raise TypeError(
                    f"{param_name} must be {type_names}, "
                    f"got {type(obj).__name__}"
                )

        def _ValidateStringNotEmpty(self, text, param_name="text"):
            """Validate string is not None and not empty."""
            if not isinstance(text, str):
                raise TypeError(
                    f"{param_name} must be a string, got {type(text).__name__}"
                )
            if text is None:
                raise Exception(f"{param_name} cannot be None")
            if len(text.strip()) == 0:
                raise Exception(
                    f"{param_name} cannot be empty or contain only whitespace"
                )

        def _ValidateIndexBounds(self, index, max_count, param_name="index"):
            """Validate index is within bounds [0, max_count-1]."""
            if not isinstance(index, int):
                raise TypeError(
                    f"{param_name} must be an integer, got {type(index).__name__}"
                )
            if index < 0:
                raise ValueError(
                    f"{param_name} cannot be negative, got {index}"
                )
            if index >= max_count:
                raise IndexError(
                    f"{param_name} out of bounds: {index} >= {max_count} "
                    f"(valid range: 0-{max_count - 1})"
                )

        def _ValidateOwner(self, obj, expected_owner, param_name="object"):
            """Validate object has expected owner."""
            if not hasattr(obj, "Owner"):
                raise AttributeError(
                    f"{param_name} does not have Owner property"
                )
            if obj.Owner != expected_owner:
                raise ValueError(
                    f"{param_name} owner does not match expected owner. "
                    f"Object owner: {obj.Owner}, Expected: {expected_owner}"
                )

        def _NormalizeMultiString(self, value):
            """Convert FLEx empty placeholder to Python empty string."""
            if value is None:
                return None
            if value == "***":
                return ""
            return value

    return MockOperations(mock_project_write_enabled)


# ========== ASSERTION HELPERS ==========

class ValidationAssertions:
    """Helper class with assertion methods for validation errors."""

    @staticmethod
    def assert_write_enabled_error(func, *args, **kwargs):
        """
        Assert that function raises exception for read-only project.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message
        """
        with pytest.raises(Exception) as exc_info:
            func(*args, **kwargs)

        assert "read-only" in str(exc_info.value).lower()
        return str(exc_info.value)

    @staticmethod
    def assert_param_error(func, *args, **kwargs):
        """
        Assert that function raises error for invalid parameter.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message
        """
        with pytest.raises(Exception) as exc_info:
            func(*args, **kwargs)

        assert "cannot be None" in str(exc_info.value)
        return str(exc_info.value)

    @staticmethod
    def assert_type_error(func, *args, **kwargs):
        """
        Assert that function raises TypeError for wrong type.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message
        """
        with pytest.raises(TypeError) as exc_info:
            func(*args, **kwargs)

        return str(exc_info.value)

    @staticmethod
    def assert_index_error(func, *args, **kwargs):
        """
        Assert that function raises IndexError for out-of-bounds index.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message
        """
        with pytest.raises(IndexError) as exc_info:
            func(*args, **kwargs)

        assert "out of bounds" in str(exc_info.value)
        return str(exc_info.value)

    @staticmethod
    def assert_value_error(func, *args, **kwargs):
        """
        Assert that function raises ValueError.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message
        """
        with pytest.raises(ValueError) as exc_info:
            func(*args, **kwargs)

        return str(exc_info.value)


@pytest.fixture
def assert_validation():
    """Fixture: Access validation assertion helpers."""
    return ValidationAssertions()


# ========== DATA GENERATORS ==========

class TestDataFactory:
    """Factory for generating test data."""

    @staticmethod
    def create_entries(count=5):
        """
        Generate mock lexical entries.

        Args:
            count: Number of entries to create

        Returns:
            List of mock ILexEntry objects
        """
        entries = []
        for i in range(count):
            entry = Mock()
            entry.Id = f"guid-entry-{i}"
            entry.Hvo = 2000 + i
            entry.SensesOS = Mock()
            entry.SensesOS.Count = (i % 3) + 1
            entries.append(entry)
        return entries

    @staticmethod
    def create_senses(count=3, owner=None):
        """
        Generate mock senses.

        Args:
            count: Number of senses to create
            owner: Owner (entry) for senses

        Returns:
            List of mock ILexSense objects
        """
        senses = []
        for i in range(count):
            sense = Mock()
            sense.Id = f"guid-sense-{i}"
            sense.Hvo = 3000 + i
            sense.Owner = owner
            senses.append(sense)
        return senses

    @staticmethod
    def create_writing_systems(count=2):
        """
        Generate mock writing systems.

        Args:
            count: Number of writing systems to create

        Returns:
            List of mock IWritingSystemDefinition objects
        """
        ws_list = [
            ("en", "English"),
            ("fr", "French"),
            ("es", "Spanish"),
            ("pt", "Portuguese"),
        ]

        systems = []
        for i in range(min(count, len(ws_list))):
            ws_id, ws_name = ws_list[i]
            ws = Mock()
            ws.Id = ws_id
            ws.LanguageName = ws_name
            ws.Handle = i + 1
            systems.append(ws)
        return systems


@pytest.fixture
def test_data():
    """Fixture: Access test data factory."""
    return TestDataFactory()


# ========== TEMPORARY DIRECTORY FIXTURE ==========

@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Fixture: Temporary directory for test files.

    Args:
        tmp_path: Pytest's tmp_path fixture

    Returns:
        Path to temporary directory
    """
    return tmp_path
