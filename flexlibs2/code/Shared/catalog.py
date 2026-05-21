#
#   catalog.py
#
#   Module: Catalog file discovery and XML parsing helpers for FieldWorks
#           catalog XML formats.
#
#           Phase 5a MVP: only supports the GOLDEtic shape used by the
#           FW Templates/GOLDEtic.xml POS catalog:
#
#               <eticPOSList>
#                 <item type="category" id="Adjective" guid="...">
#                   <abbrev ws="en">adj</abbrev>
#                   <term ws="en">Adjective</term>
#                   <def ws="en">An adjective is ...</def>
#                   <item type="category" ...>  <!-- nested -->
#                 </item>
#                 ...
#               </eticPOSList>
#
#           Other FW catalog shapes (LocalizedLists, semantic-domain catalogs,
#           inflection-feature catalogs) will be added in later phases; until
#           then keep this module narrowly scoped to GOLDEtic.
#
#   Platform: Python (stdlib only; no FieldWorks/.NET dependency)
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .. import FLExGlobals


# --- Public dataclasses ------------------------------------------------------


@dataclass
class CatalogEntry:
    """
    One <item type="category"> from the GOLDEtic catalog.

    Attributes:
        id:       The catalog id, e.g. "Adjective". This is the suffix of
                  the canonical CatalogSourceId ("GOLD:Adjective").
        guid:     The canonical FW GUID for this category, as a string.
                  e.g. "30d07580-5052-4d91-bc24-469b8b2d7df9".
        abbrev:   Map of writing-system tag -> abbreviation string,
                  e.g. {"en": "adj", "fr": "adj", "ko": "형"}.
        term:     Map of writing-system tag -> name/term string,
                  e.g. {"en": "Adjective", "fr": "Adjectif"}.
        def_:     Map of writing-system tag -> definition string. Note
                  the trailing underscore: "def" is a Python keyword.
        children: List of nested CatalogEntry items (sub-categories
                  in the catalog hierarchy).
    """

    id: str
    guid: str
    abbrev: Dict[str, str] = field(default_factory=dict)
    term: Dict[str, str] = field(default_factory=dict)
    def_: Dict[str, str] = field(default_factory=dict)
    children: List["CatalogEntry"] = field(default_factory=list)


@dataclass
class CatalogImportResult:
    """
    Summary of what happened during a catalog import.

    Attributes:
        created_count: Number of new POSs created.
        skipped_count: Number of catalog entries skipped because a POS
                       with the same canonical GUID already exists.
        created_guids: Canonical GUIDs (as strings) for the POSs that
                       were created. Useful for verification and tests.
        warnings:      Human-readable warnings (e.g. WS tags present in
                       the catalog but missing from the project).
    """

    created_count: int = 0
    skipped_count: int = 0
    created_guids: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# --- File discovery ----------------------------------------------------------


def find_catalog_file(filename):
    """
    Locate a catalog XML file under the FieldWorks Templates directory.

    Uses FLExGlobals.FWCodeDir (resolved during FLEx init from the
    Windows registry) so it works against whatever FW install the
    user actually has. Does not hard-code "C:/Program Files/SIL/...".

    Args:
        filename (str): The catalog filename, e.g. "GOLDEtic.xml".

    Returns:
        str: Absolute path to the catalog file.

    Raises:
        RuntimeError: If FLExGlobals.FWCodeDir has not been initialised
                      (caller must have imported flexlibs2 first).
        FileNotFoundError: If the file does not exist at the expected path.
    """
    if FLExGlobals.FWCodeDir is None:
        raise RuntimeError(
            "FLExGlobals.FWCodeDir is not set; "
            "import flexlibs2 (or call FLExGlobals.InitialiseFWGlobals()) first."
        )

    path = os.path.join(FLExGlobals.FWCodeDir, "Templates", filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Catalog file not found at expected location: {}".format(path)
        )
    return path


# --- XML parsing -------------------------------------------------------------


def _parse_item(elem):
    """
    Recursively parse one <item type="category"> element into a
    CatalogEntry. Non-category items are ignored. Children are walked
    depth-first so the returned tree mirrors the on-disk hierarchy.
    """
    entry = CatalogEntry(
        id=elem.get("id") or "",
        guid=elem.get("guid") or "",
    )

    for child in elem:
        tag = child.tag
        if tag == "abbrev":
            ws = child.get("ws") or ""
            if ws and child.text:
                entry.abbrev[ws] = child.text
        elif tag == "term":
            ws = child.get("ws") or ""
            if ws and child.text:
                entry.term[ws] = child.text
        elif tag == "def":
            ws = child.get("ws") or ""
            if ws and child.text:
                entry.def_[ws] = child.text
        elif tag == "item" and child.get("type") == "category":
            entry.children.append(_parse_item(child))
        # Silently ignore unknown / non-category children (source,
        # citation, etc.) - they aren't part of the Phase 5a MVP.

    return entry


def parse_etic_catalog(path):
    """
    Parse a GOLDEtic-shaped POS catalog XML file into a tree of
    CatalogEntry objects.

    Args:
        path (str): Absolute path to GOLDEtic.xml.

    Returns:
        list[CatalogEntry]: The top-level catalog entries. Nested
        sub-categories are reachable via each entry's `.children`.

    Notes:
        - The root element is <eticPOSList>; we walk its direct
          <item type="category"> children and recurse from there.
        - Other root shapes are not supported by this function.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    if root.tag != "eticPOSList":
        raise ValueError(
            "Expected root <eticPOSList>, got <{}>; this parser only "
            "handles the GOLDEtic shape.".format(root.tag)
        )

    entries = []
    for item in root.findall("item"):
        if item.get("type") == "category":
            entries.append(_parse_item(item))
    return entries


# --- Tree navigation ---------------------------------------------------------


def _strip_catalog_prefix(source_id):
    """
    Accept either a bare id ("Adjective") or a prefixed catalog
    source id ("GOLD:Adjective") and return the bare id. Case-sensitive
    on the id portion; the prefix match is case-insensitive.
    """
    if not source_id:
        return ""
    head, sep, tail = source_id.partition(":")
    if sep and head.upper() == "GOLD":
        return tail
    return source_id


def find_catalog_entry(entries, source_id):
    """
    Walk a list of CatalogEntry trees (depth-first) and return the
    entry whose id matches `source_id`. The "GOLD:" prefix is stripped
    before comparison so both "GOLD:Adjective" and "Adjective" work.

    Args:
        entries (list[CatalogEntry]): Result of parse_etic_catalog().
        source_id (str): Catalog source id with or without "GOLD:" prefix.

    Returns:
        CatalogEntry or None: The matching entry, or None if no match.
    """
    target = _strip_catalog_prefix(source_id)
    if not target:
        return None

    def _walk(items):
        for it in items:
            if it.id == target:
                return it
            if it.children:
                hit = _walk(it.children)
                if hit is not None:
                    return hit
        return None

    return _walk(entries)


def count_catalog_entries(entries):
    """
    Count all CatalogEntry items in a forest, including nested children.

    Convenience helper for tests / smoke checks. GOLDEtic.xml has
    16 top-level entries and 58 entries total.

    Args:
        entries (list[CatalogEntry]): Result of parse_etic_catalog().

    Returns:
        int: Total number of entries across the tree.
    """
    total = 0

    def _walk(items):
        nonlocal total
        for it in items:
            total += 1
            if it.children:
                _walk(it.children)

    _walk(entries)
    return total
