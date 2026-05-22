#
#   rule_patterns.py
#
#   Module: Pattern-element types for the
#           PhonologicalRuleOperations.WireRule composer.
#
#           These are inert dataclasses used to describe rule contexts
#           at the wrapper level. The composer translates them into
#           LCM simple-context objects.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

"""
Pattern-element types for the PhonologicalRuleOperations.WireRule composer.

These are inert dataclasses used to describe rule contexts at the wrapper
level. The composer translates them into LCM simple-context objects.

Usage::

    from flexlibs2 import Seg, NC, Boundary

    # Build context elements
    seg_t = Seg(phoneme_t)
    vowels_back = NC(vowel_class, plus=[alpha_back])
    word_bdry = Boundary("#")

Greek-variable identity is preserved by re-using the SAME
IPhFeatureConstraint object across multiple NC pattern elements.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Seg:
    """A single-phoneme pattern element, optionally with alpha-feature constraints.

    Args:
        phoneme: An IPhPhoneme, HVO (int), or wrapper representing a
            single phoneme.
        plus: Sequence of IPhFeatureConstraint objects to attach to
            ``PlusConstrRS`` on the resulting IPhSimpleContextNC. These
            express positive alpha-variable bindings (e.g. [+aBack]) that
            apply to the segment's own feature structure -- mechanically
            making the segment behave as a singleton natural class for
            constraint-sharing purposes.
        minus: Sequence of IPhFeatureConstraint objects for
            ``MinusConstrRS`` (negative alpha-variable bindings, e.g. [-aBack]).

    Notes:
        Re-use the SAME IPhFeatureConstraint object across multiple
        positions (Seg or NC) to express alpha/beta/gamma agreement.
        E.g. Bantu N-place assimilation: Seg(N, plus=[alpha_place]) on the
        input, NC(C, plus=[alpha_place]) on the right context.

        A Seg with constraints attaches via IPhSimpleContextNC under the
        hood (not IPhSimpleContextSeg), because IPhSimpleContextSeg has
        no constraint slots in LCM. The composer handles the dispatch
        transparently.
    """
    phoneme: object
    plus: tuple = ()
    minus: tuple = ()


@dataclass(frozen=True)
class NC:
    """A natural-class pattern element, optionally with alpha-feature constraints.

    Args:
        natural_class: An IPhNaturalClass, HVO (int), or wrapper.
        plus: Sequence of IPhFeatureConstraint objects to attach to
            ``PlusConstrRS`` (positive alpha-variable bindings, e.g. [+aBack]).
        minus: Sequence of IPhFeatureConstraint objects to attach to
            ``MinusConstrRS`` (negative alpha-variable bindings, e.g. [-aBack]).

    Notes:
        Re-use the SAME IPhFeatureConstraint object across multiple
        positions to express alpha/beta/gamma agreement.
    """
    natural_class: object
    plus: tuple = ()
    minus: tuple = ()


@dataclass(frozen=True)
class Boundary:
    """A boundary marker pattern element, identified by its FW-shipped name.

    Args:
        marker: One of FieldWorks' standard boundary marker names. The
            default project ships with ``"#"`` (word boundary), ``"+"``
            (morpheme boundary), and ``"."`` (syllable boundary).

    Notes:
        Boundary elements appear only in left/right contexts (never in
        the structural change). The composer looks the marker up by
        name from ``PhonemeSetsOS[0].BoundaryMarkersOC`` rather than
        creating new markers.
    """
    marker: str = "#"


__all__ = ["Seg", "NC", "Boundary"]
