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
import importlib


# ========== SESSION-SCOPED FIXTURE FOR FIELDWORKS INITIALIZATION ==========
# Using autouse=True ensures this runs before any tests, regardless of scope

@pytest.fixture(scope="session", autouse=True)
def initialize_flex_for_tests():
    """
    Initialize FieldWorks and flexlibs2 before running any tests.

    This fixture runs once per test session and ensures:
    1. FieldWorks DLLs are in sys.path
    2. FLEx services are initialized
    3. flexlibs2 package is fully imported with all operations
    4. Operations classes are available for tests

    Using autouse=True ensures this runs even if no test explicitly uses it.
    Using scope="session" ensures it runs only once for the entire test session.
    """
    print("[INFO] [SESSION FIXTURE] Initializing FieldWorks for tests...")
    try:
        # Step 1: Set up Windows registry access and FW paths
        import clr
        from System import Environment
        from Microsoft.Win32 import Registry

        # Get FieldWorks installation path from registry
        RegKey = r"SOFTWARE\SIL\FieldWorks\9"
        try:
            rKey = Registry.LocalMachine.OpenSubKey(RegKey)
            if rKey is None:
                rKey = Registry.CurrentUser.OpenSubKey(RegKey)

            if rKey:
                fw_code_dir = rKey.GetValue("RootCodeDir")
                if fw_code_dir and os.path.exists(os.path.join(fw_code_dir, "FieldWorks.exe")):
                    sys.path.append(fw_code_dir)
                    print(f"[OK] FieldWorks path added: {fw_code_dir}")
        except Exception as e:
            print(f"[WARN] Could not read registry: {e}")

        # Step 2: Load SIL assemblies
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
        print("[OK] FLEx services initialized")

        # Step 4: Initialize FLEx using FLExInitialize()
        print("[INFO] Running FLExInitialize()...")
        from flexlibs2.code.FLExInit import FLExInitialize
        FLExInitialize()
        print("[OK] FLExInitialize() complete")

        # Step 5: Import flexlibs2 package
        print("[INFO] Importing flexlibs2 package...")
        import flexlibs2
        print("[OK] flexlibs2 imported successfully")

        # Step 6: Manually import and add operations to flexlibs2 namespace
        # The __init__.py imports may not execute fully, so do it explicitly here
        print("[INFO] Loading operations modules...")
        operations_modules = [
            # Grammar
            ('flexlibs2.code.Grammar.POSOperations', 'POSOperations'),
            ('flexlibs2.code.Grammar.PhonemeOperations', 'PhonemeOperations'),
            ('flexlibs2.code.Grammar.NaturalClassOperations', 'NaturalClassOperations'),
            ('flexlibs2.code.Grammar.EnvironmentOperations', 'EnvironmentOperations'),
            ('flexlibs2.code.Grammar.PhonologicalRuleOperations', 'PhonologicalRuleOperations'),
            ('flexlibs2.code.Grammar.MorphRuleOperations', 'MorphRuleOperations'),
            ('flexlibs2.code.Grammar.GramCatOperations', 'GramCatOperations'),
            ('flexlibs2.code.Grammar.InflectionFeatureOperations', 'InflectionFeatureOperations'),
            # Lexicon
            ('flexlibs2.code.Lexicon.LexEntryOperations', 'LexEntryOperations'),
            ('flexlibs2.code.Lexicon.LexSenseOperations', 'LexSenseOperations'),
            ('flexlibs2.code.Lexicon.ExampleOperations', 'ExampleOperations'),
            ('flexlibs2.code.Lexicon.LexReferenceOperations', 'LexReferenceOperations'),
            ('flexlibs2.code.Lexicon.VariantOperations', 'VariantOperations'),
            ('flexlibs2.code.Lexicon.PronunciationOperations', 'PronunciationOperations'),
            ('flexlibs2.code.Lexicon.SemanticDomainOperations', 'SemanticDomainOperations'),
            ('flexlibs2.code.Lexicon.ReversalOperations', 'ReversalOperations'),
            ('flexlibs2.code.Lexicon.EtymologyOperations', 'EtymologyOperations'),
            ('flexlibs2.code.Lexicon.AllomorphOperations', 'AllomorphOperations'),
            # TextsWords
            ('flexlibs2.code.TextsWords.TextOperations', 'TextOperations'),
            ('flexlibs2.code.TextsWords.WordformOperations', 'WordformOperations'),
            ('flexlibs2.code.TextsWords.WfiAnalysisOperations', 'WfiAnalysisOperations'),
            ('flexlibs2.code.TextsWords.ParagraphOperations', 'ParagraphOperations'),
            ('flexlibs2.code.TextsWords.SegmentOperations', 'SegmentOperations'),
            ('flexlibs2.code.TextsWords.WfiGlossOperations', 'WfiGlossOperations'),
            ('flexlibs2.code.TextsWords.WfiMorphBundleOperations', 'WfiMorphBundleOperations'),
            ('flexlibs2.code.TextsWords.DiscourseOperations', 'DiscourseOperations'),
            # Notebook
            ('flexlibs2.code.Notebook.NoteOperations', 'NoteOperations'),
            ('flexlibs2.code.Notebook.PersonOperations', 'PersonOperations'),
            ('flexlibs2.code.Notebook.LocationOperations', 'LocationOperations'),
            ('flexlibs2.code.Notebook.AnthropologyOperations', 'AnthropologyOperations'),
            ('flexlibs2.code.Notebook.DataNotebookOperations', 'DataNotebookOperations'),
            # Lists
            ('flexlibs2.code.Lists.PublicationOperations', 'PublicationOperations'),
            ('flexlibs2.code.Lists.AgentOperations', 'AgentOperations'),
            ('flexlibs2.code.Lists.ConfidenceOperations', 'ConfidenceOperations'),
            ('flexlibs2.code.Lists.OverlayOperations', 'OverlayOperations'),
            ('flexlibs2.code.Lists.TranslationTypeOperations', 'TranslationTypeOperations'),
            ('flexlibs2.code.Lists.PossibilityListOperations', 'PossibilityListOperations'),
            # System
            ('flexlibs2.code.System.WritingSystemOperations', 'WritingSystemOperations'),
            ('flexlibs2.code.System.ProjectSettingsOperations', 'ProjectSettingsOperations'),
            ('flexlibs2.code.System.AnnotationDefOperations', 'AnnotationDefOperations'),
            ('flexlibs2.code.System.CheckOperations', 'CheckOperations'),
            ('flexlibs2.code.System.CustomFieldOperations', 'CustomFieldOperations'),
            # Shared
            ('flexlibs2.code.Shared.MediaOperations', 'MediaOperations'),
            ('flexlibs2.code.Shared.FilterOperations', 'FilterOperations'),
        ]

        loaded_count = 0
        for module_path, class_name in operations_modules:
            try:
                module = importlib.import_module(module_path)
                ops_class = getattr(module, class_name)
                setattr(flexlibs2, class_name, ops_class)
                loaded_count += 1
            except ImportError as e:
                print(f"[WARN] Could not import {class_name}: {e}")
            except AttributeError as e:
                print(f"[WARN] {class_name} not found in {module_path}: {e}")
            except Exception as e:
                print(f"[WARN] Error loading {class_name}: {e}")

        print(f"[OK] Loaded {loaded_count}/{len(operations_modules)} operations classes")

        # Verify
        ops_found = [x for x in dir(flexlibs2) if 'Operations' in x]
        print(f"[INFO] flexlibs2 now has {len(ops_found)} operations available")

    except Exception as e:
        print(f"[ERROR] FLEx initialization failed: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise so pytest knows initialization failed

    yield  # Let tests run

    # Cleanup after all tests (if needed)
    print("[INFO] Test session complete")


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
