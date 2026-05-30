#
#   MSAOperations.py
#
#   Class: MSAOperations
#          Morphosyntactic-analysis (MSA) creation operations for FieldWorks
#          Language Explorer projects via SIL Language and Culture Model
#          (LCM) API.
#
#          Pairs with morphosyntax_analysis.py (the reading wrapper) and
#          msa_collection.py (iteration). This module handles the creation
#          + attach side of the four concrete MSA types:
#          - MoStemMsa (kStem) -- stem entries, takes one POS
#          - MoDerivAffMsa (kDeriv) -- derivational affixes, from-POS + to-POS
#          - MoInflAffMsa (kInfl) -- inflectional affixes, POS + slots
#          - MoUnclassifiedAffixMsa (kUnclassified) -- catch-all affix
#
#          All four use the same idiom: build a SandboxGenericMSA with the
#          MsaType + POS info, call the type-specific factory's
#          Create(sense.Owner, sandbox) overload, then attach via
#          sense.MorphoSyntaxAnalysisRA.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations, OperationsMethod

# Import FLEx LCM types
from SIL.LCModel import (
    IMoStemMsa,
    IMoStemMsaFactory,
    IMoDerivAffMsa,
    IMoDerivAffMsaFactory,
    IMoInflAffMsa,
    IMoInflAffMsaFactory,
    IMoUnclassifiedAffixMsa,
    IMoUnclassifiedAffixMsaFactory,
    ILexSense,
    ILexEntry,
    LexEntryTags,
)
from SIL.LCModel.DomainServices import SandboxGenericMSA, MsaType

import clr

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ParameterError,
)


