#
#   test_flexproject_semantic_domains.py
#
#   Regression tests for FLExProject.GetAllSemanticDomains wrapper semantics.
#

import ast
import warnings
from pathlib import Path
from unittest.mock import Mock

import pytest


def _get_semantic_domains_method():
    """Load only the target method body so no FieldWorks runtime is needed."""
    source = Path("flexlibs2/code/FLExProject.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    flex_project = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "FLExProject"
    )
    method = next(
        node
        for node in flex_project.body
        if isinstance(node, ast.FunctionDef) and node.name == "GetAllSemanticDomains"
    )
    method.decorator_list = []
    class_node = ast.ClassDef(
        name="ProjectShim",
        bases=[],
        keywords=[],
        body=[method],
        decorator_list=[],
    )
    ast.fix_missing_locations(class_node)

    namespace = {"warnings": warnings}
    exec(
        compile(
            ast.Module(body=[class_node], type_ignores=[]),
            "<semantic-domain-shim>",
            "exec",
        ),
        namespace,
    )
    return namespace["ProjectShim"].GetAllSemanticDomains


class TestFLExProjectSemanticDomainsWrapper:
    def test_default_gets_all_domains_recursively(self):
        project = Mock()
        method = _get_semantic_domains_method()

        method(project)

        project.SemanticDomains.GetAll.assert_called_once_with(recursive=True)

    @pytest.mark.parametrize(
        ("recursive", "expected"),
        [
            (True, True),
            (False, False),
        ],
    )
    def test_recursive_argument_is_forwarded(self, recursive, expected):
        project = Mock()
        method = _get_semantic_domains_method()

        method(project, recursive=recursive)

        project.SemanticDomains.GetAll.assert_called_once_with(recursive=expected)

    def test_flat_alias_is_deprecated_but_preserves_legacy_meaning(self):
        project = Mock()
        method = _get_semantic_domains_method()

        with pytest.warns(DeprecationWarning, match="recursive"):
            method(project, flat=False)

        project.SemanticDomains.GetAll.assert_called_once_with(recursive=False)

    def test_unexpected_keyword_still_fails(self):
        project = Mock()
        method = _get_semantic_domains_method()

        with pytest.raises(TypeError, match="unexpected keyword"):
            method(project, unknown=True)
