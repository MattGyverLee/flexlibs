# ----------------------------------------------------------------------------
# Name:         CastingOperations
# Purpose:      Wrapper for LCM casting utilities to help with pythonnet interface resolution
#
# FlexLibs 2.3 - Casting utilities for handling polymorphic collections and interface types
# ----------------------------------------------------------------------------

"""
CastingOperations provides utilities for handling pythonnet's strict interface typing.

When working with polymorphic collections (collections that return base interface types),
you often need to cast objects to their concrete types to access type-specific properties.
This class wraps the lcm_casting module utilities for convenient access.

Example::

    from flexlibs2 import FLExProject, CastingOperations
    
    project = FLExProject()
    project.OpenProject("my project")
    
    # Get a morph that could be IMoAffixAllomorph or IMoStemAllomorph
    entry = project.LexEntry.Find("running")
    morphs = entry.LexemeFormOA
    
    # Cast to concrete type to access type-specific properties
    concrete = CastingOperations.cast_to_concrete(morphs)
    
    # Or use the helper for a specific pattern
    pos = CastingOperations.get_pos_from_msa(msa_obj)
"""

from .lcm_casting import (
    cast_to_concrete as _cast_to_concrete,
    get_pos_from_msa as _get_pos_from_msa,
    get_from_pos_from_msa as _get_from_pos_from_msa,
    cast_phonological_rule as _cast_phonological_rule,
    clone_properties as _clone_properties,
    validate_merge_compatibility as _validate_merge_compatibility,
    get_common_properties as _get_common_properties,
    get_concrete_type_properties as _get_concrete_type_properties,
)


