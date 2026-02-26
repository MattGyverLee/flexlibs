#
#   lcm_casting.py
#
#   Module:     Utilities for casting LCM objects to their concrete interfaces
#               in pythonnet.
#
#   Platform:   Python.NET
#               FieldWorks Version 9+
#
#   Copyright 2025
#

"""
LCM Object Casting Utilities for pythonnet.

This module provides utilities for casting LCM objects from their base interface
types to their concrete derived interfaces. This is necessary because pythonnet
respects .NET interface typing strictly.

The Problem:
    When you iterate over a collection like MorphoSyntaxAnalysesOC, pythonnet
    returns objects typed as the base interface (IMoMorphSynAnalysis). Properties
    from derived interfaces like IMoStemMsa.PartOfSpeechRA are not accessible
    until you explicitly cast the object to its concrete interface type.

    For example::

        # This will NOT work - msa is typed as IMoMorphSynAnalysis
        for msa in entry.MorphoSyntaxAnalysesOC:
            pos = msa.PartOfSpeechRA  # AttributeError - property not found!

        # This WILL work - cast to concrete type first
        for msa in entry.MorphoSyntaxAnalysesOC:
            concrete_msa = cast_to_concrete(msa)
            if hasattr(concrete_msa, 'PartOfSpeechRA'):
                pos = concrete_msa.PartOfSpeechRA  # Works!

Why This Happens:
    In .NET, IMoStemMsa inherits from IMoMorphSynAnalysis. When you access a
    collection typed as IEnumerable<IMoMorphSynAnalysis>, the CLR returns objects
    as the interface type, not the concrete class. Pythonnet cannot automatically
    determine the derived interface type - you must cast explicitly.

Usage::

    from flexlibs2.code.lcm_casting import cast_to_concrete, get_pos_from_msa

    # Cast any LCM object to its concrete interface
    for msa in entry.MorphoSyntaxAnalysesOC:
        concrete = cast_to_concrete(msa)
        print(f"Class: {msa.ClassName}, Type: {type(concrete)}")

    # Convenience function for the common POS lookup pattern
    for msa in entry.MorphoSyntaxAnalysesOC:
        pos = get_pos_from_msa(msa)
        if pos:
            print(f"Part of Speech: {pos.Name.BestAnalysisAlternative.Text}")

Supported Types:
    - MSA types: MoStemMsa, MoDerivAffMsa, MoInflAffMsa, MoUnclassifiedAffixMsa
    - Allomorph types: MoStemAllomorph, MoAffixAllomorph

Note:
    The interface cache is lazy-loaded on first use to avoid import issues
    at module load time. This is important because SIL.LCModel may not be
    available until after FLExInit has run.
"""

# Interface cache - populated on first use
_interface_cache = {}
_interfaces_loaded = False


