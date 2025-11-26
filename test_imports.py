"""
Test all imports in flexlibs to identify incompatibilities with installed FieldWorks
"""
import sys
import os

# Add FieldWorks to path
sys.path.append(r'C:\Program Files\SIL\FieldWorks 9')

print("Testing flexlibs imports against FieldWorks 9...")
print("=" * 70)

# Try importing flexlibs module by module
modules_to_test = [
    ("FLExInit", "flexlibs.code.FLExInit"),
    ("FLExGlobals", "flexlibs.code.FLExGlobals"),
    ("FLExProject", "flexlibs.code.FLExProject"),
    ("POSOperations", "flexlibs.code.Grammar.POSOperations"),
    ("PhonemeOperations", "flexlibs.code.Grammar.PhonemeOperations"),
    ("NaturalClassOperations", "flexlibs.code.Grammar.NaturalClassOperations"),
    ("EnvironmentOperations", "flexlibs.code.Grammar.EnvironmentOperations"),
    ("MorphRuleOperations", "flexlibs.code.Grammar.MorphRuleOperations"),
    ("InflectionFeatureOperations", "flexlibs.code.Grammar.InflectionFeatureOperations"),
    ("GramCatOperations", "flexlibs.code.Grammar.GramCatOperations"),
    ("PhonologicalRuleOperations", "flexlibs.code.Grammar.PhonologicalRuleOperations"),
]

failed_modules = []
passed_modules = []

for name, module_path in modules_to_test:
    try:
        __import__(module_path)
        print(f"✓ {name:40s} OK")
        passed_modules.append(name)
    except ImportError as e:
        print(f"✗ {name:40s} FAILED: {e}")
        failed_modules.append((name, str(e)))
    except Exception as e:
        print(f"? {name:40s} ERROR: {e}")
        failed_modules.append((name, str(e)))

print("=" * 70)
print(f"Passed: {len(passed_modules)}/{len(modules_to_test)}")
print(f"Failed: {len(failed_modules)}/{len(modules_to_test)}")

if failed_modules:
    print("\n" + "=" * 70)
    print("FAILED MODULES - Need to be fixed or disabled:")
    print("=" * 70)
    for name, error in failed_modules:
        print(f"\n{name}:")
        print(f"  {error}")
