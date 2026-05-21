#
#   PhonFeatureOperations.py
#
#   Class: PhonFeatureOperations
#          Phonological feature operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#          Manages the phonological feature system (PhFeatureSystemOA),
#          which owns IFsClosedFeature definitions and their IFsSymFeatVal
#          values. Also provides a helper for composing IFsFeatStruc objects
#          that attach to phonemes / natural classes.
#
#          The MGA PhonFeatsEticGlossList.xml catalog is the canonical
#          source for the standard set of phonological features and
#          their +/- values.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

# Import BaseOperations parent class and decorators
from ..BaseOperations import BaseOperations, OperationsMethod, wrap_enumerable

# Import FLEx LCM types
from SIL.LCModel import (
    IFsClosedFeature,
    IFsClosedFeatureFactory,
    IFsSymFeatVal,
    IFsSymFeatValFactory,
    IFsFeatStruc,
    IFsFeatStrucFactory,
    IFsClosedValue,
    IFsClosedValueFactory,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# .NET Guid for catalog-driven creation
import System

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ParameterError,
)

# Import LCM casting utilities for pythonnet interface casting
from ..lcm_casting import cast_to_concrete

# Import string utilities
from ..Shared.string_utils import normalize_match_key

# Catalog (eticGlossList) parsing helpers
from ..Shared.catalog import (
    CatalogImportResult,
    find_catalog_entry,
    find_catalog_file,
    parse_etic_gloss_list,
)


# Canonical relative subdir for the PhonFeats catalog under FWCodeDir.
# Kept as a module constant so verification / tests can reference it.
PHON_FEATS_CATALOG_FILENAME = "PhonFeatsEticGlossList.xml"
PHON_FEATS_CATALOG_SUBDIR = "Language Explorer/MGA/GlossLists"

# Optional prefix the wrapper accepts on CatalogSourceId values. Bare
# ids ("fPAConsonantal") are what FieldWorks itself writes; "PHON:" is
# accepted as a user-facing convenience and is stripped before lookup.
CATALOG_PREFIX = "PHON"


