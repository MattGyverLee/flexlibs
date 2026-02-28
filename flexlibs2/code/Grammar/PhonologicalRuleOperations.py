#
#   PhonologicalRuleOperations.py
#
#   Class: PhonologicalRuleOperations
#          Phonological rule operations for FieldWorks Language Explorer
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
    IPhRegularRuleFactory,  # Fixed: was IPhPhonRuleFactory
    IPhSegRuleRHSFactory,
    IPhSegmentRuleFactory,
    IPhSimpleContextNCFactory,
    IPhSimpleContextSegFactory,
    IPhIterationContextFactory,
    ICmObjectRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ParameterError,
)

class PhonologicalRuleOperations(BaseOperations):
    """
    This class provides operations for managing phonological rules in a
    FieldWorks project.

    Phonological rules define systematic sound changes that apply in specific
    phonological environments. They consist of input specifications, output
    specifications, and contextual conditions.

    Usage::

        from flexlibs2 import FLExProject, PhonologicalRuleOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        phonRuleOps = PhonologicalRuleOperations(project)

        # Get all phonological rules
        for rule in phonRuleOps.GetAll():
            name = phonRuleOps.GetName(rule)
            desc = phonRuleOps.GetDescription(rule)
            print(f"{name}: {desc}")

        # Create a new phonological rule
        rule = phonRuleOps.Create("Voicing Assimilation")
        phonRuleOps.SetDescription(rule, "Obstruents become voiced before vowels")

        # Add input/output components
        phonRuleOps.AddInputSegment(rule, phoneme_t)
        phonRuleOps.AddOutputSegment(rule, phoneme_d)

        # Set phonological context
        phonRuleOps.SetRightContext(rule, vowel_class)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PhonologicalRuleOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for phonological rules.
        For PhonologicalRule, we reorder parent.PhonRulesOS
        """
        return parent.PhonRulesOS

    def GetAll(self):
        """
        Get all phonological rules in the project.

        Returns:
            RuleCollection: Smart collection of PhonologicalRule wrapped objects.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rules = phonRuleOps.GetAll()
            >>> print(rules)  # Shows type breakdown
            RuleCollection (12 total)
              PhRegularRule: 7 (58%)
              PhMetathesisRule: 3 (25%)
              PhReduplicationRule: 2 (17%)

            >>> # Access individual rules
            >>> for rule in rules:
            ...     print(rule.name)

            >>> # Filter to specific type
            >>> regular_only = rules.regular_rules()

            >>> # Filter by name
            >>> voicing_rules = rules.filter(name_contains='voicing')

        Notes:
            - Returns RuleCollection (smart collection) instead of generator
            - Wrapped rules hide ClassName/casting complexity
            - Use rule.name instead of GetName(rule)
            - Use rule.input_contexts instead of accessing StrucDescOS
            - Returns empty collection if no phonological data defined
            - Type breakdown is visible when printed

        See Also:
            Create, Find, RuleCollection, PhonologicalRule
        """
        from .phonological_rule import PhonologicalRule
        from .rule_collection import RuleCollection

        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data:
            return RuleCollection()

        rules = []
        if hasattr(phon_data, 'PhonRulesOS'):
            for rule in phon_data.PhonRulesOS:
                wrapped = PhonologicalRule(rule)
                rules.append(wrapped)

        return RuleCollection(rules)

    def Create(self, name, description=None):
        """
        Create a new phonological rule.

        Args:
            name (str): The name of the rule (e.g., "Voicing Assimilation").
            description (str, optional): Optional description of the rule.
                Defaults to None.

        Returns:
            IPhPhonRule: The newly created phonological rule object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Create("Voicing Assimilation",
            ...     "Voiceless stops become voiced between vowels")
            >>> print(phonRuleOps.GetName(rule))
            Voicing Assimilation

            >>> # Create and configure
            >>> rule = phonRuleOps.Create("Final Devoicing")
            >>> phonRuleOps.SetDescription(rule, "Obstruents devoice word-finally")

        Notes:
            - Name should describe the phonological process
            - Description is optional but recommended
            - Rule is created in the default analysis writing system
            - New rules start as inactive by default
            - Must add input/output specifications separately

        See Also:
            Delete, SetDescription, AddInputSegment, AddOutputSegment
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(name, "name")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new phonological rule using the factory
        factory = self.project.project.ServiceLocator.GetService(IPhRegularRuleFactory)
        new_rule = factory.Create()

        # Add to the phonological rules collection (must be done before setting properties)
        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data:
            raise FP_ParameterError("Project has no phonological data defined")

        phon_data.PhonRulesOS.Add(new_rule)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_rule.Name.set_String(wsHandle, mkstr_name)

        # Set description if provided
        if description:
            mkstr_desc = TsStringUtils.MakeString(description, wsHandle)
            new_rule.Description.set_String(wsHandle, mkstr_desc)

        return new_rule

    def Delete(self, rule_or_hvo):
        """
        Delete a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> obsolete = phonRuleOps.Create("Obsolete Rule")
            >>> # ... realize it's not needed
            >>> phonRuleOps.Delete(obsolete)

        Warning:
            - Deletion is permanent and cannot be undone
            - Any references to this rule will be broken
            - Consider deactivating instead of deleting

        See Also:
            Create, GetAll
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        # Resolve to rule object
        rule = self.__ResolveObject(rule_or_hvo)

        # Remove from phonological rules collection
        phon_data = self.project.lp.PhonologicalDataOA
        if phon_data and hasattr(phon_data, 'PhonRulesOS'):
            if rule in phon_data.PhonRulesOS:
                phon_data.PhonRulesOS.Remove(rule)

    def Exists(self, name):
        """
        Check if a phonological rule with the given name exists.

        Args:
            name (str): The name to search for.

        Returns:
            bool: True if a rule with this name exists, False otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> if phonRuleOps.Exists("Voicing Assimilation"):
            ...     print("Rule already exists")
            >>> else:
            ...     rule = phonRuleOps.Create("Voicing Assimilation")

        See Also:
            Find, GetAll, Create
        """
        self._ValidateParam(name, "name")

        return self.Find(name) is not None

    def Find(self, name):
        """
        Find a phonological rule by name.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            PhonologicalRule or None: The wrapped rule object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Find("Voicing Assimilation")
            >>> if rule:
            ...     print(f"Found: {rule.name}")
            ...     print(f"Direction: {rule.direction}")

            >>> # Case-insensitive search
            >>> rule = phonRuleOps.Find("voicing assimilation")

        Notes:
            - Search is case-insensitive
            - Returns first matching rule if multiple exist
            - Searches in default analysis writing system
            - Returns wrapped PhonologicalRule, not raw LCM object

        See Also:
            Exists, GetAll, PhonologicalRule
        """
        self._ValidateParam(name, "name")

        name_lower = name.lower()
        for wrapped_rule in self.GetAll():
            if wrapped_rule.name.lower() == name_lower:
                return wrapped_rule

        return None

    def GetName(self, rule_or_hvo, wsHandle=None):
        """
        Get the name of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The rule name, or empty string if not set.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> for rule in phonRuleOps.GetAll():
            ...     name = phonRuleOps.GetName(rule)
            ...     print(name)
            Voicing Assimilation
            Final Devoicing

        See Also:
            SetName, GetDescription
        """
        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(rule.Name.get_String(wsHandle)).Text
        return name or ""

    def SetName(self, rule_or_hvo, name, wsHandle=None):
        """
        Set the name of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> phonRuleOps.SetName(rule, "Intervocalic Voicing")

        See Also:
            GetName, SetDescription
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")
        self._ValidateParam(name, "name")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        rule = self.__ResolveObject(rule_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        rule.Name.set_String(wsHandle, mkstr)

    def GetDescription(self, rule_or_hvo, wsHandle=None):
        """
        Get the description of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The rule description, or empty string if not set.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> for rule in phonRuleOps.GetAll():
            ...     name = phonRuleOps.GetName(rule)
            ...     desc = phonRuleOps.GetDescription(rule)
            ...     print(f"{name}: {desc}")

        See Also:
            SetDescription, GetName
        """
        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        desc = ITsString(rule.Description.get_String(wsHandle)).Text
        return desc or ""

    def SetDescription(self, rule_or_hvo, description, wsHandle=None):
        """
        Set the description of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            description (str): The new description.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or description is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> phonRuleOps.SetDescription(rule,
            ...     "Voiceless stops become voiced between vowels")

        See Also:
            GetDescription, SetName
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")
        self._ValidateParam(description, "description")

        rule = self.__ResolveObject(rule_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(description, wsHandle)
        rule.Description.set_String(wsHandle, mkstr)

    def GetStratum(self, rule_or_hvo):
        """
        Get the stratum of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.

        Returns:
            IMoStratum or None: The stratum object if set, None otherwise.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> stratum = phonRuleOps.GetStratum(rule)
            >>> if stratum:
            ...     print(f"Rule applies in stratum: {stratum.Name.BestAnalysisAlternative.Text}")

        Notes:
            - Strata define ordering levels for phonological rules
            - Rules in lower strata apply before rules in higher strata
            - Returns None if no stratum is assigned

        See Also:
            SetStratum
        """
        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)

        if hasattr(rule, 'StratumRA') and rule.StratumRA:
            return rule.StratumRA

        return None

    def SetStratum(self, rule_or_hvo, stratum):
        """
        Set the stratum of a phonological rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            stratum: The IMoStratum object, HVO, or None to clear.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> # Get first stratum
            >>> morph_data = project.lp.MorphologicalDataOA
            >>> if morph_data and morph_data.StrataOS.Count > 0:
            ...     stratum = morph_data.StrataOS[0]
            ...     phonRuleOps.SetStratum(rule, stratum)

        See Also:
            GetStratum
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)

        if hasattr(rule, 'StratumRA'):
            if stratum is None:
                rule.StratumRA = None
            else:
                if isinstance(stratum, int):
                    stratum = self.project.Object(stratum)
                rule.StratumRA = stratum

    def GetDirection(self, rule_or_hvo):
        """
        Get the direction of rule application.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.

        Returns:
            int: The direction value (0=left-to-right, 1=right-to-left,
                2=simultaneous).

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> direction = phonRuleOps.GetDirection(rule)
            >>> if direction == 0:
            ...     print("Left-to-right application")

        See Also:
            SetDirection
        """
        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)

        if hasattr(rule, 'Direction'):
            return rule.Direction

        return 0  # Default: left-to-right

    def SetDirection(self, rule_or_hvo, direction):
        """
        Set the direction of rule application.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            direction (int): 0=left-to-right, 1=right-to-left, 2=simultaneous.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.
            FP_ParameterError: If direction is not 0, 1, or 2.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> # Set to right-to-left
            >>> phonRuleOps.SetDirection(rule, 1)

        See Also:
            GetDirection
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        if direction not in [0, 1, 2]:
            raise FP_ParameterError("Direction must be 0 (L-R), 1 (R-L), or 2 (simultaneous)")

        rule = self.__ResolveObject(rule_or_hvo)

        if hasattr(rule, 'Direction'):
            rule.Direction = direction

    def AddInputSegment(self, rule_or_hvo, phoneme_or_class):
        """
        Add an input segment or natural class to the rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            phoneme_or_class: A phoneme object, natural class object, or HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or phoneme_or_class is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Create("Voicing Rule")
            >>> # Add voiceless stop as input
            >>> phoneme_t = project.Phonemes.Find("/t/")
            >>> phonRuleOps.AddInputSegment(rule, phoneme_t)

        Notes:
            - Input specifies what the rule looks for
            - Can be a single phoneme or a natural class
            - Multiple inputs create alternate patterns

        See Also:
            AddOutputSegment, GetInputSegments
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")
        self._ValidateParam(phoneme_or_class, "phoneme_or_class")

        rule = self.__ResolveObject(rule_or_hvo)

        # Resolve phoneme/class if HVO
        if isinstance(phoneme_or_class, int):
            phoneme_or_class = self.project.Object(phoneme_or_class)

        # Access the rule's input contexts
        # This requires accessing the StrucDesc (structural description)
        # which contains the input specification
        if hasattr(rule, 'StrucDescOS') and rule.StrucDescOS.Count == 0:
            # Create a segment rule for the input
            seg_factory = self.project.project.ServiceLocator.GetService(IPhSimpleContextSegFactory)
            input_context = seg_factory.Create()
            rule.StrucDescOS.Add(input_context)

        # Add the phoneme/class to the input context
        if hasattr(rule, 'StrucDescOS') and rule.StrucDescOS.Count > 0:
            input_context = rule.StrucDescOS[0]
            if hasattr(input_context, 'FeatureStructureRA'):
                input_context.FeatureStructureRA = phoneme_or_class

    def AddOutputSegment(self, rule_or_hvo, phoneme_or_class):
        """
        Add an output segment or natural class to the rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            phoneme_or_class: A phoneme object, natural class object, or HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or phoneme_or_class is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Create("Voicing Rule")
            >>> # Add voiced stop as output
            >>> phoneme_d = project.Phonemes.Find("/d/")
            >>> phonRuleOps.AddOutputSegment(rule, phoneme_d)

        Notes:
            - Output specifies what the rule produces
            - Can be a single phoneme or a natural class
            - Should correspond to input segments

        See Also:
            AddInputSegment, GetOutputSegments
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")
        self._ValidateParam(phoneme_or_class, "phoneme_or_class")

        rule = self.__ResolveObject(rule_or_hvo)

        # Resolve phoneme/class if HVO
        if isinstance(phoneme_or_class, int):
            phoneme_or_class = self.project.Object(phoneme_or_class)

        # Create RHS (right-hand side) for output if needed
        if hasattr(rule, 'RightHandSidesOS') and rule.RightHandSidesOS.Count == 0:
            rhs_factory = self.project.project.ServiceLocator.GetService(IPhSegRuleRHSFactory)
            rhs = rhs_factory.Create()
            rule.RightHandSidesOS.Add(rhs)

        # Add the phoneme/class to the output
        if hasattr(rule, 'RightHandSidesOS') and rule.RightHandSidesOS.Count > 0:
            rhs = rule.RightHandSidesOS[0]
            if hasattr(rhs, 'StrucChangeOS') and hasattr(phoneme_or_class, 'Hvo'):
                # Add to structural change specification
                seg_factory = self.project.project.ServiceLocator.GetService(IPhSimpleContextSegFactory)
                output_seg = seg_factory.Create()
                output_seg.FeatureStructureRA = phoneme_or_class
                rhs.StrucChangeOS.Add(output_seg)

    def SetLeftContext(self, rule_or_hvo, context_item):
        """
        Set the left context (environment before the target) for the rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            context_item: A phoneme, natural class, or environment object/HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Create("Final Devoicing")
            >>> # Set word boundary as left context
            >>> phonRuleOps.SetLeftContext(rule, None)  # No left constraint

        Notes:
            - Left context specifies what must precede the input
            - Pass None to indicate no left context constraint
            - Can be a phoneme, natural class, or word boundary

        See Also:
            SetRightContext, GetLeftContext
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)

        # Resolve context item if HVO
        if isinstance(context_item, int):
            context_item = self.project.Object(context_item)

        # Set left context in the rule's structural description
        # This typically uses the LeftContext property
        if hasattr(rule, 'StrucDescOS') and rule.StrucDescOS.Count > 0:
            input_context = rule.StrucDescOS[0]
            if hasattr(input_context, 'LeftContextOA'):
                if context_item is None:
                    input_context.LeftContextOA = None
                else:
                    # Create context specification
                    ctx_factory = self.project.project.ServiceLocator.GetService(IPhSimpleContextSegFactory)
                    left_ctx = ctx_factory.Create()
                    left_ctx.FeatureStructureRA = context_item
                    input_context.LeftContextOA = left_ctx

    def SetRightContext(self, rule_or_hvo, context_item):
        """
        Set the right context (environment after the target) for the rule.

        Args:
            rule_or_hvo: The IPhPhonRule object or HVO.
            context_item: A phoneme, natural class, or environment object/HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Create("Intervocalic Voicing")
            >>> # Get vowel natural class
            >>> vowels = project.NaturalClasses.Find("Vowels")
            >>> # Set vowel as right context
            >>> phonRuleOps.SetRightContext(rule, vowels)

        Notes:
            - Right context specifies what must follow the input
            - Pass None to indicate no right context constraint
            - Can be a phoneme, natural class, or word boundary

        See Also:
            SetLeftContext, GetRightContext
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(rule_or_hvo, "rule_or_hvo")

        rule = self.__ResolveObject(rule_or_hvo)

        # Resolve context item if HVO
        if isinstance(context_item, int):
            context_item = self.project.Object(context_item)

        # Set right context in the rule's structural description
        if hasattr(rule, 'StrucDescOS') and rule.StrucDescOS.Count > 0:
            input_context = rule.StrucDescOS[0]
            if hasattr(input_context, 'RightContextOA'):
                if context_item is None:
                    input_context.RightContextOA = None
                else:
                    # Create context specification
                    ctx_factory = self.project.project.ServiceLocator.GetService(IPhSimpleContextSegFactory)
                    right_ctx = ctx_factory.Create()
                    right_ctx.FeatureStructureRA = context_item
                    input_context.RightContextOA = right_ctx

    def Duplicate(self, item_or_hvo, insert_after=True, deep=True):
        """
        Duplicate a phonological rule, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IPhPhonRule object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source rule.
                                If False, insert at end of rules list.
            deep (bool): If True (default), deep copy owned objects (StrucDescOS, RightHandSidesOS).
                        If False, owned objects are not copied.

        Returns:
            IPhPhonRule: The newly created duplicate rule with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> voicing = phonRuleOps.Create("Voicing Assimilation")
            >>> # Deep copy (default - includes StrucDescOS and RightHandSidesOS)
            >>> copy = phonRuleOps.Duplicate(voicing)
            >>> print(phonRuleOps.GetName(copy))
            Voicing Assimilation

            >>> # Shallow copy (no owned objects)
            >>> rule = phonRuleOps.Create("Complex Rule")
            >>> copy = phonRuleOps.Duplicate(rule, deep=False)

        Notes:
            - Uses collection.CreateAndAppendElement() for proper LCM registration
            - insert_after=True preserves the original rule's position
            - Copies all simple properties: Name, Description, Direction, StratumRA
            - Copies all owned objects when deep=True:
              - StrucDescOS (structural description / input)
              - RightHandSidesOS (output specifications)
            - Emulates FieldWorks' "Duplicate selected Phonological Rule" pattern

        See Also:
            Create, Delete, SetDirection
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(item_or_hvo, "item_or_hvo")

        # Get source rule
        source = self.__ResolveObject(item_or_hvo)

        # Create new rule using collection's CreateAndAppendElement for proper registration
        phon_data = self.project.lp.PhonologicalDataOA

        # Try to use CreateAndAppendElement (proper LCM registration)
        if hasattr(phon_data.PhonRulesOS, 'CreateAndAppendElement'):
            duplicate = phon_data.PhonRulesOS.CreateAndAppendElement()
            # If we need to insert at a specific position, remove and reinsert
            if insert_after:
                source_index = phon_data.PhonRulesOS.IndexOf(source)
                phon_data.PhonRulesOS.Remove(duplicate)
                phon_data.PhonRulesOS.Insert(source_index + 1, duplicate)
        else:
            # Fallback to factory.Create() + Add/Insert
            factory = self.project.project.ServiceLocator.GetService(IPhRegularRuleFactory)
            duplicate = factory.Create()
            if insert_after:
                source_index = phon_data.PhonRulesOS.IndexOf(source)
                phon_data.PhonRulesOS.Insert(source_index + 1, duplicate)
            else:
                phon_data.PhonRulesOS.Add(duplicate)

        # Clone all properties (simple, reference, and owned objects)
        if deep:
            # Deep clone using the LCM cloning utilities
            from ..lcm_casting import clone_properties
            clone_properties(source, duplicate, self.project)
        else:
            # Shallow copy - only simple properties
            duplicate.Name.CopyAlternatives(source.Name)
            duplicate.Description.CopyAlternatives(source.Description)

            # Copy Reference Atomic (RA) properties
            if hasattr(source, 'StratumRA') and source.StratumRA:
                duplicate.StratumRA = source.StratumRA

            # Copy integer properties
            if hasattr(source, 'Direction'):
                duplicate.Direction = source.Direction

        return duplicate

    def __ResolveObject(self, rule_or_hvo):
        """
        Resolve HVO or object to IPhPhonRule.

        Args:
            rule_or_hvo: Either an IPhPhonRule object or an HVO (int).

        Returns:
            IPhPhonRule: The resolved rule object.
        """
        if isinstance(rule_or_hvo, int):
            return self.project.Object(rule_or_hvo)
        return rule_or_hvo

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get dictionary of syncable properties for cross-project synchronization.

        Args:
            item: The IPhPhonRule object.

        Returns:
            dict: Dictionary mapping property names to their values.
                Keys are property names, values are the property values.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = list(phonRuleOps.GetAll())[0]
            >>> props = phonRuleOps.GetSyncableProperties(rule)
            >>> print(props.keys())
            dict_keys(['Name', 'Description', 'Direction', 'StratumGuid'])

        Notes:
            - Returns all MultiString properties (all writing systems)
            - Returns Direction integer property (0=L-R, 1=R-L, 2=simultaneous)
            - Returns StratumGuid as string (GUID of referenced stratum)
            - Does not include owned objects (StrucDescOS, RightHandSidesOS)
            - Does not include GUID or HVO of the rule itself
        """
        rule = self.__ResolveObject(item)

        # Get all writing systems for MultiString properties
        ws_factory = self.project.project.WritingSystemFactory
        all_ws = {ws.Id: ws.Handle for ws in ws_factory.WritingSystems}

        props = {}

        # MultiString properties
        for prop_name in ['Name', 'Description']:
            if hasattr(rule, prop_name):
                prop_obj = getattr(rule, prop_name)
                ws_values = {}
                for ws_id, ws_handle in all_ws.items():
                    text = ITsString(prop_obj.get_String(ws_handle)).Text
                    if text:  # Only include non-empty values
                        ws_values[ws_id] = text
                if ws_values:  # Only include property if it has values
                    props[prop_name] = ws_values

        # Integer properties
        if hasattr(rule, 'Direction'):
            props['Direction'] = rule.Direction

        # Reference Atomic (RA) properties - return GUID as string
        if hasattr(rule, 'StratumRA') and rule.StratumRA:
            props['StratumGuid'] = str(rule.StratumRA.Guid)

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two phonological rules and return detailed differences.

        Args:
            item1: First rule to compare (from source project).
            item2: Second rule to compare (from target project).
            ops1: Optional PhonologicalRuleOperations instance for item1's project.
                 Defaults to self.
            ops2: Optional PhonologicalRuleOperations instance for item2's project.
                 Defaults to self.

        Returns:
            tuple: (is_different, differences) where:
                - is_different (bool): True if items differ
                - differences (dict): Maps property names to (value1, value2) tuples

        Example:
            >>> rule1 = project1_phonRuleOps.Find("Voicing Assimilation")
            >>> rule2 = project2_phonRuleOps.Find("Voicing Assimilation")
            >>> is_diff, diffs = project1_phonRuleOps.CompareTo(
            ...     rule1, rule2,
            ...     ops1=project1_phonRuleOps,
            ...     ops2=project2_phonRuleOps
            ... )
            >>> if is_diff:
            ...     for prop, (val1, val2) in diffs.items():
            ...         print(f"{prop}: {val1} -> {val2}")

        Notes:
            - Compares all MultiString properties across all writing systems
            - Compares integer and reference properties
            - Returns empty dict if items are identical
            - Handles cross-project comparison via ops1/ops2
        """
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        # Get syncable properties from both items
        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        is_different = False
        differences = {}

        # Compare each property
        all_keys = set(props1.keys()) | set(props2.keys())
        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)

            if val1 != val2:
                is_different = True
                differences[key] = (val1, val2)

        return (is_different, differences)

    # --- Private Helper Methods ---

    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)
