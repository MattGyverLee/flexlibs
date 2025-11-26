#
#   MorphRuleOperations.py
#
#   Class: MorphRuleOperations
#          Morphological rule operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

# Import FLEx LCM types
# Note: Morph rule interfaces may not exist in current LCM API version
# from SIL.LCModel import (
#     IMoMorphRule,  # May not exist
#     IMoAffixProcessFactory,
#     IMoStratumFactory,
# )
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class MorphRuleOperations:
    """
    This class provides operations for managing morphological rules in a
    FieldWorks project.

    Morphological rules define systematic patterns of word formation, including
    affixation processes, templates, and other morphological transformations
    used in the language.

    Usage::

        from flexlibs import FLExProject, MorphRuleOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        ruleOps = MorphRuleOperations(project)

        # Get all morphological rules
        for rule in ruleOps.GetAll():
            name = ruleOps.GetName(rule)
            description = ruleOps.GetDescription(rule)
            active = ruleOps.IsActive(rule)
            print(f"{name}: {description} (active={active})")

        # Create a new rule
        rule = ruleOps.Create("Plural Formation", "Adds plural suffix")
        ruleOps.SetActive(rule, True)

        # Update rule
        ruleOps.SetDescription(rule, "Forms plural nouns by adding -s")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize MorphRuleOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self):
        """
        Get all morphological rules in the project.

        Yields:
            IMoMorphRule: Each morphological rule object in the project.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> for rule in ruleOps.GetAll():
            ...     name = ruleOps.GetName(rule)
            ...     active = ruleOps.IsActive(rule)
            ...     status = "active" if active else "inactive"
            ...     print(f"{name} ({status})")
            Plural Formation (active)
            Past Tense (active)
            Verb Template (inactive)

        Notes:
            - Returns rules from all rule collections (affixation, templates, etc.)
            - Includes both active and inactive rules
            - Returns empty if no morphological data defined
            - Order depends on the order in each collection

        See Also:
            Create, GetName, IsActive
        """
        morph_data = self.project.lp.MorphologicalDataOA
        if not morph_data:
            return

        # Get affixation rules
        if hasattr(morph_data, 'AffixRulesOS'):
            for rule in morph_data.AffixRulesOS:
                yield rule

        # Get template rules
        if hasattr(morph_data, 'TemplatesOS'):
            for rule in morph_data.TemplatesOS:
                yield rule


    def Create(self, name, description=None):
        """
        Create a new morphological rule.

        Args:
            name (str): The name of the rule (e.g., "Plural Formation").
            description (str, optional): Optional description of what this rule
                does. Defaults to None.

        Returns:
            IMoMorphRule: The newly created rule object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> plural = ruleOps.Create("Plural Formation", "Adds -s suffix")
            >>> print(ruleOps.GetName(plural))
            Plural Formation

            >>> past = ruleOps.Create("Past Tense")
            >>> ruleOps.SetDescription(past, "Forms past tense verbs")
            >>> ruleOps.SetActive(past, True)

        Notes:
            - Name should be descriptive of the morphological process
            - Description is optional but helpful for documentation
            - Rule is created in the default analysis writing system
            - New rules are added to the AffixRulesOS collection
            - Rules start as inactive by default

        See Also:
            Delete, GetName, SetDescription, SetActive
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new rule using the factory
        factory = self.project.project.ServiceLocator.GetService(IMoAffixProcessFactory)
        new_rule = factory.Create()

        # Add to the morphological rules collection (must be done before setting properties)
        morph_data = self.project.lp.MorphologicalDataOA
        morph_data.AffixRulesOS.Add(new_rule)

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
        Delete a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> obsolete = ruleOps.Create("Obsolete Rule")
            >>> # ... realize it's not needed
            >>> ruleOps.Delete(obsolete)

        Warning:
            - Deleting a rule that is in use may cause errors
            - This includes rules referenced by:
              - Morphological processes
              - Allomorph conditions
              - Other rule definitions
            - Deletion is permanent and cannot be undone
            - Consider deactivating instead of deleting

        See Also:
            Create, SetActive, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

        # Resolve to rule object
        rule = self.__ResolveObject(rule_or_hvo)

        # Remove from the appropriate collection
        morph_data = self.project.lp.MorphologicalDataOA

        # Try removing from affixation rules
        if hasattr(morph_data, 'AffixRulesOS') and rule in morph_data.AffixRulesOS:
            morph_data.AffixRulesOS.Remove(rule)
        # Try removing from template rules
        elif hasattr(morph_data, 'TemplatesOS') and rule in morph_data.TemplatesOS:
            morph_data.TemplatesOS.Remove(rule)


    def GetName(self, rule_or_hvo, wsHandle=None):
        """
        Get the name of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The rule name, or empty string if not set.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> for rule in ruleOps.GetAll():
            ...     name = ruleOps.GetName(rule)
            ...     print(name)
            Plural Formation
            Past Tense
            Progressive Aspect

            >>> # Get name in a specific writing system
            >>> rule = list(ruleOps.GetAll())[0]
            >>> name = ruleOps.GetName(rule, project.WSHandle('en'))

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
        Set the name of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> rule = list(ruleOps.GetAll())[0]
            >>> ruleOps.SetName(rule, "Noun Pluralization")

            >>> # Use descriptive names
            >>> ruleOps.SetName(rule, "Plural Formation (Regular Nouns)")

        Notes:
            - Use clear, descriptive names
            - Names should indicate the morphological process
            - Consider including the grammatical category affected

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
        Get the description of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The rule description, or empty string if not set.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> for rule in ruleOps.GetAll():
            ...     name = ruleOps.GetName(rule)
            ...     desc = ruleOps.GetDescription(rule)
            ...     print(f"{name}: {desc}")
            Plural Formation: Adds -s suffix to form plural nouns
            Past Tense: Adds -ed suffix to form past tense verbs

            >>> # Get description in a specific writing system
            >>> rule = list(ruleOps.GetAll())[0]
            >>> desc = ruleOps.GetDescription(rule, project.WSHandle('en'))

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
        Set the description of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            description (str): The new description.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or description is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> rule = list(ruleOps.GetAll())[0]
            >>> ruleOps.SetDescription(rule, "Adds -s suffix to form plural nouns")

            >>> # Provide detailed descriptions
            >>> desc = "Forms past tense by adding -ed to regular verb stems"
            >>> ruleOps.SetDescription(rule, desc)

        Notes:
            - Descriptions can be empty string (but not None)
            - Use descriptions to document the morphological process
            - Include information about the grammatical context
            - Consider mentioning exceptions or special cases

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
        Get the stratum of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.

        Returns:
            IMoStratum or None: The stratum object if set, None otherwise.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> rule = list(ruleOps.GetAll())[0]
            >>> stratum = ruleOps.GetStratum(rule)
            >>> if stratum:
            ...     print(f"Rule uses stratum: {stratum.Name.BestAnalysisAlternative.Text}")

        Notes:
            - Strata define ordering levels for morphological rules
            - Rules in lower strata apply before rules in higher strata
            - Returns None if no stratum is assigned
            - Stratum assignment is optional

        See Also:
            SetStratum, GetName
        """
        if not rule_or_hvo:
            raise FP_NullParameterError()

        rule = self.__ResolveObject(rule_or_hvo)

        # Check if rule has stratum reference
        if hasattr(rule, 'StratumRA') and rule.StratumRA:
            return rule.StratumRA

        return None


    def SetStratum(self, rule_or_hvo, stratum):
        """
        Set the stratum of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            stratum: The IMoStratum object, HVO, or None to clear.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> rule = list(ruleOps.GetAll())[0]

            >>> # Create or get a stratum
            >>> morph_data = project.lp.MorphologicalDataOA
            >>> if morph_data.StrataOS.Count > 0:
            ...     stratum = morph_data.StrataOS[0]
            ...     ruleOps.SetStratum(rule, stratum)

            >>> # Clear stratum assignment
            >>> ruleOps.SetStratum(rule, None)

        Notes:
            - Strata control the order of rule application
            - Pass None to remove stratum assignment
            - Stratum must exist in the project's morphological data
            - Rules without strata may apply in undefined order

        See Also:
            GetStratum, SetActive
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()

        rule = self.__ResolveObject(rule_or_hvo)

        # Set or clear stratum
        if hasattr(rule, 'StratumRA'):
            if stratum is None:
                rule.StratumRA = None
            else:
                # Resolve stratum if it's an HVO
                if isinstance(stratum, int):
                    stratum = self.project.Object(stratum)
                rule.StratumRA = stratum


    def IsActive(self, rule_or_hvo):
        """
        Check if a morphological rule is active.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.

        Returns:
            bool: True if the rule is active, False otherwise.

        Raises:
            FP_NullParameterError: If rule_or_hvo is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> for rule in ruleOps.GetAll():
            ...     name = ruleOps.GetName(rule)
            ...     active = ruleOps.IsActive(rule)
            ...     status = "active" if active else "inactive"
            ...     print(f"{name}: {status}")
            Plural Formation: active
            Obsolete Rule: inactive

            >>> # Check before applying rule
            >>> rule = list(ruleOps.GetAll())[0]
            >>> if ruleOps.IsActive(rule):
            ...     print(f"{ruleOps.GetName(rule)} will be applied")

        Notes:
            - Only active rules are applied during morphological analysis
            - Inactive rules are retained but not used
            - Use SetActive() to enable/disable rules
            - Returns False if the rule doesn't have an Active property

        See Also:
            SetActive, GetAll
        """
        if not rule_or_hvo:
            raise FP_NullParameterError()

        rule = self.__ResolveObject(rule_or_hvo)

        # Check if rule has Active property
        if hasattr(rule, 'Active'):
            return rule.Active

        return False


    def SetActive(self, rule_or_hvo, active):
        """
        Set the active state of a morphological rule.

        Args:
            rule_or_hvo: The IMoMorphRule object or HVO.
            active (bool): True to activate the rule, False to deactivate.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If rule_or_hvo or active is None.

        Example:
            >>> ruleOps = MorphRuleOperations(project)
            >>> rule = list(ruleOps.GetAll())[0]

            >>> # Activate a rule
            >>> ruleOps.SetActive(rule, True)
            >>> print(f"Active: {ruleOps.IsActive(rule)}")
            Active: True

            >>> # Deactivate obsolete rules
            >>> for rule in ruleOps.GetAll():
            ...     name = ruleOps.GetName(rule)
            ...     if "obsolete" in name.lower():
            ...         ruleOps.SetActive(rule, False)

        Notes:
            - Active rules are used during morphological analysis
            - Inactive rules are retained in the project but not applied
            - Deactivating is safer than deleting (can be reactivated)
            - Use to temporarily disable rules for testing

        See Also:
            IsActive, Delete, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not rule_or_hvo:
            raise FP_NullParameterError()
        if active is None:
            raise FP_NullParameterError()

        rule = self.__ResolveObject(rule_or_hvo)

        # Set active state
        if hasattr(rule, 'Active'):
            rule.Active = bool(active)


    # --- Private Helper Methods ---

    def __ResolveObject(self, rule_or_hvo):
        """
        Resolve HVO or object to IMoMorphRule.

        Args:
            rule_or_hvo: Either an IMoMorphRule object or an HVO (int).

        Returns:
            IMoMorphRule: The resolved rule object.
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