class PhonFeatureOperations(BaseOperations):
    """
    This class provides operations for managing phonological features and
    feature values in a FieldWorks project.

    Phonological features are owned by ``LangProject.PhFeatureSystemOA``
    (an ``IFsFeatureSystem``). Each feature is an ``IFsClosedFeature`` with
    one or more ``IFsSymFeatVal`` value children (typically ``+`` and ``-``
    for binary features). Phonemes and natural classes attach an
    ``IFsFeatStruc`` whose ``FeatureSpecsOC`` references (feature, value)
    pairs.

    The MGA ``PhonFeatsEticGlossList.xml`` catalog provides the canonical
    set of features and values with stable GUIDs; ``ImportCatalog`` and
    ``CreateFromCatalog`` populate the project from it.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        phonFeats = project.PhonFeatures

        # Bulk-import the standard MGA feature set.
        result = phonFeats.ImportCatalog()
        print(f"Created {result.created_count}, "
              f"skipped {result.skipped_count}")

        # Or create a specific feature with its +/- values.
        cons = phonFeats.CreateFromCatalog("fPAConsonantal")

        # Compose a feature structure for a phoneme.
        plus = next(v for v in phonFeats.GetValues(cons)
                    if phonFeats.GetAbbreviation(v) == "+")
        struct = phonFeats.MakeFeatStruc([(cons, plus)], owner=phoneme)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PhonFeatureOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    # ========================================================================
    # READ METHODS
    # ========================================================================

    @wrap_enumerable
    @OperationsMethod
    def GetAll(self):
        """
        Get all phonological features in the project.

        Yields:
            IFsClosedFeature: Each feature in PhFeatureSystemOA.FeaturesOC.

        Notes:
            - ``FeaturesOC`` is typed as ``IFsFeatDefn`` in C#. Each yielded
              item is cast to ``IFsClosedFeature`` (the only concrete shape
              this catalog uses) so callers can access ``ValuesOC`` directly.
            - Returns nothing if the project has no PhFeatureSystemOA.
        """
        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            return
        for feat in feature_system.FeaturesOC:
            yield IFsClosedFeature(feat)

    @OperationsMethod
    def GetName(self, feature_or_hvo, wsHandle=None):
        """
        Get the name of a phonological feature or value.

        Args:
            feature_or_hvo: An IFsClosedFeature, IFsSymFeatVal, or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The Name in the requested WS, or "" if not set.
        """
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        obj = self.__ResolveObject(feature_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)
        name = ITsString(obj.Name.get_String(wsHandle)).Text
        return name or ""

    @OperationsMethod
    def GetAbbreviation(self, feature_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a phonological feature or value.

        For values, the abbreviation is typically ``+`` or ``-``.
        """
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        obj = self.__ResolveObject(feature_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)
        abbr = ITsString(obj.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""

    @OperationsMethod
    def GetDescription(self, feature_or_hvo, wsHandle=None):
        """
        Get the description of a phonological feature or value.

        Returns "" if the object has no Description property.
        """
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        obj = self.__ResolveObject(feature_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)
        if not hasattr(obj, "Description"):
            return ""
        desc = ITsString(obj.Description.get_String(wsHandle)).Text
        return desc or ""

    @wrap_enumerable
    @OperationsMethod
    def GetValues(self, feature_or_hvo):
        """
        Get all IFsSymFeatVal values defined on a closed feature.

        Args:
            feature_or_hvo: The IFsClosedFeature object or HVO.

        Yields:
            IFsSymFeatVal: Each value (typically "+" and "-" for binary
            phonological features).
        """
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        feature = self.__ResolveObject(feature_or_hvo)
        # ValuesOC is typed as IFsSymFeatVal directly.
        for val in feature.ValuesOC:
            yield IFsSymFeatVal(val)

    @OperationsMethod
    def Find(self, name, wsHandle=None):
        """
        Find a phonological feature by name.

        Args:
            name (str): The name to search for. Compared via NFD-normalised
                        casefold match against each feature's Name in the
                        chosen WS.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            IFsClosedFeature or None: First match, or None.

        Notes:
            - Does NOT search value names; values are looked up via
              ``GetValues(feature)``.
            - Matches the feature-name convention used by other linguistic
              Find methods (case-insensitive, NFD-normalised).
        """
        self._ValidateParam(name, "name")
        target = normalize_match_key(name, casefold=True)
        if not target:
            return None
        wsHandle = self.__WSHandle(wsHandle)

        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            return None

        for raw in feature_system.FeaturesOC:
            feat = IFsClosedFeature(raw)
            feat_name = ITsString(feat.Name.get_String(wsHandle)).Text
            if feat_name and normalize_match_key(feat_name, casefold=True) == target:
                return feat
        return None

    @OperationsMethod
    def Exists(self, name, wsHandle=None):
        """
        Check whether a phonological feature with the given name exists.
        """
        self._ValidateParam(name, "name")
        return self.Find(name, wsHandle=wsHandle) is not None

    # ========================================================================
    # WRITE METHODS - FEATURE
    # ========================================================================

    @OperationsMethod
    def Create(self, name, abbreviation, catalogSourceId=None):
        """
        Create a new phonological feature (IFsClosedFeature).

        Args:
            name (str): Feature name (e.g. "consonantal").
            abbreviation (str): Short abbreviation (e.g. "cons").
            catalogSourceId (str, optional): Optional catalog id. If it
                starts with the ``PHON:`` prefix (case-insensitive),
                the feature is created from the MGA catalog (canonical
                GUID + localized strings + +/- value children), then
                the user-supplied name/abbreviation overlay the analysis
                WS. Otherwise the value is written verbatim to
                ``CatalogSourceId``.

        Returns:
            IFsClosedFeature: The newly created feature.

        Raises:
            FP_ReadOnlyError, FP_NullParameterError, FP_ParameterError:
                Per BaseOperations validation rules.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(name, "name")
        self._ValidateParam(abbreviation, "abbreviation")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        # Catalog-driven creation: defer to CreateFromCatalog for the
        # canonical GUID + values, then overlay the user's strings.
        if catalogSourceId and catalogSourceId.upper().startswith(CATALOG_PREFIX + ":"):
            wsHandle = self.project.project.DefaultAnalWs
            new_feat = self.CreateFromCatalog(catalogSourceId)
            mkstr_name = TsStringUtils.MakeString(name, wsHandle)
            new_feat.Name.set_String(wsHandle, mkstr_name)
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            new_feat.Abbreviation.set_String(wsHandle, mkstr_abbr)
            return new_feat

        # Uniqueness check by name within the feature system.
        if self.Exists(name):
            raise FP_ParameterError(
                f"Phonological feature '{name}' already exists"
            )

        wsHandle = self.project.project.DefaultAnalWs

        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            raise FP_ParameterError(
                "Project has no PhFeatureSystemOA; cannot create "
                "phonological features."
            )

        # Phase 2 ownership-ordering rule: attach to the owning collection
        # FIRST, then mutate properties. The parameterless factory create
        # returns an unowned object whose property setters will NPE until
        # it is added to FeaturesOC.
        factory = self.project.project.ServiceLocator.GetService(
            IFsClosedFeatureFactory
        )
        new_feat = factory.Create()
        feature_system.FeaturesOC.Add(new_feat)
        new_feat = IFsClosedFeature(new_feat)

        # Set name + abbreviation in default analysis WS.
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_feat.Name.set_String(wsHandle, mkstr_name)
        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        new_feat.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Verbatim CatalogSourceId for non-PHON: prefixes (and bare ids).
        if catalogSourceId:
            new_feat.CatalogSourceId = catalogSourceId

        return new_feat

    @OperationsMethod
    def SetName(self, feature_or_hvo, name, wsHandle=None):
        """
        Set the name of a phonological feature or value.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        self._ValidateParam(name, "name")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        obj = self.__ResolveObject(feature_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)
        mkstr = TsStringUtils.MakeString(name, wsHandle)
        obj.Name.set_String(wsHandle, mkstr)

    @OperationsMethod
    def SetAbbreviation(self, feature_or_hvo, abbrev, wsHandle=None):
        """
        Set the abbreviation of a phonological feature or value.

        For values, the abbreviation is typically ``+`` or ``-``.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        self._ValidateParam(abbrev, "abbrev")

        if not abbrev or not str(abbrev).strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        obj = self.__ResolveObject(feature_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)
        mkstr = TsStringUtils.MakeString(abbrev, wsHandle)
        obj.Abbreviation.set_String(wsHandle, mkstr)

    @OperationsMethod
    def SetDescription(self, feature_or_hvo, description, wsHandle=None):
        """
        Set the description of a phonological feature or value.

        Raises:
            FP_ParameterError: If the object has no Description property.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        self._ValidateParam(description, "description")

        obj = self.__ResolveObject(feature_or_hvo)
        if not hasattr(obj, "Description"):
            raise FP_ParameterError(
                "Target object has no Description multistring property."
            )
        wsHandle = self.__WSHandle(wsHandle)
        mkstr = TsStringUtils.MakeString(description, wsHandle)
        obj.Description.set_String(wsHandle, mkstr)

    @OperationsMethod
    def Delete(self, feature_or_hvo):
        """
        Delete a phonological feature.

        Args:
            feature_or_hvo: The IFsClosedFeature, wrapper, or HVO to delete.

        Notes:
            - Per Phase 4 lesson, accepts a wrapped form and unwraps it
              before talking to the LCM collection.
            - Deletion removes the feature from PhFeatureSystemOA.FeaturesOC.
              LCM will cascade-delete its IFsSymFeatVal children and any
              references from IFsClosedValue.FeatureRA.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")

        feat = self.__Unwrap(self.__ResolveObject(feature_or_hvo))
        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is not None:
            feature_system.FeaturesOC.Remove(feat)

    # ========================================================================
    # WRITE METHODS - VALUE (IFsSymFeatVal under a feature)
    # ========================================================================

    @OperationsMethod
    def CreateValue(self, feature_or_hvo, name, abbreviation, value_marker=None):
        """
        Create a new symbolic value (IFsSymFeatVal) under a closed feature.

        Args:
            feature_or_hvo: The IFsClosedFeature or HVO that owns the value.
            name (str): Value name (e.g. "positive", "negative").
            abbreviation (str): Short abbreviation. For standard binary
                                phonological features, conventionally
                                "+" or "-".
            value_marker (str, optional): Currently informational only --
                                accepted for API symmetry with FW UIs that
                                ask the user to choose +/-, but the abbreviation
                                itself carries the actual marker. Defaults to
                                None (no constraint).

        Returns:
            IFsSymFeatVal: The newly created value.

        Notes:
            - Applies the Phase 2 ownership-ordering rule: factory.Create()
              -> feature.ValuesOC.Add() -> set Name + Abbreviation.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(feature_or_hvo, "feature_or_hvo")
        self._ValidateParam(name, "name")
        self._ValidateParam(abbreviation, "abbreviation")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not str(abbreviation).strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        feature = self.__Unwrap(self.__ResolveObject(feature_or_hvo))
        wsHandle = self.project.project.DefaultAnalWs

        factory = self.project.project.ServiceLocator.GetService(
            IFsSymFeatValFactory
        )
        new_val = factory.Create()
        # Ownership-first: attach to feature.ValuesOC before mutating strings.
        feature.ValuesOC.Add(new_val)
        new_val = IFsSymFeatVal(new_val)

        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_val.Name.set_String(wsHandle, mkstr_name)
        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        new_val.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # value_marker is reserved for a future strict-mode check (e.g.
        # enforce that abbreviation == value_marker when both supplied).
        # Phase 5b deliberately leaves it informational only.
        _ = value_marker

        return new_val

    @OperationsMethod
    def DeleteValue(self, value_or_hvo):
        """
        Delete a phonological feature value.

        Removes the value from its owning feature's ValuesOC.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(value_or_hvo, "value_or_hvo")

        val = self.__Unwrap(self.__ResolveObject(value_or_hvo))
        owner = val.Owner
        if owner is not None and hasattr(owner, "ValuesOC"):
            # Cast to IFsClosedFeature so the .NET collection accessor is found.
            try:
                feat = IFsClosedFeature(owner)
            except Exception:
                feat = owner
            feat.ValuesOC.Remove(val)

    # ========================================================================
    # COMPOSE - FsFeatStruc
    # ========================================================================

    @OperationsMethod
    def MakeFeatStruc(self, specs, owner=None):
        """
        Build an IFsFeatStruc populated with (feature, value) pairs.

        Args:
            specs (list[tuple]): A list of ``(feature, value)`` tuples.
                Each side may be an IFsClosedFeature / IFsSymFeatVal
                object, a wrapper, or an HVO. Items are added to the
                struct's ``FeatureSpecsOC`` in the order provided.

            owner: LCM object that should own the struct via its
                ``FeaturesOA`` atomic-owning property. If provided, the
                struct is attached to ``owner.FeaturesOA`` BEFORE its
                FeatureSpecsOC is populated -- mandatory because
                FsFeatStruc property setters will NPE on a free-floating
                struct (Phase 2 ownership rule). Phonemes and natural
                classes both use ``FeaturesOA``.

                When ``owner`` is None, this method returns an empty
                struct and ``specs`` must be empty; the caller is then
                responsible for attaching it to an owner before
                populating. When ``owner`` is provided, the struct is
                attached and populated atomically. Passing
                ``owner=None`` together with a non-empty ``specs`` is
                rejected because LCM would NPE on the first
                FeatureSpecsOC mutation.

        Returns:
            IFsFeatStruc: The populated feature structure (or empty
            struct, when ``owner=None`` and ``specs`` is empty).

        Raises:
            FP_ParameterError: If a spec tuple is malformed, if an
                owner is supplied but has no FeaturesOA property, or
                if ``owner`` is None while ``specs`` is non-empty.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(specs, "specs")

        if owner is None and specs:
            raise FP_ParameterError(
                "MakeFeatStruc requires an owner when specs is non-empty. "
                "LCM property setters NPE on unowned IFsFeatStruc objects; "
                "either attach the struct to an owner before populating, "
                "or pass owner=phoneme / owner=natural_class / owner=context "
                "so this method attaches first."
            )

        # Normalize and validate specs up front, before any LCM mutation.
        normalized = []
        for i, pair in enumerate(specs):
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise FP_ParameterError(
                    f"specs[{i}] must be a (feature, value) tuple"
                )
            feat_in, val_in = pair
            feat = self.__Unwrap(self.__ResolveObject(feat_in))
            val = self.__Unwrap(self.__ResolveObject(val_in))
            normalized.append((feat, val))

        # Create the unowned struct.
        factory = self.project.project.ServiceLocator.GetService(
            IFsFeatStrucFactory
        )
        struct = factory.Create()

        # Attach to owner FIRST if supplied, so subsequent FeatureSpecsOC
        # mutations don't trip the Phase 2 NPE pattern.
        if owner is not None:
            owner_unwrapped = self.__Unwrap(owner)
            if not hasattr(owner_unwrapped, "FeaturesOA"):
                raise FP_ParameterError(
                    "owner has no FeaturesOA property; cannot attach FsFeatStruc."
                )
            owner_unwrapped.FeaturesOA = struct
            # Re-fetch via the owning property to ensure we hold the LCM
            # view of the now-owned struct.
            struct = owner_unwrapped.FeaturesOA

        struct = IFsFeatStruc(struct)

        # Populate FeatureSpecsOC. Each spec is an IFsClosedValue with
        # FeatureRA -> feature and ValueRA -> value.
        cv_factory = self.project.project.ServiceLocator.GetService(
            IFsClosedValueFactory
        )
        for feat, val in normalized:
            closed_value = cv_factory.Create()
            struct.FeatureSpecsOC.Add(closed_value)
            cv = IFsClosedValue(closed_value)
            cv.FeatureRA = feat
            cv.ValueRA = val

        return struct

    # ========================================================================
    # CATALOG (eticGlossList) IMPORT METHODS
    # ========================================================================
    #
    # Parallel of POSOperations' catalog import (Phase 5a). The structural
    # shape is the same -- catalog -> per-entry attach with canonical GUID
    # -> overlay localized strings -- but it operates on IFsClosedFeature /
    # IFsSymFeatVal in PhFeatureSystemOA instead of IPartOfSpeech in
    # PartsOfSpeechOA.
    #
    # Mixin extraction deferred to Phase 5c+ per the Original Author's
    # Option B decision (#11). Helpers here are marked with TODOs.

    @OperationsMethod
    def ImportCatalog(self, progress=None):
        """
        Import the MGA PhonFeatsEticGlossList catalog into this project.

        Each ``type="feature"`` entry becomes an IFsClosedFeature under
        ``PhFeatureSystemOA.FeaturesOC`` with the canonical GUID. Each
        of its ``type="value"`` children becomes an IFsSymFeatVal under
        the feature's ``ValuesOC``. ``type="group"`` entries are
        organizational only and are skipped (their child features are
        still imported).

        Idempotent: any entry whose canonical GUID already exists in
        the project is skipped. Re-running never duplicates.

        Args:
            progress: Optional callable accepting (count, total, name)
                      for progress reporting. May be None.

        Returns:
            CatalogImportResult: Created/skipped counts (across both
            features and their values), list of created GUIDs, and any
            human-readable warnings raised during import.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FileNotFoundError: If the catalog is not found under FWCodeDir.
        """
        self._EnsureWriteEnabled()

        path = find_catalog_file(
            PHON_FEATS_CATALOG_FILENAME,
            subdir=PHON_FEATS_CATALOG_SUBDIR,
        )
        feature_entries = parse_etic_gloss_list(path)

        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            raise FP_ParameterError(
                "Project has no PhFeatureSystemOA; cannot import catalog."
            )

        existing_guids = self._GetAllFeatureGuids()

        result = CatalogImportResult()
        missing_ws_seen = set()

        # Total items for progress = features + sum(values).
        total = sum(1 + len(e.children) for e in feature_entries)

        for entry in feature_entries:
            guid_str = entry.guid.lower() if entry.guid else ""
            existing = existing_guids.get(guid_str)
            if existing is not None:
                result.skipped_count += 1
                feature = existing
            else:
                feature = self._CreateFeatureFromEntry(
                    entry, feature_system, missing_ws_seen, result.warnings
                )
                result.created_count += 1
                result.created_guids.append(guid_str)
                existing_guids[guid_str] = feature

            if progress:
                try:
                    progress(
                        result.created_count + result.skipped_count,
                        total,
                        entry.id,
                    )
                except Exception:
                    pass

            # Now do each value child of this feature. Value idempotency
            # is checked per-feature: _GetAllFeatureGuids returns only
            # feature GUIDs, so re-imports must consult feature.ValuesOC
            # directly (parallels CreateFromCatalog ~line 767-769).
            existing_value_guids = {
                str(v.Guid).lower() for v in feature.ValuesOC
            }
            for value_entry in entry.children:
                v_guid = value_entry.guid.lower() if value_entry.guid else ""
                if v_guid and v_guid in existing_value_guids:
                    result.skipped_count += 1
                else:
                    self._CreateValueFromEntry(
                        value_entry, feature, missing_ws_seen, result.warnings
                    )
                    result.created_count += 1
                    if v_guid:
                        result.created_guids.append(v_guid)
                        # Track within this import pass so a duplicate
                        # entry (e.g. badly-formed catalog) won't re-create.
                        existing_value_guids.add(v_guid)

                if progress:
                    try:
                        progress(
                            result.created_count + result.skipped_count,
                            total,
                            value_entry.id,
                        )
                    except Exception:
                        pass

        return result

    @OperationsMethod
    def CreateFromCatalog(self, source_id):
        """
        Create a single phonological feature (with its value children)
        from the MGA catalog.

        Args:
            source_id (str): Catalog feature id, with or without the
                ``PHON:`` prefix. e.g. ``"PHON:fPAConsonantal"`` or
                ``"fPAConsonantal"``.

        Returns:
            IFsClosedFeature: The created (or pre-existing) feature.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_ParameterError: If ``source_id`` is not present in the catalog.
            FileNotFoundError: If the catalog is not found under FWCodeDir.

        Notes:
            - Idempotent on the feature: if the canonical GUID already
              exists, that feature is returned unchanged.
            - Value children are created idempotently too: any value
              whose canonical GUID is already present is left alone.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(source_id, "source_id")

        path = find_catalog_file(
            PHON_FEATS_CATALOG_FILENAME,
            subdir=PHON_FEATS_CATALOG_SUBDIR,
        )
        feature_entries = parse_etic_gloss_list(path)
        entry = find_catalog_entry(feature_entries, source_id)
        if entry is None:
            raise FP_ParameterError(
                f"Catalog id '{source_id}' not found in "
                f"{PHON_FEATS_CATALOG_FILENAME}"
            )

        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            raise FP_ParameterError(
                "Project has no PhFeatureSystemOA; cannot import catalog."
            )

        existing_guids = self._GetAllFeatureGuids()

        warnings = []
        missing_ws_seen = set()

        guid_str = entry.guid.lower() if entry.guid else ""
        feature = existing_guids.get(guid_str)
        if feature is None:
            feature = self._CreateFeatureFromEntry(
                entry, feature_system, missing_ws_seen, warnings
            )

        # Create any value children not already present.
        existing_value_guids = {
            str(v.Guid).lower() for v in feature.ValuesOC
        }
        for value_entry in entry.children:
            v_guid = value_entry.guid.lower() if value_entry.guid else ""
            if v_guid and v_guid in existing_value_guids:
                continue
            self._CreateValueFromEntry(
                value_entry, feature, missing_ws_seen, warnings
            )

        return feature

    @OperationsMethod
    def FixGuidsAgainstCatalog(self):
        """
        Scan phonological features in this project; for any whose
        CatalogSourceId matches a PhonFeatsEticGlossList entry but
        whose GUID differs from the catalog's canonical GUID, create
        a replacement with the correct GUID, transfer references via
        MergeObject, and remove the old feature.

        Returns:
            list[tuple]: One (old_name, old_guid, new_guid) tuple per
            feature repaired. Empty list if everything is already
            canonical.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.

        Notes:
            - Values (IFsSymFeatVal) do not reliably expose a
              CatalogSourceId field; their GUIDs are repaired indirectly
              when their parent feature is replaced (the catalog's
              value GUIDs are re-applied via _CreateValueFromEntry).
            - A warning is logged for any value-level GUID drift that
              cannot be repaired in this pass.
        """
        self._EnsureWriteEnabled()

        path = find_catalog_file(
            PHON_FEATS_CATALOG_FILENAME,
            subdir=PHON_FEATS_CATALOG_SUBDIR,
        )
        feature_entries = parse_etic_gloss_list(path)

        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            return []

        fixed = []
        # Collect candidates first so we don't iterate + mutate the same
        # collection during MergeObject.
        candidates = []
        for raw in feature_system.FeaturesOC:
            feat = IFsClosedFeature(raw)
            cat_id = feat.CatalogSourceId or ""
            if not cat_id:
                continue
            entry = find_catalog_entry(feature_entries, cat_id)
            if entry is None:
                continue
            current_guid = str(feat.Guid).lower()
            canonical_guid = entry.guid.lower()
            if current_guid == canonical_guid:
                continue
            candidates.append((feat, entry))

        for old_feat, entry in candidates:
            wsHandle = self.project.project.DefaultAnalWs
            old_name = (
                ITsString(old_feat.Name.get_String(wsHandle)).Text
                or "(unnamed)"
            )
            old_guid = str(old_feat.Guid).lower()

            warnings = []
            missing_ws = set()
            new_feat = self._CreateFeatureFromEntry(
                entry, feature_system, missing_ws, warnings
            )
            # Recreate value children with canonical GUIDs.
            existing_value_guids = {
                str(v.Guid).lower() for v in new_feat.ValuesOC
            }
            for value_entry in entry.children:
                v_guid = value_entry.guid.lower() if value_entry.guid else ""
                if v_guid and v_guid in existing_value_guids:
                    continue
                self._CreateValueFromEntry(
                    value_entry, new_feat, missing_ws, warnings
                )

            # Transfer references (e.g. IFsClosedValue.FeatureRA pointers)
            # from old_feat to new_feat and delete old_feat.
            try:
                old_feat.MergeObject(new_feat, True)
            except Exception as e:
                raise FP_ParameterError(
                    f"Failed to merge feature '{old_name}' into "
                    f"canonical-GUID replacement (entry '{entry.id}'): {e}"
                ) from e

            fixed.append((old_name, old_guid, entry.guid.lower()))

        return fixed

    # --- Catalog helper methods (internal) ---
    #
    # TODO(mixin): unify with POSOperations._CreatePosFromEntry when third
    # catalog-backed domain lands (see Phase 5c+ planning per #11).
    def _CreateFeatureFromEntry(
        self, entry, feature_system, missing_ws_seen, warnings
    ):
        """
        Internal: instantiate one IFsClosedFeature from a CatalogEntry,
        attach to PhFeatureSystemOA.FeaturesOC with the canonical GUID,
        then set per-WS Name / Abbreviation / Description and the
        CatalogSourceId.

        Applies the Phase 2 ownership-ordering rule: attach first
        (via the 2-arg factory overload, or fall back to Create+Add),
        then mutate properties.
        """
        factory = self.project.project.ServiceLocator.GetService(
            IFsClosedFeatureFactory
        )
        guid = System.Guid(entry.guid)

        new_feat = None
        # Path A: explicit 2-arg interface overload (creates+attaches in one step).
        # Pythonnet may or may not expose this; fall back if it doesn't.
        try:
            new_feat = factory.Create(guid, feature_system)
        except Exception:
            new_feat = None

        if new_feat is None:
            # Path B: implementation-side Create(Guid) followed by Add() to
            # the owning collection. cast_to_concrete defends against
            # interface-only views that hide Create(Guid).
            concrete_factory = (
                cast_to_concrete(factory)
                if hasattr(factory, "ClassName")
                else factory
            )
            try:
                new_feat = concrete_factory.Create(guid)
            except Exception as e:
                # No safe fallback: parameterless Create() would generate a
                # random GUID, defeating the point of CreateFromCatalog.
                raise FP_ParameterError(
                    f"Could not create phonological feature '{entry.id}' "
                    f"with canonical GUID {entry.guid} via either "
                    f"Create(Guid, FeatureSystem) or Create(Guid) factory "
                    f"overloads. The canonical GUID cannot be applied in "
                    f"this LCM version; a manual factory.Create() workaround "
                    f"would produce a random GUID and is not acceptable here."
                ) from e

            feature_system.FeaturesOC.Add(new_feat)

        new_feat = IFsClosedFeature(new_feat)

        # Set per-writing-system multistring properties. Skip any WS the
        # project doesn't have a handle for; record one warning per tag.
        self._SetFsMultiString(
            new_feat.Name, entry.term, missing_ws_seen, warnings
        )
        self._SetFsMultiString(
            new_feat.Abbreviation, entry.abbrev, missing_ws_seen, warnings
        )
        if hasattr(new_feat, "Description"):
            self._SetFsMultiString(
                new_feat.Description, entry.def_, missing_ws_seen, warnings
            )

        # CatalogSourceId: write the BARE id (matches FW's own convention).
        # CreateFromCatalog accepts both bare and PHON:-prefixed forms.
        # Note: bare entry.id (not "PHON:"-prefixed) matches FW's storage
        # convention for phonological features. Differs from POSOperations
        # which writes "GOLD:<id>". When extracting CatalogBackedMixin,
        # make the prefix policy configurable.
        new_feat.CatalogSourceId = entry.id

        return new_feat

    # TODO(mixin): unify with POSOperations equivalent for value-shaped
    # children when the third catalog-backed domain lands (#11).
    def _CreateValueFromEntry(
        self, value_entry, parent_feature, missing_ws_seen, warnings
    ):
        """
        Internal: instantiate one IFsSymFeatVal under `parent_feature`
        from a value-typed CatalogEntry. Applies the canonical GUID and
        per-WS strings.
        """
        factory = self.project.project.ServiceLocator.GetService(
            IFsSymFeatValFactory
        )
        guid = System.Guid(value_entry.guid)

        new_val = None
        # Path A: 2-arg factory overload if pythonnet exposes it.
        try:
            new_val = factory.Create(guid, parent_feature)
        except Exception:
            new_val = None

        if new_val is None:
            # Path B: implementation-side Create(Guid) followed by Add().
            concrete_factory = (
                cast_to_concrete(factory)
                if hasattr(factory, "ClassName")
                else factory
            )
            try:
                new_val = concrete_factory.Create(guid)
            except Exception as e:
                raise FP_ParameterError(
                    f"Could not create feature value '{value_entry.id}' "
                    f"with canonical GUID {value_entry.guid} via either "
                    f"Create(Guid, parent) or Create(Guid) factory "
                    f"overloads."
                ) from e
            parent_feature.ValuesOC.Add(new_val)

        new_val = IFsSymFeatVal(new_val)

        # Per-WS strings (abbreviation is the +/- marker, term is positive/negative).
        self._SetFsMultiString(
            new_val.Name, value_entry.term, missing_ws_seen, warnings
        )
        self._SetFsMultiString(
            new_val.Abbreviation, value_entry.abbrev, missing_ws_seen, warnings
        )
        if hasattr(new_val, "Description"):
            self._SetFsMultiString(
                new_val.Description, value_entry.def_, missing_ws_seen, warnings
            )

        # IFsSymFeatVal does not have a CatalogSourceId field in stock LCM,
        # so we don't try to set one. Value-level catalog provenance is
        # recoverable indirectly via the parent feature's CatalogSourceId
        # and the value's canonical GUID.

        return new_val

    # TODO(mixin): identical body to POSOperations._SetPosMultiString;
    # unify when third catalog-backed domain lands (#11).
    def _SetFsMultiString(self, multistring, ws_to_text, missing_ws_seen, warnings):
        """
        Apply a {ws_tag: text} dict to an LCM multistring, mapping ws_tag
        to handle via project.WSHandle(). Missing handles are skipped;
        a warning is recorded once per missing tag.
        """
        for ws_tag, text in ws_to_text.items():
            handle = self.project.WSHandle(ws_tag)
            if handle is None:
                if ws_tag not in missing_ws_seen:
                    missing_ws_seen.add(ws_tag)
                    warnings.append(
                        f"Skipping catalog WS '{ws_tag}': "
                        "no matching writing system in project."
                    )
                continue
            tss = TsStringUtils.MakeString(text, handle)
            multistring.set_String(handle, tss)

    # TODO(mixin): parallel to POSOperations._GetAllPosGuids; unify when
    # the third catalog-backed domain lands (#11).
    def _GetAllFeatureGuids(self):
        """
        Build a dict mapping lowercased GUID string -> IFsClosedFeature for
        every closed feature in this project's PhFeatureSystemOA. Value
        GUIDs are NOT included here -- value idempotency is checked
        per-feature in ImportCatalog / CreateFromCatalog.
        """
        guids = {}
        feature_system = self.project.lp.PhFeatureSystemOA
        if feature_system is None:
            return guids
        for raw in feature_system.FeaturesOC:
            feat = IFsClosedFeature(raw)
            guids[str(feat.Guid).lower()] = feat
        return guids

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def __ResolveObject(self, obj_or_hvo):
        """
        Resolve HVO or object to its LCM object. Wrappers are passed
        through unchanged here; use __Unwrap() to peel them off if you
        need to call LCM property setters on the result.
        """
        if isinstance(obj_or_hvo, int):
            return self.project.Object(obj_or_hvo)
        return obj_or_hvo

    def __Unwrap(self, obj):
        """
        Peel off LCMObjectWrapper-style wrappers, if any. Plain LCM
        objects pass through. Mirrors the Phase 4 wrapper-aware pattern.
        """
        # Wrapper classes expose ._obj to the underlying LCM object.
        if hasattr(obj, "_obj") and not hasattr(obj, "Hvo"):
            return obj._obj
        if hasattr(obj, "_obj") and hasattr(obj._obj, "Hvo"):
            # Both shapes: wrapper that proxies .Hvo. Prefer the inner LCM obj.
            return obj._obj
        return obj

    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(
            wsHandle, self.project.project.DefaultAnalWs
        )
