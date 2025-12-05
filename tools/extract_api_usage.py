#!/usr/bin/env python3
"""
extract_api_usage.py

A comprehensive tool for analyzing and documenting SIL API usage across the flexlibs codebase.

This tool scans all Python files in flexlibs/code/ and extracts information about
imports from SIL.* namespaces (LCModel, FieldWorks, WritingSystems, etc.).

Features:
- Extracts all SIL.* imports with line numbers
- Categorizes imports by namespace
- Identifies repositories, factories, interfaces, tags, and utilities
- Outputs detailed JSON reports
- Provides summary statistics
- Supports multiple output formats

Usage:
    python extract_api_usage.py --extract          # Full extraction to JSON
    python extract_api_usage.py --summary          # Summary statistics
    python extract_api_usage.py --by-namespace     # Group by namespace
    python extract_api_usage.py --by-file          # Group by file
    python extract_api_usage.py --all              # All reports

Author: Programmer Team 1
Date: 2025-12-05
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class APIUsageExtractor:
    """
    Extract and analyze SIL API usage from Python source files.

    This class provides comprehensive analysis of SIL.* namespace imports,
    categorizing them by type (repositories, factories, interfaces, etc.)
    and tracking usage across the codebase.

    Attributes:
        code_dir (Path): Path to the flexlibs/code directory
        imports_data (List[Dict]): Detailed import information
        namespace_summary (Dict): Summary by namespace
        class_usage_count (Dict): Usage count per class
        file_dependencies (Dict): Dependencies per file
    """

    # Category patterns for classification
    REPOSITORY_PATTERN = re.compile(r'I\w+Repository$')
    FACTORY_PATTERN = re.compile(r'I\w+Factory$')
    INTERFACE_PATTERN = re.compile(r'^I[A-Z]\w+$')
    TAGS_PATTERN = re.compile(r'\w+Tags$')

    # SIL namespace patterns
    SIL_NAMESPACES = {
        'SIL.LCModel': 'Core LCModel classes and interfaces',
        'SIL.LCModel.Core.Cellar': 'Cellar infrastructure',
        'SIL.LCModel.Core.KernelInterfaces': 'Kernel interfaces (ITsString, etc.)',
        'SIL.LCModel.Core.Text': 'Text utilities (TsStringUtils)',
        'SIL.LCModel.Infrastructure': 'Infrastructure classes',
        'SIL.LCModel.Utils': 'Utility classes',
        'SIL.FieldWorks': 'FieldWorks core',
        'SIL.FieldWorks.Common.Controls': 'UI controls',
        'SIL.FieldWorks.Common.FwUtils': 'FieldWorks utilities',
        'SIL.FieldWorks.FdoUi': 'FDO UI components',
        'SIL.FieldWorks.FwCoreDlgs': 'Core dialogs',
        'SIL.WritingSystems': 'Writing system definitions',
    }

    def __init__(self, code_dir: str = None):
        """
        Initialize the API usage extractor.

        Args:
            code_dir: Path to the code directory (defaults to flexlibs/code)
        """
        if code_dir is None:
            # Determine code directory relative to this script
            script_dir = Path(__file__).parent.parent
            code_dir = script_dir / 'flexlibs' / 'code'

        self.code_dir = Path(code_dir)
        self.imports_data = []
        self.namespace_summary = defaultdict(lambda: {
            'files': set(),
            'classes': set(),
            'count': 0
        })
        self.class_usage_count = defaultdict(int)
        self.file_dependencies = defaultdict(lambda: {
            'namespaces': set(),
            'classes': [],
            'repositories': [],
            'factories': [],
            'interfaces': [],
            'tags': [],
            'utilities': []
        })

    def extract_imports_from_file(self, file_path: Path) -> List[Dict]:
        """
        Extract all SIL.* imports from a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of dictionaries containing import information
        """
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            relative_path = file_path.relative_to(self.code_dir.parent)

            i = 0
            while i < len(lines):
                line = lines[i]
                line_num = i + 1

                # Match: from SIL.* import ...
                from_match = re.match(r'^\s*from\s+(SIL\.[\w.]+)\s+import\s+(.+)', line)
                if from_match:
                    namespace = from_match.group(1)
                    import_part = from_match.group(2).strip()

                    # Handle multi-line imports with parentheses
                    if '(' in import_part and ')' not in import_part:
                        # Multi-line import
                        full_import = import_part
                        start_line = line_num
                        i += 1
                        while i < len(lines) and ')' not in lines[i]:
                            full_import += ' ' + lines[i].strip()
                            i += 1
                        if i < len(lines):
                            full_import += ' ' + lines[i].strip()
                        import_part = full_import
                        end_line = i + 1
                    else:
                        end_line = line_num

                    # Parse imported classes
                    classes = self._parse_import_list(import_part)

                    for cls in classes:
                        import_info = {
                            'file': str(relative_path),
                            'namespace': namespace,
                            'class': cls,
                            'line_start': start_line if ')' in import_part else line_num,
                            'line_end': end_line,
                            'import_type': self._categorize_class(cls),
                            'statement': f"from {namespace} import {cls}"
                        }
                        imports.append(import_info)

                # Match: import SIL.*
                import_match = re.match(r'^\s*import\s+(SIL\.[\w.]+)', line)
                if import_match:
                    namespace = import_match.group(1)
                    import_info = {
                        'file': str(relative_path),
                        'namespace': namespace,
                        'class': namespace.split('.')[-1],
                        'line_start': line_num,
                        'line_end': line_num,
                        'import_type': 'module',
                        'statement': f"import {namespace}"
                    }
                    imports.append(import_info)

                i += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return imports

    def _parse_import_list(self, import_str: str) -> List[str]:
        """
        Parse a potentially complex import statement into individual class names.

        Args:
            import_str: The import portion after 'import'

        Returns:
            List of class names
        """
        # Remove parentheses and comments
        import_str = re.sub(r'[()]', '', import_str)
        import_str = re.sub(r'#.*$', '', import_str, flags=re.MULTILINE)

        # Split by comma and clean
        classes = [c.strip() for c in import_str.split(',')]
        classes = [c for c in classes if c and not c.startswith('#')]

        return classes

    def _categorize_class(self, class_name: str) -> str:
        """
        Categorize a class by its naming pattern.

        Args:
            class_name: Name of the class/interface

        Returns:
            Category string (repository, factory, interface, tags, utility, class)
        """
        if self.REPOSITORY_PATTERN.match(class_name):
            return 'repository'
        elif self.FACTORY_PATTERN.match(class_name):
            return 'factory'
        elif self.TAGS_PATTERN.match(class_name):
            return 'tags'
        elif self.INTERFACE_PATTERN.match(class_name):
            return 'interface'
        elif class_name.endswith('Utils') or class_name.endswith('Helper'):
            return 'utility'
        else:
            return 'class'

    def scan_directory(self) -> None:
        """
        Scan all Python files in the code directory and extract imports.

        Updates the instance's imports_data and summary dictionaries.
        """
        print(f"Scanning directory: {self.code_dir}")

        python_files = list(self.code_dir.rglob('*.py'))
        print(f"Found {len(python_files)} Python files")

        for py_file in python_files:
            imports = self.extract_imports_from_file(py_file)
            self.imports_data.extend(imports)

            # Update summaries
            for imp in imports:
                namespace = imp['namespace']
                cls = imp['class']
                file_path = imp['file']
                import_type = imp['import_type']

                # Namespace summary
                self.namespace_summary[namespace]['files'].add(file_path)
                self.namespace_summary[namespace]['classes'].add(cls)
                self.namespace_summary[namespace]['count'] += 1

                # Class usage count
                self.class_usage_count[cls] += 1

                # File dependencies
                self.file_dependencies[file_path]['namespaces'].add(namespace)
                self.file_dependencies[file_path]['classes'].append(cls)

                # Categorize by type
                if import_type == 'repository':
                    self.file_dependencies[file_path]['repositories'].append(cls)
                elif import_type == 'factory':
                    self.file_dependencies[file_path]['factories'].append(cls)
                elif import_type == 'interface':
                    self.file_dependencies[file_path]['interfaces'].append(cls)
                elif import_type == 'tags':
                    self.file_dependencies[file_path]['tags'].append(cls)
                elif import_type == 'utility':
                    self.file_dependencies[file_path]['utilities'].append(cls)

        print(f"Extracted {len(self.imports_data)} imports")

    def get_summary(self) -> Dict:
        """
        Generate a summary of API usage.

        Returns:
            Dictionary containing summary statistics
        """
        # Convert sets to lists for JSON serialization
        namespace_data = {}
        for ns, data in self.namespace_summary.items():
            namespace_data[ns] = {
                'description': self.SIL_NAMESPACES.get(ns, 'Other SIL namespace'),
                'file_count': len(data['files']),
                'class_count': len(data['classes']),
                'import_count': data['count'],
                'files': sorted(list(data['files'])),
                'classes': sorted(list(data['classes']))
            }

        # Critical dependencies (used in 5+ files)
        critical_deps = {
            cls: count for cls, count in self.class_usage_count.items()
            if count >= 5
        }

        summary = {
            'total_imports': len(self.imports_data),
            'total_namespaces': len(self.namespace_summary),
            'total_unique_classes': len(self.class_usage_count),
            'total_files_analyzed': len(self.file_dependencies),
            'namespaces': namespace_data,
            'critical_dependencies': dict(sorted(
                critical_deps.items(),
                key=lambda x: x[1],
                reverse=True
            )),
            'class_usage_count': dict(sorted(
                self.class_usage_count.items(),
                key=lambda x: x[1],
                reverse=True
            ))
        }

        return summary

    def get_by_namespace(self) -> Dict:
        """
        Get imports grouped by namespace.

        Returns:
            Dictionary with namespaces as keys
        """
        by_namespace = defaultdict(list)

        for imp in self.imports_data:
            by_namespace[imp['namespace']].append({
                'file': imp['file'],
                'class': imp['class'],
                'type': imp['import_type'],
                'line': imp['line_start']
            })

        return dict(by_namespace)

    def get_by_file(self) -> Dict:
        """
        Get imports grouped by file.

        Returns:
            Dictionary with file paths as keys
        """
        result = {}

        for file_path, deps in self.file_dependencies.items():
            result[file_path] = {
                'namespaces': sorted(list(deps['namespaces'])),
                'total_imports': len(deps['classes']),
                'repositories': sorted(set(deps['repositories'])),
                'factories': sorted(set(deps['factories'])),
                'interfaces': sorted(set(deps['interfaces'])),
                'tags': sorted(set(deps['tags'])),
                'utilities': sorted(set(deps['utilities']))
            }

        return result

    def get_full_extraction(self) -> List[Dict]:
        """
        Get complete detailed extraction data.

        Returns:
            List of all import records
        """
        return self.imports_data

    def save_json(self, data: any, output_file: str) -> None:
        """
        Save data to a JSON file.

        Args:
            data: Data to save (must be JSON serializable)
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {output_path}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Extract and analyze SIL API usage from flexlibs codebase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --extract                    # Full detailed extraction
  %(prog)s --summary                    # Summary statistics only
  %(prog)s --by-namespace               # Group by namespace
  %(prog)s --by-file                    # Group by file
  %(prog)s --all                        # Generate all reports
  %(prog)s --extract -o custom.json     # Custom output file
        """
    )

    parser.add_argument(
        '--extract',
        action='store_true',
        help='Extract full detailed API usage data to JSON'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate summary statistics'
    )
    parser.add_argument(
        '--by-namespace',
        action='store_true',
        help='Group imports by namespace'
    )
    parser.add_argument(
        '--by-file',
        action='store_true',
        help='Group imports by file'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all reports'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: api_usage_<type>.json)'
    )
    parser.add_argument(
        '--code-dir',
        help='Path to code directory (default: ../flexlibs/code)'
    )

    args = parser.parse_args()

    # If no options specified, show help
    if not any([args.extract, args.summary, args.by_namespace, args.by_file, args.all]):
        parser.print_help()
        return

    # Create extractor and scan
    extractor = APIUsageExtractor(args.code_dir)
    extractor.scan_directory()

    # Generate requested outputs
    if args.all or args.extract:
        output = args.output or 'api_usage_extract.json'
        data = extractor.get_full_extraction()
        extractor.save_json(data, output)

    if args.all or args.summary:
        output = args.output or 'api_usage_summary.json'
        data = extractor.get_summary()
        extractor.save_json(data, output)

        # Print summary to console
        print("\n" + "="*70)
        print("API USAGE SUMMARY")
        print("="*70)
        print(f"Total imports:        {data['total_imports']}")
        print(f"Unique classes:       {data['total_unique_classes']}")
        print(f"Namespaces used:      {data['total_namespaces']}")
        print(f"Files analyzed:       {data['total_files_analyzed']}")
        print(f"Critical deps (5+):   {len(data['critical_dependencies'])}")
        print("\nTop 10 Most Used Classes:")
        for i, (cls, count) in enumerate(list(data['class_usage_count'].items())[:10], 1):
            print(f"  {i:2d}. {cls:40s} ({count} files)")

    if args.all or args.by_namespace:
        output = args.output or 'api_usage_by_namespace.json'
        data = extractor.get_by_namespace()
        extractor.save_json(data, output)

    if args.all or args.by_file:
        output = args.output or 'api_usage_by_file.json'
        data = extractor.get_by_file()
        extractor.save_json(data, output)

    print("\nExtraction complete!")


if __name__ == '__main__':
    main()
