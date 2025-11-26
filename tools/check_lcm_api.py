"""
Check what's available in the installed FieldWorks LCM API
"""
import sys
import os

# Initialize flexlibs to set up paths correctly
os.chdir(r'd:\Github\flexlibs')
sys.path.insert(0, r'd:\Github\flexlibs')

print("Initializing FieldWorks...")
print("=" * 70)

# Import the initialization code
from flexlibs.code import FLExGlobals
FLExGlobals.InitialiseFWGlobals()

print(f"FieldWorks Code Dir: {FLExGlobals.FWCodeDir}")
print(f"FieldWorks Version: {FLExGlobals.FWShortVersion}")
print()

# Now check what's in LCModel
import clr
clr.AddReference("SIL.LCModel")

from SIL import LCModel

print("Checking for problematic imports...")
print("=" * 70)

# Test imports from MorphRuleOperations.py
print("\n1. MorphRuleOperations.py imports:")
test_imports = [
    'IMoMorphRule',
    'IMoAffixProcessFactory',
    'IMoStratumFactory',
]

for name in test_imports:
    if hasattr(LCModel, name):
        print(f"   ✓ {name:30s} EXISTS")
    else:
        print(f"   ✗ {name:30s} MISSING")
        # Try to find similar names
        similar = [x for x in dir(LCModel) if name[1:5] in x or name[-10:] in x][:5]
        if similar:
            print(f"      Similar names: {', '.join(similar)}")

# Test imports from InflectionFeatureOperations.py
print("\n2. InflectionFeatureOperations.py imports:")
test_imports = [
    'IMoInflClass',
    'IMoInflClassFactory',
    'IFsFeatStruc',
    'IFsFeatStrucFactory',
    'IFsFeatureDefn',  # This is wrong
    'IFsFeatDefn',     # This might be correct
    'IFsComplexFeature',
    'IFsComplexFeatureFactory',
]

for name in test_imports:
    if hasattr(LCModel, name):
        print(f"   ✓ {name:30s} EXISTS")
    else:
        print(f"   ✗ {name:30s} MISSING")

# Show all IMo* interfaces
print("\n3. All IMo* interfaces available:")
mo_interfaces = [x for x in dir(LCModel) if x.startswith('IMo')]
for i, name in enumerate(mo_interfaces[:20], 1):
    print(f"   {i:3d}. {name}")
if len(mo_interfaces) > 20:
    print(f"   ... and {len(mo_interfaces) - 20} more")

# Show all IFs* interfaces
print("\n4. All IFs* interfaces available:")
fs_interfaces = [x for x in dir(LCModel) if x.startswith('IFs')]
for i, name in enumerate(fs_interfaces[:20], 1):
    print(f"   {i:3d}. {name}")
if len(fs_interfaces) > 20:
    print(f"   ... and {len(fs_interfaces) - 20} more")