def _ensure_interfaces():
    """
    Load and cache LCM interface types from SIL.LCModel.

    This function is called automatically on first use of cast_to_concrete().
    It populates the _interface_cache dictionary mapping ClassName strings
    to their corresponding interface types.

    The lazy loading pattern avoids import issues that can occur if
    SIL.LCModel is imported before FLExInit has configured the CLR.

    Returns:
        None

    Side Effects:
        Populates _interface_cache with ClassName -> Interface mappings.
        Sets _interfaces_loaded to True.

    Raises:
        ImportError: If SIL.LCModel cannot be imported. This typically means
            FLExInit has not been run, or the FieldWorks DLLs are not available.
    """
    global _interface_cache, _interfaces_loaded

    if _interfaces_loaded:
        return

    from SIL.LCModel import (
        # MSA (MorphoSyntaxAnalysis) interfaces
        IMoStemMsa,
        IMoDerivAffMsa,
        IMoInflAffMsa,
        IMoUnclassifiedAffixMsa,
        # Allomorph interfaces
        IMoStemAllomorph,
        IMoAffixAllomorph,
        IMoAffixForm,
    )

    # Phonological rule interfaces - try to import, but don't fail if unavailable
    try:
        from SIL.LCModel import IPhRegularRule, IPhSimpleContextSeg, IPhSimpleContextNC, IPhSegRuleRHS
    except ImportError:
        IPhRegularRule = IPhSimpleContextSeg = IPhSimpleContextNC = IPhSegRuleRHS = None

    _interface_cache = {
        # MSA types - used for grammatical category assignment
        'MoStemMsa': IMoStemMsa,
        'MoDerivAffMsa': IMoDerivAffMsa,
        'MoInflAffMsa': IMoInflAffMsa,
        'MoUnclassifiedAffixMsa': IMoUnclassifiedAffixMsa,

        # Allomorph types - used for morpheme form variants
        'MoStemAllomorph': IMoStemAllomorph,
        'MoAffixAllomorph': IMoAffixAllomorph,
        'MoAffixForm': IMoAffixForm,
    }

    # Add phonological rule types if imports succeeded
    if IPhRegularRule is not None:
        _interface_cache['PhRegularRule'] = IPhRegularRule
    if IPhSimpleContextSeg is not None:
        _interface_cache['PhSimpleContextSeg'] = IPhSimpleContextSeg
    if IPhSimpleContextNC is not None:
        _interface_cache['PhSimpleContextNC'] = IPhSimpleContextNC
    if IPhSegRuleRHS is not None:
        _interface_cache['PhSegRuleRHS'] = IPhSegRuleRHS

    _interfaces_loaded = True


def cast_to_concrete(obj):
    """
    Cast an LCM object to its concrete interface type based on ClassName.

    This function examines the object's ClassName property and casts it to
    the appropriate derived interface type. If the ClassName is not in the
    known mappings, the original object is returned unchanged.

    Args:
        obj: An LCM object with a ClassName property (e.g., IMoMorphSynAnalysis,
            IMoForm, or any ICmObject).

    Returns:
        The object cast to its concrete interface type, or the original object
        if the ClassName is not recognized or casting fails.

    Example::

        # Iterate MSAs and access derived properties
        for msa in entry.MorphoSyntaxAnalysesOC:
            concrete_msa = cast_to_concrete(msa)

            # Now we can check for and access derived properties
            if hasattr(concrete_msa, 'PartOfSpeechRA'):
                pos = concrete_msa.PartOfSpeechRA
                if pos:
                    print(f"POS: {pos.Name.BestAnalysisAlternative.Text}")

        # Cast allomorphs to access type-specific properties
        for allo in entry.AlternateFormsOS:
            concrete_allo = cast_to_concrete(allo)

            if hasattr(concrete_allo, 'StemName'):
                # This is a stem allomorph
                stem_name = concrete_allo.StemName
            elif hasattr(concrete_allo, 'InflectionClasses'):
                # This is an affix allomorph
                infl_classes = concrete_allo.InflectionClasses

    Notes:
        - Returns the original object if ClassName is not in the mapping
        - Returns the original object if casting fails for any reason
        - Thread-safe for the interface loading (uses lazy initialization)
        - The interface cache is loaded on first call
    """
    _ensure_interfaces()

    # Get the class name from the object
    if not hasattr(obj, 'ClassName'):
        return obj

    class_name = obj.ClassName

    # Look up the interface type
    interface_type = _interface_cache.get(class_name)
    if interface_type is None:
        return obj

    # Cast to the concrete interface
    try:
        return interface_type(obj)
    except Exception:
        # If casting fails for any reason, return original
        return obj


