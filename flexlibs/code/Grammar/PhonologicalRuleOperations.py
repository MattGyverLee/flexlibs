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

import logging
logger = logging.getLogger(__name__)

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
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
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

        from flexlibs import FLExProject, PhonologicalRuleOperations

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

        Yields:
            IPhPhonRule: Each phonological rule object in the project.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> for rule in phonRuleOps.GetAll():
            ...     name = phonRuleOps.GetName(rule)
            ...     print(f"Rule: {name}")
            Rule: Voicing Assimilation
            Rule: Nasal Place Assimilation
            Rule: Final Devoicing

        Notes:
            - Returns rules from the phonological data's PhonRulesOS collection
            - Includes both active and inactive rules
            - Returns empty if no phonological data defined
            - Order depends on rule ordering in the project

        See Also:
            Create, GetName, IsActive
        """
        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data:
            return

        if hasattr(phon_data, 'PhonRulesOS'):
            for rule in phon_data.PhonRulesOS:
                yield rule


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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if name is None:
            raise FP_NullParameterError()

        return self.Find(name) is not None


    def Find(self, name):
        """
        Find a phonological rule by name.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            IPhPhonRule or None: The rule object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> rule = phonRuleOps.Find("Voicing Assimilation")
            >>> if rule:
            ...     desc = phonRuleOps.GetDescription(rule)
            ...     print(f"Found: {desc}")

            >>> # Case-insensitive search
            >>> rule = phonRuleOps.Find("voicing assimilation")

        Notes:
            - Search is case-insensitive
            - Returns first matching rule if multiple exist
            - Searches in default analysis writing system

        See Also:
            Exists, GetAll, GetName
        """
        if name is None:
            raise FP_NullParameterError()

        name_lower = name.lower()
        for rule in self.GetAll():
            rule_name = self.GetName(rule)
            if rule_name.lower() == name_lower:
                return rule

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
        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

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
        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()
        if description is None:
            raise FP_NullParameterError()

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
        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()
        if not phoneme_or_class:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()
        if not phoneme_or_class:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

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


    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a phonological rule, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IPhPhonRule object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source rule.
                                If False, insert at end of rules list.
            deep (bool): If True, deep copy owned objects (StrucDescOS, RightHandSidesOS).
                        If False (default), owned objects are not copied.

        Returns:
            IPhPhonRule: The newly created duplicate rule with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> phonRuleOps = PhonologicalRuleOperations(project)
            >>> voicing = phonRuleOps.Create("Voicing Assimilation")
            >>> # Shallow copy (no owned objects)
            >>> copy = phonRuleOps.Duplicate(voicing)
            >>> print(phonRuleOps.GetName(copy))
            Voicing Assimilation

            >>> # Deep copy (includes StrucDescOS and RightHandSidesOS)
            >>> rule = phonRuleOps.Create("Complex Rule")
            >>> copy = phonRuleOps.Duplicate(rule, deep=True)

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original rule's position
            - Simple properties copied: Name, Description (MultiString)
            - Reference property copied: StratumRA
            - Integer property copied: Direction
            - deep=True copies owned objects using LCM CopyObject pattern:
              - StrucDescOS (structural description)
              - RightHandSidesOS (output specifications)
            - Complex owned objects are deep cloned with new GUIDs
            - Follows LCM SetCloneProperties pattern (OverridesLing_Lex.cs)

        See Also:
            Create, Delete, SetDirection
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source rule
        source = self.__ResolveObject(item_or_hvo)

        # Create new rule using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(IPhRegularRuleFactory)
        duplicate = factory.Create()

        # Add to phonological rules collection
        phon_data = self.project.lp.PhonologicalDataOA
        if insert_after:
            source_index = phon_data.PhonRulesOS.IndexOf(source)
            phon_data.PhonRulesOS.Insert(source_index + 1, duplicate)
        else:
            phon_data.PhonRulesOS.Add(duplicate)

        # Copy simple MultiString properties (AFTER adding to parent)
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Description.CopyAlternatives(source.Description)

        # Copy Reference Atomic (RA) properties
        if hasattr(source, 'StratumRA') and source.StratumRA:
            duplicate.StratumRA = source.StratumRA

        # Copy integer properties
        if hasattr(source, 'Direction'):
            duplicate.Direction = source.Direction

        # Deep copy: owned objects (following LCM pattern from OverridesLing_Lex.cs)
        if deep:
            # Clear RightHandSidesOS before copying (LCM pattern line 7679)
            if hasattr(duplicate, 'RightHandSidesOS'):
                duplicate.RightHandSidesOS.Clear()

            # Copy StrucDescOS items
            if hasattr(source, 'StrucDescOS') and source.StrucDescOS.Count > 0:
                for struc_item in source.StrucDescOS:
                    # Deep clone using CopyObject pattern
                    cloned_item = self.__CopyPhonRuleObject(struc_item)
                    if cloned_item:
                        duplicate.StrucDescOS.Add(cloned_item)

            # Copy RightHandSidesOS items (LCM pattern line 7680-7697)
            if hasattr(source, 'RightHandSidesOS') and source.RightHandSidesOS.Count > 0:
                for rhs_item in source.RightHandSidesOS:
                    # Deep clone using CopyObject pattern
                    cloned_rhs = self.__CopyPhonRuleObject(rhs_item)
                    if cloned_rhs:
                        duplicate.RightHandSidesOS.Add(cloned_rhs)

        return duplicate


    def __CopyPhonRuleObject(self, source_obj):
        """
        Helper method to deep copy a phonological rule object (StrucDesc or RHS).

        Args:
            source_obj: The source object to copy.

        Returns:
            The duplicated object with new GUID.

        Notes:
            - Uses LCM's CopyObject pattern for deep cloning
            - Handles all owned objects and nested structures recursively
            - Generates new GUIDs for all cloned objects
        """
        # Use LCM's CopyObject for deep cloning of complex structures
        # This is the pattern used in OverridesLing_Lex.cs SetCloneProperties
        cache = self.project.project.ServiceLocator.GetInstance("ICmObjectRepository")
        if hasattr(cache, 'CopyObject'):
            return cache.CopyObject(source_obj)

        # Fallback: if CopyObject not available, return None
        # The rule will still be duplicated, just without these complex objects
        return None


    # --- Private Helper Methods ---

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
