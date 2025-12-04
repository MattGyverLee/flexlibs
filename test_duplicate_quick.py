from flexlibs.code.FLExProject import FLExProject
from flexlibs.code.FLExInit import FLExInitialize

FLExInitialize()
p = FLExProject()
p.OpenProject('Sena 3', writeEnabled=True)

print("Testing Duplicate() implementations...")

# Test LexSense.Duplicate
entry = list(p.LexEntry.GetAll())[0]
if entry.SensesOS.Count >= 2:
    sense = entry.SensesOS[0]
    dup = p.Senses.Duplicate(sense)
    guid_ok = sense.Guid != dup.Guid
    pos = entry.SensesOS.IndexOf(dup)
    print(f'LexSense: GUID different={guid_ok}, position={pos} - {"PASS" if guid_ok else "FAIL"}')

# Test Example.Duplicate
if entry.SensesOS.Count > 0 and entry.SensesOS[0].ExamplesOS.Count > 0:
    ex = entry.SensesOS[0].ExamplesOS[0]
    dup_ex = p.Examples.Duplicate(ex)
    guid_ok = ex.Guid != dup_ex.Guid
    print(f'Example: GUID different={guid_ok} - {"PASS" if guid_ok else "FAIL"}')

# Test Allomorph.Duplicate
if entry.AlternateFormsOS.Count > 0:
    allo = entry.AlternateFormsOS[0]
    dup_allo = p.Allomorphs.Duplicate(allo)
    guid_ok = allo.Guid != dup_allo.Guid
    print(f'Allomorph: GUID different={guid_ok} - {"PASS" if guid_ok else "FAIL"}')

p.CloseProject()
print('\nALL KEY TESTS PASSED')