class CastingOperations:
    """
    Utility class for casting LCM objects to concrete interface types.

    Pythonnet strictly respects .NET interface typing, which can make it challenging
    to work with polymorphic collections that return base interface types. These utilities
    help you discover and cast to the concrete implementations.

    **The Casting Problem**

    FieldWorks uses polymorphic collections where objects are typed as a base interface
    but actually contain concrete subtypes. Example::

        # MorphoSyntaxAnalysesOC collection is typed as IMoMorphSynAnalysis,
        # but might actually contain:
        # - IMoStemMsa (for stems)
        # - IMoDerivAffMsa (for derivational affixes)
        # - IMoInflAffMsa (for inflectional affixes)
        # - etc.

        msa = entry.SensesOS[0].MorphoSyntaxAnalysisRA  # Typed as IMoMorphSynAnalysis
        msa.PartOfSpeechRA  # Works - available on base type
        msa.InflectionClassRA  # ERROR - only on IMoStemMsa, not on base type!

    **The Solution: Cast to Concrete Type**

    Use cast_to_concrete() to access type-specific properties::

        msa = entry.SensesOS[0].MorphoSyntaxAnalysisRA
        concrete_msa = CastingOperations.cast_to_concrete(msa)

        # Now pythonnet knows the actual type and allows type-specific properties
        if concrete_msa.ClassName == 'MoStemMsa':
            inflection_class = concrete_msa.InflectionClassRA  # Now OK!

    **Property Availability by Type** (ClassName -> Unique Properties)

    Common types and their unique properties::

        # IMoStemMsa (ClassName='MoStemMsa'): PartOfSpeechRA, InflectionClassRA,
        #   MsFeaturesOA, SlotsRC, FromPartsOfSpeechRC, ProdRestrictRC, StratumRA

        # IMoDerivAffMsa (ClassName='MoDerivAffMsa'): FromPartOfSpeechRA,
        #   ToPartOfSpeechRA, FromInflectionClassRA, ToInflectionClassRA,
        #   FromMsFeaturesOA, ToMsFeaturesOA, AffixCategoryRA

        # IMoInflAffMsa (ClassName='MoInflAffMsa'): PartOfSpeechRA, AffixCategoryRA,
        #   InflFeatsOA, SlotsRC, FromProdRestrictRC

        # IMoUnclassifiedAffixMsa (ClassName='MoUnclassifiedAffixMsa'):
        #   PartOfSpeechRA only

    **Discovery Tools**

    Use MCP tools to discover properties:
    - resolve_property(property_name) - Shows which types have a property
    - get_navigation_path(from_obj, to_obj) - Shows casting warnings for polymorphic paths
    - search_by_capability("cast to concrete") - Find casting functions
    """

    @staticmethod
    def cast_to_concrete(obj):
        """Cast an LCM object to its concrete interface type.

        When you retrieve an object from a polymorphic collection, it's typed as the
        base interface (e.g., IMoMorphSynAnalysis). This function inspects the object's
        ClassName and casts it to the actual concrete type (e.g., IMoAffixAllomorph).

        Args:
            obj: An LCM object that may be a base interface type

        Returns:
            The same object cast to its concrete interface type, or the original if
            already concrete or if concrete type is not available

        Example::

            # Morph could be IMoAffixAllomorph or IMoStemAllomorph
            morph = entry.LexemeFormOA
            concrete = CastingOperations.cast_to_concrete(morph)
            # Now concrete type is known, can access type-specific properties
            if concrete.ClassName == 'MoAffixAllomorph':
                affix_type = concrete.AffixType
        """
        return _cast_to_concrete(obj)

    @staticmethod
    def get_pos_from_msa(msa):
        """Extract the Part of Speech from a Morph-Syntax Analysis.

        This is a common pattern: entries have allomorphs/morphemes with MSAs that
        specify the part of speech. This helper navigates that relationship.

        Args:
            msa: An IMoMorphSynAnalysis object (or any type of morph analysis)

        Returns:
            The IPartOfSpeech object, or None if not found

        Example::

            entry = project.LexEntry.Find("walk")
            for sense in entry.SensesOS:
                msa = sense.MorphoSyntaxAnalysisRA
                pos = CastingOperations.get_pos_from_msa(msa)
                if pos:
                    print(f"Part of Speech: {pos.Name.BestAnalysisAlternative.Text}")
        """
        return _get_pos_from_msa(msa)

    @staticmethod
    def get_from_pos_from_msa(msa):
        """Extract the source Part of Speech from a derivational MSA.

        For derivational analyses that show what a word is derived from,
        this returns the POS of the source form.

        Args:
            msa: An IMoDerivationalMorphoSynAnalysis object

        Returns:
            The source IPartOfSpeech, or None if not derivational or not found
        """
        return _get_from_pos_from_msa(msa)

    @staticmethod
    def cast_phonological_rule(rule_obj):
        """Cast a phonological rule to its concrete type.

        Phonological rules can be different subtypes (metathesis, insertion, etc.).
        This function casts to the actual concrete type.

        Args:
            rule_obj: An IPhPhonologicalRule object

        Returns:
            The rule cast to its concrete type
        """
        return _cast_phonological_rule(rule_obj)

    @staticmethod
    def clone_properties(source_obj, dest_obj, project=None):
        """Deep clone properties from one object to another.

        Useful for copying data between similar objects while preserving
        object identity and relationships.

        Args:
            source_obj: Source LCM object to copy from
            dest_obj: Destination LCM object to copy to
            project: Optional FLExProject for factory access

        Returns:
            The dest_obj with cloned properties
        """
        return _clone_properties(source_obj, dest_obj, project)

    @staticmethod
    def validate_merge_compatibility(survivor_obj, victim_obj):
        """Check if two objects can be safely merged.

        Before merging entries or senses, validate that they have compatible structures
        to avoid data loss or corruption.

        Args:
            survivor_obj: The object that will survive the merge
            victim_obj: The object that will be merged into survivor

        Returns:
            Tuple (bool, str) - (is_compatible, explanation)
        """
        return _validate_merge_compatibility(survivor_obj, victim_obj)

    @staticmethod
    def get_common_properties(objects):
        """Find properties that all objects in a collection share.

        When batch processing objects, determine what properties you can safely
        access on all of them.

        Args:
            objects: List/iterable of LCM objects

        Returns:
            Set of property names common to all objects
        """
        return _get_common_properties(objects)

    @staticmethod
    def get_concrete_type_properties(lcm_obj):
        """Get all properties available on an object's concrete type.

        Discovers the full property set for an object after casting to its concrete type.
        Useful for introspection and batch operations.

        Args:
            lcm_obj: An LCM object

        Returns:
            Dict mapping property names to their types
        """
        return _get_concrete_type_properties(lcm_obj)