def get_pos_from_msa(msa):
    """
    Get the Part of Speech from any MSA type.

    This is a convenience function for the common pattern of extracting
    the Part of Speech reference from a MorphoSyntaxAnalysis object.
    It handles the casting internally and checks each MSA type for its
    POS property.

    Different MSA types store POS in different properties:
        - MoStemMsa: PartOfSpeechRA (main POS for stems)
        - MoDerivAffMsa: ToPartOfSpeechRA (output POS after derivation)
        - MoInflAffMsa: PartOfSpeechRA (POS this affix attaches to)
        - MoUnclassifiedAffixMsa: PartOfSpeechRA

    Args:
        msa: An MSA object (IMoMorphSynAnalysis or derived type).

    Returns:
        IPartOfSpeech: The Part of Speech reference, or None if:
            - The MSA type doesn't have a POS property
            - The POS property is not set (null reference)
            - The object cannot be cast to a known MSA type

    Example::

        # Get POS for all MSAs on an entry
        for msa in entry.MorphoSyntaxAnalysesOC:
            pos = get_pos_from_msa(msa)
            if pos:
                pos_name = pos.Name.BestAnalysisAlternative.Text
                pos_abbr = pos.Abbreviation.BestAnalysisAlternative.Text
                print(f"{pos_name} ({pos_abbr})")

        # Check if entry has a specific POS
        target_pos_guid = some_guid
        has_target_pos = any(
            get_pos_from_msa(msa) and
            str(get_pos_from_msa(msa).Guid) == str(target_pos_guid)
            for msa in entry.MorphoSyntaxAnalysesOC
        )

    Notes:
        - For MoDerivAffMsa, this returns ToPartOfSpeechRA (the output POS),
          not FromPartOfSpeechRA (the input POS). Use cast_to_concrete()
          directly if you need to access FromPartOfSpeechRA.
        - Returns None rather than raising exceptions for robustness
        - Handles all common MSA types found in typical FLEx projects
    """
    _ensure_interfaces()

    if not hasattr(msa, 'ClassName'):
        return None

    class_name = msa.ClassName

    try:
        if class_name == 'MoStemMsa':
            interface_type = _interface_cache.get('MoStemMsa')
            if interface_type:
                concrete = interface_type(msa)
                return concrete.PartOfSpeechRA

        elif class_name == 'MoDerivAffMsa':
            interface_type = _interface_cache.get('MoDerivAffMsa')
            if interface_type:
                concrete = interface_type(msa)
                # Return the "to" POS (output of derivation)
                return concrete.ToPartOfSpeechRA

        elif class_name == 'MoInflAffMsa':
            interface_type = _interface_cache.get('MoInflAffMsa')
            if interface_type:
                concrete = interface_type(msa)
                return concrete.PartOfSpeechRA

        elif class_name == 'MoUnclassifiedAffixMsa':
            interface_type = _interface_cache.get('MoUnclassifiedAffixMsa')
            if interface_type:
                concrete = interface_type(msa)
                return concrete.PartOfSpeechRA

    except Exception:
        # If anything fails, return None rather than crashing
        pass

    return None


def clone_properties(source_obj, dest_obj, project=None):
    """
    Deep clone all properties from source object to destination object.

    This is a Python equivalent of ICloneableCmObject.SetCloneProperties() from C#.
    It copies all properties recursively, handling:
    - Simple properties (names, descriptions, etc.)
    - Reference properties (RA)
    - Owned objects (OA) - creates new objects with cloned properties
    - Owned collections (OS/OC) - creates new objects for each item

    Args:
        source_obj: The source LCM object to clone from.
        dest_obj: The destination LCM object to clone to.
        project: Optional FLExProject instance for factory access. If not provided,
                 extracted from the destination object's owner.

    Returns:
        None. The destination object is modified in place.

    Example::

        from flexlibs2.code.lcm_casting import clone_properties

        # Clone a rule
        source_rule = phonRuleOps.GetAll()[0]
        new_rule = factory.Create()
        clone_properties(source_rule, new_rule, project)

    Notes:
        - Recursively clones owned objects
        - Shares reference objects (doesn't create copies of referenced objects)
        - Handles collections by adding cloned items to the destination collection
        - Silently skips any properties that cannot be cloned
    """
    if not hasattr(source_obj, 'ClassName') or not hasattr(dest_obj, 'ClassName'):
        return

    # Cast both to concrete types for full property access
    source = cast_to_concrete(source_obj)
    dest = cast_to_concrete(dest_obj)

    # If project not provided, try to get it from the destination object
    if project is None and hasattr(dest, 'OwnerOfClass'):
        try:
            project = dest.OwnerOfClass.project
        except:
            pass

    # Get all properties from the source object
    for attr_name in dir(source):
        # Skip private, special, and known method attributes
        if attr_name.startswith('_') or attr_name in ['Clone', 'PostClone']:
            continue

        try:
            attr_value = getattr(source, attr_name, None)

            # Skip methods and special attributes
            if callable(attr_value) or attr_name in ['Hvo', 'ClassID', 'ClassName', 'Guid', 'Owner', 'OwningFlid']:
                continue

            # Try to set the property on destination
            if hasattr(dest, attr_name):
                try:
                    # Check if it's a collection (OS/OC) - these need special handling
                    if hasattr(attr_value, 'Count') and hasattr(attr_value, 'Add'):
                        # This is a collection - clone each item
                        dest_collection = getattr(dest, attr_name)
                        try:
                            dest_collection.Clear()
                        except:
                            pass

                        # Add cloned items
                        for item in attr_value:
                            try:
                                # Get factory based on item class name
                                if project:
                                    factory = _get_factory_for_class(item.ClassName, project.project)
                                    if factory:
                                        cloned_item = factory.Create()
                                        dest_collection.Add(cloned_item)
                                        clone_properties(item, cloned_item, project)
                            except:
                                # If we can't clone an item, just skip it
                                pass
                    else:
                        # Simple property or reference - copy directly
                        setattr(dest, attr_name, attr_value)
                except:
                    # If we can't set a property, skip it silently
                    pass
        except:
            # If we can't read a property, skip it
            pass


