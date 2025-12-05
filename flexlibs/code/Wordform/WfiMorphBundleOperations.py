#
#   WfiMorphBundleOperations.py
#
#   Class: WfiMorphBundleOperations
#          Wordform morpheme bundle operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IWfiMorphBundle,
    IWfiMorphBundleFactory,
    IWfiAnalysis,
    ILexSense,
    IMoMorphType,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)

class WfiMorphBundleOperations(BaseOperations):
    """
    This class provides operations for managing wordform morpheme bundles.

    A WfiMorphBundle represents one morpheme in a wordform analysis, linking:
    - Morpheme form (surface representation)
    - Lexical sense (meaning from lexicon)
    - Morpheme type (stem, prefix, suffix, etc.)

    Morph bundles form the morphological breakdown, connecting texts to the lexicon.
    They enable interlinear glossing and parser training.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get analysis
        wordform = project.Wordforms.FindOrCreate("hlauka")
        analysis = project.WfiAnalyses.Create(wordform)

        # Create morph bundles for stem + suffix
        stem_bundle = project.WfiMorphBundles.Create(analysis, "hlauk-")
        suffix_bundle = project.WfiMorphBundles.Create(analysis, "-a")

        # Link to lexical entries
        stem_entry = project.LexEntry.Find("hlauk")
        if stem_entry and stem_entry.SensesOS.Count > 0:
            sense = stem_entry.SensesOS[0]
            project.WfiMorphBundles.SetSense(stem_bundle, sense)

        # Set morpheme type
        project.WfiMorphBundles.SetMorphemeType(stem_bundle, "stem")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize WfiMorphBundleOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for morph bundles.
        For WfiMorphBundle, we reorder analysis.MorphBundlesOS
        """
        return parent.MorphBundlesOS

    # --- Core CRUD Operations ---

    def GetAll(self, analysis_or_hvo):
        """
        Get all morpheme bundles in an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Yields:
            IWfiMorphBundle: Each morph bundle object in the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> for bundle in project.WfiMorphBundles.GetAll(analysis):
            ...     form = project.WfiMorphBundles.GetForm(bundle)
            ...     sense = project.WfiMorphBundles.GetSense(bundle)
            ...     gloss = project.Senses.GetGloss(sense) if sense else "?"
            ...     print(f"{form} = {gloss}")
            hlauk- = run
            -a = VERB

        Notes:
            - Returns empty generator if no morph bundles
            - Bundles ordered left-to-right in the word
            - Each bundle represents one morpheme
            - Use _GetSequence() for reordering bundles

        See Also:
            Create, Find, Delete
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        for bundle in analysis.MorphBundlesOS:
            yield bundle

    def Create(self, analysis_or_hvo, form, sense=None, wsHandle=None):
        """
        Create a new morpheme bundle in an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            form (str): The morpheme form text
            sense: Optional ILexSense object to link to
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiMorphBundle: The newly created morph bundle

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or form is None
            FP_ParameterError: If form is empty

        Example:
            >>> analysis = project.WfiAnalyses.Create(wordform)
            >>>
            >>> # Create stem bundle
            >>> stem = project.WfiMorphBundles.Create(analysis, "hlauk-")
            >>>
            >>> # Create suffix bundle with linked sense
            >>> suffix_entry = project.LexEntry.Find("-a")
            >>> if suffix_entry and suffix_entry.SensesOS.Count > 0:
            ...     sense = suffix_entry.SensesOS[0]
            ...     suffix = project.WfiMorphBundles.Create(analysis, "-a", sense)

        Notes:
            - Bundle is added to the analysis's morph bundles sequence
            - Bundles are ordered left-to-right in the word
            - If sense provided, it's automatically linked
            - Use SetMorphemeType() to specify stem/affix/etc.

        See Also:
            Delete, SetSense, SetForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if analysis_or_hvo is None:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Morpheme bundle form cannot be empty")

        analysis = self.__GetAnalysisObject(analysis_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the morph bundle using factory
        factory = self.project.project.ServiceLocator.GetService(IWfiMorphBundleFactory)
        new_bundle = factory.Create()

        # Add to analysis's morph bundles sequence
        analysis.MorphBundlesOS.Add(new_bundle)

        # Set the morpheme form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_bundle.Form.set_String(wsHandle, mkstr)

        # Link to sense if provided
        if sense:
            new_bundle.SenseRA = sense

        return new_bundle

    def Delete(self, bundle_or_hvo):
        """
        Delete a morpheme bundle from an analysis.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If bundle_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> bundles = list(project.WfiMorphBundles.GetAll(analysis))
            >>> if len(bundles) > 2:
            ...     # Delete incorrect morpheme
            ...     project.WfiMorphBundles.Delete(bundles[1])

        Warning:
            - This is a destructive operation
            - Cannot be undone
            - Changes the morphological breakdown
            - May affect parser training

        Notes:
            - Safe to delete incorrect parser guesses
            - Be careful with human-approved analyses
            - Analysis can exist with zero bundles

        See Also:
            Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not bundle_or_hvo:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)

        # Delete the bundle (LCM handles removal from collections)
        bundle.Delete()

    def Find(self, analysis_or_hvo, index):
        """
        Find a morph bundle by its index in the analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            index (int): Zero-based index of the morph bundle

        Returns:
            IWfiMorphBundle or None: The bundle object if found, None otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> # Get first morpheme (typically the stem)
            >>> first_bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> if first_bundle:
            ...     form = project.WfiMorphBundles.GetForm(first_bundle)
            ...     print(f"First morpheme: {form}")

        Notes:
            - Returns None if index out of range
            - Index 0 is typically the leftmost morpheme
            - Bundles are ordered left-to-right in the word
            - Use GetAll() to iterate all bundles

        See Also:
            GetAll, Create
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        if index < 0 or index >= analysis.MorphBundlesOS.Count:
            return None

        return analysis.MorphBundlesOS[index]

    # --- Property Access ---

    def GetForm(self, bundle_or_hvo, wsHandle=None):
        """
        Get the morpheme form of a morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The morpheme form text (empty string if not set)

        Raises:
            FP_NullParameterError: If bundle_or_hvo is None

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> form = project.WfiMorphBundles.GetForm(bundle)
            >>> print(form)
            hlauk-

        See Also:
            SetForm, Create
        """
        if not bundle_or_hvo:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        form = ITsString(bundle.Form.get_String(wsHandle)).Text
        return form or ""

    def SetForm(self, bundle_or_hvo, text, wsHandle=None):
        """
        Set the morpheme form of a morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO
            text (str): The new morpheme form text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If bundle_or_hvo or text is None
            FP_ParameterError: If text is empty

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> project.WfiMorphBundles.SetForm(bundle, "hlauka-")
            >>> print(project.WfiMorphBundles.GetForm(bundle))
            hlauka-

        See Also:
            GetForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not bundle_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        if not text or not text.strip():
            raise FP_ParameterError("Morpheme bundle form cannot be empty")

        bundle = self.__ResolveObject(bundle_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        bundle.Form.set_String(wsHandle, mkstr)

    # --- Lexicon Linking ---

    def GetSense(self, bundle_or_hvo):
        """
        Get the lexical sense linked to this morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO

        Returns:
            ILexSense or None: The linked sense, or None if not linked

        Raises:
            FP_NullParameterError: If bundle_or_hvo is None

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> sense = project.WfiMorphBundles.GetSense(bundle)
            >>> if sense:
            ...     gloss = project.Senses.GetGloss(sense)
            ...     entry = sense.Entry
            ...     headword = project.LexEntry.GetHeadword(entry)
            ...     print(f"{headword}: {gloss}")
            hlauk: run

        Notes:
            - Returns None if no sense linked
            - Sense links the morpheme to the lexicon
            - Essential for interlinear glossing
            - Parser uses sense links for training

        See Also:
            SetSense, project.Senses operations
        """
        if not bundle_or_hvo:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)

        return bundle.SenseRA if hasattr(bundle, 'SenseRA') else None

    def SetSense(self, bundle_or_hvo, sense):
        """
        Link a lexical sense to this morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO
            sense: ILexSense object to link (or None to clear link)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If bundle_or_hvo is None

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>>
            >>> # Find lexical entry and link its sense
            >>> entry = project.LexEntry.Find("hlauk")
            >>> if entry and entry.SensesOS.Count > 0:
            ...     sense = entry.SensesOS[0]
            ...     project.WfiMorphBundles.SetSense(bundle, sense)
            >>>
            >>> # Clear sense link
            >>> project.WfiMorphBundles.SetSense(bundle, None)

        Notes:
            - Sense link connects text to lexicon
            - Essential for interlinear glossing
            - Pass None to clear the link
            - Parser uses sense links for training
            - One bundle links to one sense

        See Also:
            GetSense, project.LexEntry.Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not bundle_or_hvo:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)

        if hasattr(bundle, 'SenseRA'):
            bundle.SenseRA = sense

    # --- Morpheme Type ---

    def GetMorphemeType(self, bundle_or_hvo):
        """
        Get the morpheme type (stem, prefix, suffix, etc.) of a morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO

        Returns:
            IMoMorphType or None: The morph type object, or None if not set

        Raises:
            FP_NullParameterError: If bundle_or_hvo is None

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> morph_type = project.WfiMorphBundles.GetMorphemeType(bundle)
            >>> if morph_type:
            ...     name = ITsString(morph_type.Name.BestAnalysisAlternative).Text
            ...     print(f"Morpheme type: {name}")
            Morpheme type: stem

        Notes:
            - Returns None if no type set
            - Common types: stem, root, prefix, suffix, infix
            - Type affects parsing and morphological rules
            - Should match the linked sense's entry morph type

        See Also:
            SetMorphemeType
        """
        if not bundle_or_hvo:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)

        return bundle.MorphRA if hasattr(bundle, 'MorphRA') else None

    def SetMorphemeType(self, bundle_or_hvo, type_or_name):
        """
        Set the morpheme type (stem, prefix, suffix, etc.) of a morph bundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or its HVO
            type_or_name: Either an IMoMorphType object or a type name (str)
                         such as "stem", "prefix", "suffix", etc.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If bundle_or_hvo or type_or_name is None
            FP_ParameterError: If type name not found

        Example:
            >>> bundle = project.WfiMorphBundles.Find(analysis, 0)
            >>> project.WfiMorphBundles.SetMorphemeType(bundle, "stem")
            >>>
            >>> suffix = project.WfiMorphBundles.Find(analysis, 1)
            >>> project.WfiMorphBundles.SetMorphemeType(suffix, "suffix")

        Notes:
            - Type should match morphological function
            - Common types: stem, root, prefix, suffix, infix, circumfix
            - Affects parsing and morphological analysis
            - Should match linked sense's entry morph type

        See Also:
            GetMorphemeType, project.LexEntry.GetAvailableMorphTypes
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not bundle_or_hvo:
            raise FP_NullParameterError()
        if type_or_name is None:
            raise FP_NullParameterError()

        bundle = self.__ResolveObject(bundle_or_hvo)

        # Resolve morph type if string provided
        if isinstance(type_or_name, str):
            morph_type = self.__FindMorphType(type_or_name)
            if not morph_type:
                raise FP_ParameterError(f"Morpheme type '{type_or_name}' not found")
            type_or_name = morph_type

        if hasattr(bundle, 'MorphRA'):
            bundle.MorphRA = type_or_name

    # --- Private Helper Methods ---

    def __ResolveObject(self, bundle_or_hvo):
        """
        Resolve HVO or object to IWfiMorphBundle.

        Args:
            bundle_or_hvo: Either an IWfiMorphBundle object or an HVO (int)

        Returns:
            IWfiMorphBundle: The resolved bundle object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a morph bundle
        """
        if isinstance(bundle_or_hvo, int):
            obj = self.project.Object(bundle_or_hvo)
            if not isinstance(obj, IWfiMorphBundle):
                raise FP_ParameterError("HVO does not refer to a morph bundle")
            return obj
        return bundle_or_hvo

    def __GetAnalysisObject(self, analysis_or_hvo):
        """
        Resolve HVO or object to IWfiAnalysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or an HVO (int)

        Returns:
            IWfiAnalysis: The resolved analysis object

        Raises:
            FP_ParameterError: If HVO doesn't refer to an analysis
        """
        if isinstance(analysis_or_hvo, int):
            obj = self.project.Object(analysis_or_hvo)
            if not isinstance(obj, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
            return obj
        return analysis_or_hvo

    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle

        Returns:
            int: The writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultVernWs
        )

    def __FindMorphType(self, name):
        """
        Find a morph type by name (case-insensitive).

        Args:
            name (str): The morph type name to search for

        Returns:
            IMoMorphType or None: The morph type object if found, None otherwise
        """
        name_lower = name.lower()

        morph_types = self.project.lp.LexDbOA.MorphTypesOA
        if not morph_types:
            return None

        # Search through all morph types (including subcategories)
        def search_morph_types(possibilities):
            for mt in possibilities:
                mt_name = mt.Name.BestAnalysisAlternative.Text
                if mt_name and mt_name.lower() == name_lower:
                    return mt
                # Search subcategories
                if mt.SubPossibilitiesOS.Count > 0:
                    found = search_morph_types(mt.SubPossibilitiesOS)
                    if found:
                        return found
            return None

        return search_morph_types(morph_types.PossibilitiesOS)