class MSAOperations(BaseOperations):
    """
    Creation + attach operations for morphosyntactic analyses (MSAs).

    A LexSense's grammatical analysis lives in
    ``sense.MorphoSyntaxAnalysisRA``, which is a reference to an MSA owned
    by ``sense.Entry.MorphoSyntaxAnalysesOC``. LCM offers four concrete
    MSA subtypes that share IMoMorphSynAnalysis as base; each subtype has
    its own factory whose 2-arg Create overload takes an owner (the sense's
    entry) and a SandboxGenericMSA descriptor.

    This wrapper hides the ServiceLocator + SandboxGenericMSA dance and
    auto-attaches the new MSA to the sense, mirroring the read-side
    coverage in MorphosyntaxAnalysis.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        entry = list(project.LexiconAllEntries())[0]
        sense = entry.SensesOS[0]

        # Stem MSA (most common case): assign POS to a lexical entry.
        verb_pos = project.GramCat.Find("Verb")
        project.MSA.CreateStem(sense, verb_pos)

        # Derivational affix: noun -> verb
        n_pos = project.GramCat.Find("Noun")
        v_pos = project.GramCat.Find("Verb")
        project.MSA.CreateDerivAff(sense, from_pos=n_pos, to_pos=v_pos)

    See Also:
        morphosyntax_analysis.MorphosyntaxAnalysis (reading)
        msa_collection.MSACollection (iteration)
    """

    def __init__(self, project):
        super().__init__(project)

    @OperationsMethod
    def CreateStem(self, sense, pos):
        """
        Create an IMoStemMsa, attach it to the sense.

        Args:
            sense: An ILexSense (or HVO) to attach the MSA to.
            pos: An IPartOfSpeech (or HVO) -- the grammatical category.

        Returns:
            IMoStemMsa: The newly created and attached MSA.

        Raises:
            FP_ReadOnlyError, FP_NullParameterError, FP_ParameterError.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")
        self._ValidateParam(pos, "pos")

        sense_obj = self.__ResolveSense(sense)
        pos_obj = self.__Resolve(pos)

        sandbox = SandboxGenericMSA()
        sandbox.MsaType = MsaType.kStem
        sandbox.MainPOS = pos_obj

        new_msa = self.__CreateAndAttach(
            sense_obj, sandbox, IMoStemMsaFactory
        )
        return IMoStemMsa(new_msa)

    @OperationsMethod
    def CreateDerivAff(self, sense, from_pos, to_pos):
        """
        Create an IMoDerivAffMsa, attach it to the sense.

        Args:
            sense: An ILexSense (or HVO) to attach the MSA to.
            from_pos: An IPartOfSpeech the affix attaches to (input category).
            to_pos: An IPartOfSpeech the affix produces (output category).

        Returns:
            IMoDerivAffMsa: The newly created and attached MSA.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")
        self._ValidateParam(from_pos, "from_pos")
        self._ValidateParam(to_pos, "to_pos")

        sense_obj = self.__ResolveSense(sense)
        from_pos_obj = self.__Resolve(from_pos)
        to_pos_obj = self.__Resolve(to_pos)

        sandbox = SandboxGenericMSA()
        sandbox.MsaType = MsaType.kDeriv
        sandbox.MainPOS = from_pos_obj
        sandbox.SecondaryPOS = to_pos_obj

        new_msa = self.__CreateAndAttach(
            sense_obj, sandbox, IMoDerivAffMsaFactory
        )
        return IMoDerivAffMsa(new_msa)

    @OperationsMethod
    def CreateInflAff(self, sense, pos, slots=None):
        """
        Create an IMoInflAffMsa, attach it to the sense.

        Args:
            sense: An ILexSense (or HVO) to attach the MSA to.
            pos: An IPartOfSpeech -- the category this affix inflects.
            slots: Optional sequence of IMoInflAffixSlot objects. Slots
                are added to the MSA's SlotsRC reference collection
                after creation (Phase 2 ownership-ordering doesn't apply
                to reference collections).

        Returns:
            IMoInflAffMsa: The newly created and attached MSA.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")
        self._ValidateParam(pos, "pos")

        sense_obj = self.__ResolveSense(sense)
        pos_obj = self.__Resolve(pos)

        sandbox = SandboxGenericMSA()
        sandbox.MsaType = MsaType.kInfl
        sandbox.MainPOS = pos_obj

        new_msa = self.__CreateAndAttach(
            sense_obj, sandbox, IMoInflAffMsaFactory
        )
        new_msa = IMoInflAffMsa(new_msa)

        if slots:
            for slot in slots:
                resolved = self.__Resolve(slot)
                new_msa.SlotsRC.Add(resolved)

        return new_msa

    @OperationsMethod
    def CreateUnclassifiedAffix(self, sense, pos):
        """
        Create an IMoUnclassifiedAffixMsa, attach it to the sense.

        Args:
            sense: An ILexSense (or HVO) to attach the MSA to.
            pos: An IPartOfSpeech (or HVO) -- the grammatical category.

        Returns:
            IMoUnclassifiedAffixMsa: The newly created and attached MSA.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")
        self._ValidateParam(pos, "pos")

        sense_obj = self.__ResolveSense(sense)
        pos_obj = self.__Resolve(pos)

        sandbox = SandboxGenericMSA()
        sandbox.MsaType = MsaType.kUnclassified
        sandbox.MainPOS = pos_obj

        new_msa = self.__CreateAndAttach(
            sense_obj, sandbox, IMoUnclassifiedAffixMsaFactory
        )
        return IMoUnclassifiedAffixMsa(new_msa)

    @OperationsMethod
    def SetStemMsaPos(self, sense, pos):
        """
        Update the POS on an existing IMoStemMsa attached to a sense.

        If the sense has no MSA, or if its MSA isn't a stem MSA, raises
        FP_ParameterError. For type conversion (e.g. stem -> deriv-aff)
        the caller should create a new MSA via CreateStem / CreateDerivAff;
        in-place conversion across MSA types is intentionally not
        supported by this wrapper because LCM doesn't expose a clean
        idiom for it.

        Args:
            sense: An ILexSense whose MSA should be updated.
            pos: New IPartOfSpeech (or HVO) for the stem.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")
        self._ValidateParam(pos, "pos")

        sense_obj = self.__ResolveSense(sense)
        existing = sense_obj.MorphoSyntaxAnalysisRA
        if existing is None:
            raise FP_ParameterError(
                "Sense has no MSA; use CreateStem to create one."
            )
        try:
            stem = IMoStemMsa(existing)
        except Exception:
            raise FP_ParameterError(
                "Sense's existing MSA is not a stem MSA. To change MSA "
                "type, create a new MSA with the appropriate Create* method."
            )

        pos_obj = self.__Resolve(pos)
        stem.PartOfSpeechRA = pos_obj

    @OperationsMethod
    def SetDerivAffMsaPos(self, sense, from_pos=None, to_pos=None):
        """
        Update the from-POS and/or to-POS on an existing IMoDerivAffMsa
        attached to a sense.

        If the sense has no MSA, or if its MSA isn't a derivational-affix
        MSA, raises FP_ParameterError. At least one of from_pos or to_pos
        must be supplied.

        Args:
            sense: An ILexSense whose MSA should be updated.
            from_pos: New IPartOfSpeech (or HVO) for the input category
                (FromPartOfSpeechRA). Pass None to leave unchanged.
            to_pos: New IPartOfSpeech (or HVO) for the output category
                (ToPartOfSpeechRA). Pass None to leave unchanged.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(sense, "sense")

        if from_pos is None and to_pos is None:
            raise FP_ParameterError(
                "At least one of from_pos or to_pos must be supplied."
            )

        sense_obj = self.__ResolveSense(sense)
        existing = sense_obj.MorphoSyntaxAnalysisRA
        if existing is None:
            raise FP_ParameterError(
                "Sense has no MSA; use CreateDerivAff to create one."
            )
        try:
            deriv = IMoDerivAffMsa(existing)
        except Exception:
            raise FP_ParameterError(
                "Sense's existing MSA is not a derivational-affix MSA. To "
                "change MSA type, create a new MSA with the appropriate "
                "Create* method."
            )

        if from_pos is not None:
            deriv.FromPartOfSpeechRA = self.__Resolve(from_pos)
        if to_pos is not None:
            deriv.ToPartOfSpeechRA = self.__Resolve(to_pos)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def __CreateAndAttach(self, sense, sandbox, factory_interface):
        """
        Common MSA-creation flow: resolve service, create with sandbox
        descriptor, attach to sense.

        Uses clr.GetClrType(factory_interface) because pythonnet's
        ServiceLocator.GetService overload needs the System.Type form of
        the interface rather than the raw interface object.
        """
        factory = self.project.project.Cache.ServiceLocator.GetService(
            clr.GetClrType(factory_interface)
        )
        if factory is None:
            raise FP_ParameterError(
                f"{factory_interface.__name__} service is unavailable."
            )

        # Factory.Create(owner, sandbox) -- the owner is the sense's
        # ENTRY, not the sense's direct Owner. For a subsense,
        # sense.Owner is the parent sense, not the entry; LCM expects
        # the enclosing ILexEntry, so walk up the ownership chain via
        # OwnerOfClass(LexEntryTags.kClassId). Same idiom that
        # LexSenseOperations.SetPartOfSpeech uses to resolve the owning
        # entry. (issue #129)
        entry = ILexEntry(sense.OwnerOfClass(LexEntryTags.kClassId))
        new_msa = factory.Create(entry, sandbox)
        sense.MorphoSyntaxAnalysisRA = new_msa
        return new_msa

    def __ResolveSense(self, sense_or_hvo):
        """Resolve a sense parameter, accepting either an object or HVO."""
        if isinstance(sense_or_hvo, int):
            obj = self.project.Object(sense_or_hvo)
            return ILexSense(obj)
        # Pass through; assume the caller gave us a usable sense object
        # or wrapper. Wrappers' _obj is unwrapped lazily by LCM via the
        # operations they pass through to.
        if hasattr(sense_or_hvo, "_obj"):
            return sense_or_hvo._obj
        return sense_or_hvo

    def __Resolve(self, obj_or_hvo):
        """Generic resolve -- HVO -> object, wrapper -> unwrapped."""
        if isinstance(obj_or_hvo, int):
            return self.project.Object(obj_or_hvo)
        if hasattr(obj_or_hvo, "_obj"):
            return obj_or_hvo._obj
        return obj_or_hvo