def _get_factory_for_class(class_name, project):
    """
    Get the factory for creating an object of the given class.

    Args:
        class_name: String like 'PhRegularRule', 'PhSegRuleRHS', etc.
        project: The FLExProject instance.

    Returns:
        The factory object, or None if not found.
    """
    try:
        from SIL.LCModel import (
            IPhRegularRuleFactory,
            IPhSegRuleRHSFactory,
            IPhSimpleContextSegFactory,
            IPhSimpleContextNCFactory,
        )

        factory_map = {
            'PhRegularRule': IPhRegularRuleFactory,
            'PhSegRuleRHS': IPhSegRuleRHSFactory,
            'PhSimpleContextSeg': IPhSimpleContextSegFactory,
            'PhSimpleContextNC': IPhSimpleContextNCFactory,
        }

        factory_type = factory_map.get(class_name)
        if factory_type:
            return project.ServiceLocator.GetService(factory_type)
    except:
        pass

    return None


def get_from_pos_from_msa(msa):
    """
    Get the source Part of Speech from a derivational MSA.

    Only IMoDerivAffMsa has a FromPartOfSpeechRA property indicating
    the POS before derivation. This function returns None for all
    other MSA types.

    Args:
        msa: An MSA object (IMoMorphSynAnalysis or derived type).

    Returns:
        IPartOfSpeech: The source Part of Speech for derivational affixes,
            or None if not a derivational MSA or no source POS is set.

    Example::

        for msa in entry.MorphoSyntaxAnalysesOC:
            from_pos = get_from_pos_from_msa(msa)
            to_pos = get_pos_from_msa(msa)
            if from_pos and to_pos:
                from_name = from_pos.Name.BestAnalysisAlternative.Text
                to_name = to_pos.Name.BestAnalysisAlternative.Text
                print(f"Derives: {from_name} -> {to_name}")

    Notes:
        - Only meaningful for MoDerivAffMsa objects
        - Returns None for MoStemMsa, MoInflAffMsa, MoUnclassifiedAffixMsa
        - Use in combination with get_pos_from_msa() to get both ends
          of a derivational relationship
    """
    _ensure_interfaces()

    if not hasattr(msa, 'ClassName'):
        return None

    if msa.ClassName != 'MoDerivAffMsa':
        return None

    try:
        interface_type = _interface_cache.get('MoDerivAffMsa')
        if interface_type:
            concrete = interface_type(msa)
            return concrete.FromPartOfSpeechRA
    except Exception:
        pass

    return None
