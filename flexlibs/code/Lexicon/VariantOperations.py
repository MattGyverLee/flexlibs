#
#   VariantOperations.py
#
#   Class: VariantOperations
#          Variant form operations for FieldWorks Language Explorer
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
from SIL.LCModel import (
    ILexEntry,
    ILexEntryRef,
    ILexEntryRefFactory,
    ILexEntryType,
    ILexEntryTypeRepository,
    IVariantComponentLexeme,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class VariantOperations:
    """
    This class provides operations for managing variant forms in a FieldWorks project.

    Variant forms represent alternative forms of lexical entries, including:
    - Spelling variants (e.g., "color" vs. "colour")
    - Dialectal variants (e.g., regional pronunciations)
    - Irregularly inflected forms (e.g., "went" as past tense of "go")
    - Free variants (e.g., "among" vs. "amongst")

    Variants are linked through ILexEntryRef objects which can connect entries
    as variants of each other or as components of complex forms.

    This class should be accessed via FLExProject.Variants property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all variant types
        for vtype in project.Variants.GetAllTypes():
            name = project.Variants.GetTypeName(vtype)
            print(f"Variant type: {name}")

        # Find a specific variant type
        spelling_type = project.Variants.FindType("Spelling Variant")

        # Create a variant
        entry = project.LexEntry.Find("color")
        variant = project.Variants.Create(entry, "colour", spelling_type)

        # Get all variants for an entry
        for var in project.Variants.GetAll(entry):
            form = project.Variants.GetForm(var)
            vtype = project.Variants.GetType(var)
            print(f"Variant: {form} ({vtype})")

        # For irregularly inflected forms
        go_entry = project.LexEntry.Find("go")
        went_entry = project.LexEntry.Find("went")
        irregular_type = project.Variants.FindType("Irregularly Inflected Form")

        # Create variant with component
        variant_ref = project.Variants.Create(went_entry, "went", irregular_type)
        project.Variants.AddComponentLexeme(variant_ref, go_entry)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize VariantOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Variant Type Management ---

    def GetAllTypes(self):
        """
        Get all variant entry types defined in the project.

        Variant types define the nature of the relationship between entries,
        such as spelling variants, dialectal variants, irregularly inflected
        forms, etc.

        Yields:
            ILexEntryType: Each variant type defined in the project.

        Example:
            >>> for vtype in project.Variants.GetAllTypes():
            ...     name = project.Variants.GetTypeName(vtype)
            ...     desc = project.Variants.GetTypeDescription(vtype)
            ...     print(f"{name}: {desc}")
            Spelling Variant: A variant spelling of the same word
            Dialectal Variant: A form used in a particular dialect
            Irregularly Inflected Form: An irregular inflection of a lexeme

        Notes:
            - Returns both built-in and custom variant types
            - Types are hierarchical - may include subtypes
            - Empty if no variant types are defined (unusual)
            - Types control how variants are displayed and linked

        See Also:
            FindType, GetTypeName, GetTypeDescription
        """
        if not self.project.lp.LexDbOA.VariantEntryTypesOA:
            return

        for vtype in self.project.lp.LexDbOA.VariantEntryTypesOA.PossibilitiesOS:
            yield vtype
            # Also yield any subtypes
            if vtype.SubPossibilitiesOS.Count > 0:
                for subtype in vtype.SubPossibilitiesOS:
                    yield subtype


    def FindType(self, name):
        """
        Find a variant type by name.

        Args:
            name (str): The name of the variant type to find (case-insensitive).
                Common types: "Spelling Variant", "Dialectal Variant",
                "Irregularly Inflected Form", "Free Variant", etc.

        Returns:
            ILexEntryType or None: The variant type if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> spelling_type = project.Variants.FindType("Spelling Variant")
            >>> if spelling_type:
            ...     print(f"Found: {project.Variants.GetTypeName(spelling_type)}")
            Found: Spelling Variant

            >>> # Case-insensitive search
            >>> dialectal = project.Variants.FindType("dialectal variant")
            >>> irregular = project.Variants.FindType("Irregularly Inflected Form")

        Notes:
            - Search is case-insensitive
            - Returns first match found
            - Searches both types and subtypes
            - Returns None if not found (doesn't raise exception)
            - Common built-in types:
              - Spelling Variant
              - Dialectal Variant
              - Free Variant
              - Irregularly Inflected Form

        See Also:
            GetAllTypes, GetTypeName
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_lower = name.lower()
        wsHandle = self.project.project.DefaultAnalWs

        for vtype in self.GetAllTypes():
            type_name = ITsString(vtype.Name.get_String(wsHandle)).Text
            if type_name and type_name.lower() == name_lower:
                return vtype

        return None


    def GetTypeName(self, variant_type, wsHandle=None):
        """
        Get the name of a variant type.

        Args:
            variant_type: The ILexEntryType object.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The variant type name (empty string if not set).

        Raises:
            FP_NullParameterError: If variant_type is None.

        Example:
            >>> for vtype in project.Variants.GetAllTypes():
            ...     name = project.Variants.GetTypeName(vtype)
            ...     print(f"Type: {name}")
            Type: Spelling Variant
            Type: Dialectal Variant
            Type: Irregularly Inflected Form

            >>> # Get in specific writing system
            >>> name_fr = project.Variants.GetTypeName(vtype, project.WSHandle('fr'))

        Notes:
            - Returns empty string if name not set in specified writing system
            - Variant types are typically defined in analysis writing systems
            - Type names are localizable (can differ per writing system)

        See Also:
            GetTypeDescription, FindType
        """
        if not variant_type:
            raise FP_NullParameterError()

        wsHandle = self.__WSHandleAnalysis(wsHandle)

        name = ITsString(variant_type.Name.get_String(wsHandle)).Text
        return name or ""


    def GetTypeDescription(self, variant_type, wsHandle=None):
        """
        Get the description of a variant type.

        Args:
            variant_type: The ILexEntryType object.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The variant type description (empty string if not set).

        Raises:
            FP_NullParameterError: If variant_type is None.

        Example:
            >>> spelling_type = project.Variants.FindType("Spelling Variant")
            >>> if spelling_type:
            ...     desc = project.Variants.GetTypeDescription(spelling_type)
            ...     print(desc)
            A variant spelling of the same word

        Notes:
            - Returns empty string if description not set
            - Description is a MultiString field (can vary by writing system)
            - Not all variant types have descriptions
            - Useful for documenting custom variant types

        See Also:
            GetTypeName, FindType
        """
        if not variant_type:
            raise FP_NullParameterError()

        wsHandle = self.__WSHandleAnalysis(wsHandle)

        desc = ITsString(variant_type.Description.get_String(wsHandle)).Text
        return desc or ""


    # --- Variant Management ---

    def GetAll(self, entry_or_hvo):
        """
        Get all variant references for a lexical entry.

        This returns the entry references that define this entry as a variant
        of other entries, or other entries as variants of this one.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.

        Yields:
            ILexEntryRef: Each variant reference associated with the entry.

        Raises:
            FP_NullParameterError: If entry_or_hvo is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant_ref in project.Variants.GetAll(entry):
            ...     vtype = project.Variants.GetType(variant_ref)
            ...     type_name = project.Variants.GetTypeName(vtype)
            ...     print(f"Variant type: {type_name}")
            Variant type: Spelling Variant

        Notes:
            - Returns empty generator if entry has no variants
            - Each ILexEntryRef represents one variant relationship
            - For complex entries, may return multiple references
            - Variant references are bidirectional in some cases

        See Also:
            Create, GetVariantCount, GetType
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__GetEntryObject(entry_or_hvo)

        for entry_ref in entry.EntryRefsOS:
            # Check if this is a variant type reference
            if entry_ref.RefType == 0:  # Variant type
                yield entry_ref


    def Create(self, entry_or_hvo, variant_form, variant_type, wsHandle=None):
        """
        Create a variant relationship for an entry.

        This creates an ILexEntryRef object that defines the entry as a variant
        of another form. The variant_form can be set as the lexeme form of the
        entry itself, or you can create a separate entry for the variant.

        Args:
            entry_or_hvo: The ILexEntry object or HVO (the variant entry).
            variant_form (str): The variant form text (for display/reference).
            variant_type: The ILexEntryType object defining the variant type.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ILexEntryRef: The newly created variant reference object.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo, variant_form, or variant_type is None.
            FP_ParameterError: If variant_form is empty.

        Example:
            >>> # Create spelling variant
            >>> colour_entry = project.LexEntry.Find("colour")
            >>> if not colour_entry:
            ...     colour_entry = project.LexEntry.Create("colour")
            >>> spelling_type = project.Variants.FindType("Spelling Variant")
            >>> variant = project.Variants.Create(colour_entry, "colour", spelling_type)

            >>> # Create irregularly inflected form
            >>> went_entry = project.LexEntry.Find("went")
            >>> irregular_type = project.Variants.FindType("Irregularly Inflected Form")
            >>> variant_ref = project.Variants.Create(went_entry, "went", irregular_type)
            >>> # Then add the base form as a component
            >>> go_entry = project.LexEntry.Find("go")
            >>> project.Variants.AddComponentLexeme(variant_ref, go_entry)

        Notes:
            - Creates an ILexEntryRef with RefType = 0 (Variant)
            - The variant_type determines how the variant is classified
            - For irregularly inflected forms, add ComponentLexemes afterward
            - The variant_form is typically the same as the entry's lexeme form
            - Multiple variant references can exist for one entry

        See Also:
            Delete, GetType, SetType, AddComponentLexeme
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if variant_form is None:
            raise FP_NullParameterError()
        if variant_type is None:
            raise FP_NullParameterError()

        if not variant_form or not variant_form.strip():
            raise FP_ParameterError("Variant form cannot be empty")

        entry = self.__GetEntryObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the entry reference
        factory = self.project.project.ServiceLocator.GetInstance(ILexEntryRefFactory)
        entry_ref = factory.Create()

        # Set as variant type (RefType = 0)
        entry_ref.RefType = 0

        # Set the variant type
        entry_ref.VariantEntryTypesRS.Add(variant_type)

        # Note: The variant form itself is typically the entry's lexeme form
        # We don't set a separate form on the ILexEntryRef
        # The variant_form parameter is for consistency with the API and
        # for cases where the entry's lexeme form needs to be set

        # Ensure the entry's lexeme form matches
        if entry.LexemeFormOA:
            current_form = ITsString(entry.LexemeFormOA.Form.get_String(wsHandle)).Text
            if not current_form or current_form != variant_form:
                mkstr = TsStringUtils.MakeString(variant_form, wsHandle)
                entry.LexemeFormOA.Form.set_String(wsHandle, mkstr)

        # Add to entry
        entry.EntryRefsOS.Add(entry_ref)

        return entry_ref


    def Delete(self, variant_or_hvo):
        """
        Delete a variant reference.

        This removes the variant relationship but does not delete the entry itself.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If variant_or_hvo is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant in project.Variants.GetAll(entry):
            ...     # Delete the variant reference
            ...     project.Variants.Delete(variant)

        Warning:
            - Deletes the variant relationship, not the entry
            - To delete the variant entry itself, use project.LexEntry.Delete()
            - Deletion is permanent and cannot be undone
            - Component lexeme links are also removed

        Notes:
            - Removes the ILexEntryRef from the entry's EntryRefsOS collection
            - The owning entry remains unchanged
            - Any component lexemes are automatically dereferenced

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not variant_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)

        # Get the owning entry
        owner = variant.Owner

        # Remove from entry's EntryRefsOS
        if hasattr(owner, 'EntryRefsOS'):
            owner.EntryRefsOS.Remove(variant)


    def GetForm(self, variant_or_hvo, wsHandle=None):
        """
        Get the form of a variant.

        This returns the lexeme form of the entry that owns this variant reference.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The variant form text (empty string if not set).

        Raises:
            FP_NullParameterError: If variant_or_hvo is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant in project.Variants.GetAll(entry):
            ...     form = project.Variants.GetForm(variant)
            ...     print(f"Variant form: {form}")
            Variant form: colour

        Notes:
            - Returns the owning entry's lexeme form
            - Returns empty string if entry has no lexeme form
            - ILexEntryRef doesn't store form directly - it's on the entry
            - For component lexemes, use GetComponentLexemes()

        See Also:
            SetForm, GetOwningEntry
        """
        if not variant_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Get the owning entry
        owner = variant.Owner

        # Get the lexeme form from the entry
        if hasattr(owner, 'LexemeFormOA') and owner.LexemeFormOA:
            form = ITsString(owner.LexemeFormOA.Form.get_String(wsHandle)).Text
            return form or ""

        return ""


    def SetForm(self, variant_or_hvo, text, wsHandle=None):
        """
        Set the form of a variant.

        This sets the lexeme form of the entry that owns this variant reference.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.
            text (str): The new variant form text.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If variant_or_hvo or text is None.
            FP_ParameterError: If text is empty or entry has no lexeme form.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant in project.Variants.GetAll(entry):
            ...     project.Variants.SetForm(variant, "coulour")  # Fix typo
            ...     print(project.Variants.GetForm(variant))
            coulour

        Notes:
            - Sets the owning entry's lexeme form
            - Entry must have a lexeme form object
            - Changes the headword of the variant entry
            - Affects how the entry appears in the lexicon

        See Also:
            GetForm, GetOwningEntry
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not variant_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        if not text or not text.strip():
            raise FP_ParameterError("Variant form cannot be empty")

        variant = self.__GetVariantObject(variant_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Get the owning entry
        owner = variant.Owner

        if not hasattr(owner, 'LexemeFormOA') or not owner.LexemeFormOA:
            raise FP_ParameterError("Entry has no lexeme form object")

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        owner.LexemeFormOA.Form.set_String(wsHandle, mkstr)


    def GetType(self, variant_or_hvo):
        """
        Get the variant type of a variant reference.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.

        Returns:
            ILexEntryType or None: The variant type, or None if not set.

        Raises:
            FP_NullParameterError: If variant_or_hvo is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant in project.Variants.GetAll(entry):
            ...     vtype = project.Variants.GetType(variant)
            ...     if vtype:
            ...         name = project.Variants.GetTypeName(vtype)
            ...         print(f"Variant type: {name}")
            Variant type: Spelling Variant

        Notes:
            - Returns None if no variant type is set (unusual)
            - A variant reference can have multiple types, this returns the first
            - Use VariantEntryTypesRS collection for all types
            - Variant type determines how the variant is classified

        See Also:
            SetType, GetTypeName, GetAllTypes
        """
        if not variant_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)

        if variant.VariantEntryTypesRS.Count > 0:
            return variant.VariantEntryTypesRS[0]

        return None


    def SetType(self, variant_or_hvo, variant_type):
        """
        Set the variant type of a variant reference.

        This replaces all existing variant types with the specified type.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.
            variant_type: The ILexEntryType object to set.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If variant_or_hvo or variant_type is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> for variant in project.Variants.GetAll(entry):
            ...     dialectal_type = project.Variants.FindType("Dialectal Variant")
            ...     if dialectal_type:
            ...         project.Variants.SetType(variant, dialectal_type)
            ...         vtype = project.Variants.GetType(variant)
            ...         print(project.Variants.GetTypeName(vtype))
            Dialectal Variant

        Notes:
            - Clears all existing variant types
            - Sets the new type as the only type
            - To add additional types, use VariantEntryTypesRS.Add()
            - Changing type affects how variant is displayed and processed

        See Also:
            GetType, FindType, GetAllTypes
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not variant_or_hvo:
            raise FP_NullParameterError()
        if variant_type is None:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)

        # Clear existing types
        variant.VariantEntryTypesRS.Clear()

        # Add the new type
        variant.VariantEntryTypesRS.Add(variant_type)


    # --- Component Management (for irregularly inflected forms) ---

    def GetComponentLexemes(self, variant_or_hvo):
        """
        Get the component lexemes of a variant.

        Component lexemes are the base entries that make up an irregularly
        inflected form. For example, "went" has "go" as a component.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.

        Returns:
            list: List of ILexEntry objects that are components (empty list if none).

        Raises:
            FP_NullParameterError: If variant_or_hvo is None.

        Example:
            >>> # "went" is irregular past tense of "go"
            >>> went_entry = project.LexEntry.Find("went")
            >>> for variant in project.Variants.GetAll(went_entry):
            ...     components = project.Variants.GetComponentLexemes(variant)
            ...     for comp in components:
            ...         headword = project.LexEntry.GetHeadword(comp)
            ...         print(f"Component: {headword}")
            Component: go

            >>> # "worse" might have components "bad" or "ill"
            >>> worse_entry = project.LexEntry.Find("worse")
            >>> for variant in project.Variants.GetAll(worse_entry):
            ...     for comp in project.Variants.GetComponentLexemes(variant):
            ...         print(project.LexEntry.GetHeadword(comp))
            bad

        Notes:
            - Returns empty list if no components
            - Primarily used for "Irregularly Inflected Form" variant type
            - Can have multiple components (rare but possible)
            - Components are ILexEntry objects (not ILexEntryRef)
            - Access via ComponentLexemesRS collection

        See Also:
            AddComponentLexeme, RemoveComponentLexeme, Create
        """
        if not variant_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)

        components = []
        for comp_lex in variant.ComponentLexemesRS:
            components.append(comp_lex)

        return components


    def AddComponentLexeme(self, variant_or_hvo, entry_or_hvo):
        """
        Add a component lexeme to a variant.

        This creates a link from an irregularly inflected form to its base entry.
        For example, linking "went" to "go".

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.
            entry_or_hvo: The ILexEntry object or HVO to add as a component.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If variant_or_hvo or entry_or_hvo is None.

        Example:
            >>> # Create "went" as irregular past of "go"
            >>> went_entry = project.LexEntry.Find("went")
            >>> go_entry = project.LexEntry.Find("go")
            >>>
            >>> irregular_type = project.Variants.FindType("Irregularly Inflected Form")
            >>> variant_ref = project.Variants.Create(went_entry, "went", irregular_type)
            >>>
            >>> # Add "go" as the component
            >>> project.Variants.AddComponentLexeme(variant_ref, go_entry)
            >>>
            >>> # Verify
            >>> components = project.Variants.GetComponentLexemes(variant_ref)
            >>> for comp in components:
            ...     print(project.LexEntry.GetHeadword(comp))
            go

        Notes:
            - Typically used with "Irregularly Inflected Form" variant type
            - Creates a reference from the variant to the base form
            - Multiple components can be added (e.g., for suppletion)
            - The component entry must already exist
            - Adds to ComponentLexemesRS collection

        See Also:
            GetComponentLexemes, RemoveComponentLexeme, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not variant_or_hvo:
            raise FP_NullParameterError()
        if not entry_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)
        entry = self.__GetEntryObject(entry_or_hvo)

        # Add the entry as a component
        variant.ComponentLexemesRS.Add(entry)


    def RemoveComponentLexeme(self, variant_or_hvo, entry_or_hvo):
        """
        Remove a component lexeme from a variant.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.
            entry_or_hvo: The ILexEntry object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If variant_or_hvo or entry_or_hvo is None.

        Example:
            >>> went_entry = project.LexEntry.Find("went")
            >>> go_entry = project.LexEntry.Find("go")
            >>>
            >>> for variant in project.Variants.GetAll(went_entry):
            ...     # Remove "go" as component
            ...     project.Variants.RemoveComponentLexeme(variant, go_entry)
            ...
            ...     # Verify removal
            ...     components = project.Variants.GetComponentLexemes(variant)
            ...     print(f"Remaining components: {len(components)}")
            Remaining components: 0

        Notes:
            - If entry not in component list, this is a no-op (no error)
            - Removes from ComponentLexemesRS collection
            - Doesn't delete the component entry itself
            - Doesn't affect the variant reference (only the component link)

        See Also:
            GetComponentLexemes, AddComponentLexeme
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not variant_or_hvo:
            raise FP_NullParameterError()
        if not entry_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)
        entry = self.__GetEntryObject(entry_or_hvo)

        # Remove if present
        if entry in variant.ComponentLexemesRS:
            variant.ComponentLexemesRS.Remove(entry)


    # --- Utilities ---

    def GetOwningEntry(self, variant_or_hvo):
        """
        Get the entry that owns a variant reference.

        Args:
            variant_or_hvo: The ILexEntryRef object or HVO.

        Returns:
            ILexEntry: The entry that owns this variant reference.

        Raises:
            FP_NullParameterError: If variant_or_hvo is None.

        Example:
            >>> # Find all variants in the lexicon and their owners
            >>> for entry in project.LexEntry.GetAll():
            ...     for variant in project.Variants.GetAll(entry):
            ...         owner = project.Variants.GetOwningEntry(variant)
            ...         owner_hw = project.LexEntry.GetHeadword(owner)
            ...         var_form = project.Variants.GetForm(variant)
            ...         vtype = project.Variants.GetType(variant)
            ...         type_name = project.Variants.GetTypeName(vtype) if vtype else "?"
            ...         print(f"{owner_hw} -> {var_form} ({type_name})")
            color -> colour (Spelling Variant)
            go -> went (Irregularly Inflected Form)

        Notes:
            - Returns the ILexEntry that contains this variant reference
            - The owner is the variant entry (e.g., "colour")
            - For irregularly inflected forms, owner is the irregular form
            - Use GetComponentLexemes() to get the base form(s)

        See Also:
            GetAll, GetComponentLexemes
        """
        if not variant_or_hvo:
            raise FP_NullParameterError()

        variant = self.__GetVariantObject(variant_or_hvo)

        return variant.Owner


    def GetVariantCount(self, entry_or_hvo):
        """
        Get the count of variant references for an entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.

        Returns:
            int: The number of variant references (0 if none).

        Raises:
            FP_NullParameterError: If entry_or_hvo is None.

        Example:
            >>> entry = project.LexEntry.Find("colour")
            >>> count = project.Variants.GetVariantCount(entry)
            >>> print(f"Entry has {count} variant reference(s)")
            Entry has 1 variant reference(s)

            >>> # Check if entry has any variants
            >>> if project.Variants.GetVariantCount(entry) > 0:
            ...     print("This entry has variants")

        Notes:
            - Returns 0 if entry has no variant references
            - Only counts variant-type references (RefType = 0)
            - More efficient than len(list(GetAll(entry)))
            - An entry can have multiple variant references of different types

        See Also:
            GetAll, Create
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__GetEntryObject(entry_or_hvo)

        count = 0
        for entry_ref in entry.EntryRefsOS:
            if entry_ref.RefType == 0:  # Variant type
                count += 1

        return count


    # --- Private Helper Methods ---

    def __GetEntryObject(self, entry_or_hvo):
        """
        Resolve HVO or object to ILexEntry.

        Args:
            entry_or_hvo: Either an ILexEntry object or an HVO (int).

        Returns:
            ILexEntry: The resolved entry object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a lexical entry.
        """
        if isinstance(entry_or_hvo, int):
            obj = self.project.Object(entry_or_hvo)
            if not isinstance(obj, ILexEntry):
                raise FP_ParameterError("HVO does not refer to a lexical entry")
            return obj
        return entry_or_hvo


    def __GetVariantObject(self, variant_or_hvo):
        """
        Resolve HVO or object to ILexEntryRef.

        Args:
            variant_or_hvo: Either an ILexEntryRef object or an HVO (int).

        Returns:
            ILexEntryRef: The resolved variant reference object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a variant reference.
        """
        if isinstance(variant_or_hvo, int):
            obj = self.project.Object(variant_or_hvo)
            if not isinstance(obj, ILexEntryRef):
                raise FP_ParameterError("HVO does not refer to a variant reference")
            return obj
        return variant_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultVernWs
        )


    def __WSHandleAnalysis(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultAnalWs
        )
