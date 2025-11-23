import re
import os

# Read FLExProject.py
flex_path = r'D:\Github\flexlibs\flexlibs\code\FLExProject.py'
with open(flex_path, 'r', encoding='utf-8') as f:
    flex_content = f.read()
    flex_lines = flex_content.split('\n')

# Extract all public methods with context
methods = []
pattern = r'^\s{4}def ([a-zA-Z][a-zA-Z0-9_]*)\s*\('

for i, line in enumerate(flex_lines):
    match = re.match(pattern, line)
    if match:
        method_name = match.group(1)
        if not method_name.startswith('_'):
            methods.append({'line': i + 1, 'name': method_name})

print(f"Total public methods: {len(methods)}\n")

# Already delegated (from your context)
already_delegated = {
    # Initial 23
    'GetAll', 'Find', 'Create', 'Delete', 'GetName', 'SetName',
    'GetAbbreviation', 'SetAbbreviation', 'GetDescription', 'SetDescription',
    'AddSubitem', 'RemoveSubitem', 'GetSubitems', 'GetParent', 'SetParent',
    'GetOrder', 'SetOrder', 'IsDeprecated', 'SetDeprecated', 'GetGUID',
    'ValidateItem', 'CloneItem', 'GetFeatures',
    # WS 7
    'GetAllWritingSystems', 'GetVernacularWritingSystems', 'GetAnalysisWritingSystems',
    'GetWritingSystemName', 'GetWritingSystemAbbreviation', 'IsVernacularWS', 'IsAnalysisWS',
    # CustomField 9
    'GetAllCustomFields', 'GetCustomFieldNames', 'GetCustomFieldByName', 'GetCustomFieldType',
    'GetCustomFieldValue', 'SetCustomFieldValue', 'ClearCustomFieldValue',
    'GetCustomFieldChoices', 'AddCustomFieldChoice'
}

# Categorize methods
category_a = []  # CAN DELEGATE
category_b = []  # SHOULD KEEP
category_c = []  # NEEDS INVESTIGATION

# Methods that are clearly infrastructure
infrastructure_methods = {
    'OpenProject', 'CloseProject', 'ObjectRepository', 'Object',
    'ProjectName', 'BestStr', 'BuildGotoURL', 'GetDateLastModified'
}

# Methods that are property accessors for Operations
operations_properties = {
    'POS', 'LexEntry', 'Texts', 'Wordforms', 'WfiAnalyses', 'Paragraphs',
    'Segments', 'Phonemes', 'NaturalClasses', 'Environments', 'Allomorphs',
    'MorphRules', 'InflectionFeatures', 'GramCat', 'PhonRules', 'Senses',
    'Examples', 'LexReferences', 'Reversal', 'SemanticDomains', 'Pronunciations',
    'Variants', 'Etymology', 'PossibilityLists', 'CustomFields', 'WritingSystems',
    'WfiGlosses', 'WfiMorphBundles', 'Media', 'Notes', 'Filters', 'Discourse',
    'Person', 'Location', 'Anthropology', 'ProjectSettings', 'Publications',
    'Agents', 'Confidence', 'Overlays', 'TranslationTypes', 'AnnotationDefs',
    'Checks', 'DataNotebook'
}

for method in methods:
    name = method['name']
    line = method['line']

    # Skip if already delegated
    if name in already_delegated:
        continue

    # Category B: Infrastructure
    if name in infrastructure_methods:
        category_b.append({'name': name, 'line': line, 'reason': 'Core infrastructure method'})
        continue

    # Category B: Operations property accessors
    if name in operations_properties:
        category_b.append({'name': name, 'line': line, 'reason': 'Operations class property accessor'})
        continue

    # Check if it's a simple WS helper
    if name.startswith('GetAllVernacular') or name.startswith('GetAllAnalysis') or \
       name.startswith('GetDefault') or name == 'WSUIName' or name == 'WSHandle' or \
       name == 'GetWritingSystems':
        category_a.append({'name': name, 'line': line, 'ops_class': 'WritingSystemOperations', 'note': 'WS utility method'})
        continue

    # Check if it starts with Lexicon - likely delegatable to LexEntry or LexSense
    if name.startswith('Lexicon'):
        if 'Sense' in name:
            ops_class = 'LexSenseOperations'
        elif 'Example' in name:
            ops_class = 'ExampleOperations'
        elif 'Field' in name or 'CustomField' in name:
            ops_class = 'CustomFieldOperations'
        else:
            ops_class = 'LexEntryOperations'

        category_a.append({'name': name, 'line': line, 'ops_class': ops_class, 'note': 'Lexicon method - likely delegatable'})
        continue

    # Check for simple repository/query methods
    if name.startswith('ObjectsIn') or name.startswith('ObjectCountFor'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'Repository', 'note': 'Repository query method'})
        continue

    # Check for domain-specific methods
    if name.startswith('Texts'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'TextOperations', 'note': 'Text-specific method'})
        continue

    if name.startswith('Reversal'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'ReversalOperations', 'note': 'Reversal-specific method'})
        continue

    if name.startswith('GetPartsOfSpeech') or name.startswith('GetAllSemanticDomains'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'POSOperations or SemanticDomainOperations', 'note': 'List retrieval method'})
        continue

    if name.startswith('UnpackNestedPossibilityList') or name.startswith('ListField'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'PossibilityListOperations', 'note': 'Possibility list utility'})
        continue

    if name.startswith('GetLexicalRelationTypes') or name.startswith('GetPublications') or \
       name.startswith('PublicationType'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'LexReferenceOperations or PublicationOperations', 'note': 'Domain-specific getter'})
        continue

    if name.startswith('GetFieldID'):
        category_a.append({'name': name, 'line': line, 'ops_class': 'CustomFieldOperations', 'note': 'Field metadata method'})
        continue

    # Otherwise, needs investigation
    category_c.append({'name': name, 'line': line, 'note': 'Needs analysis to determine if delegatable'})

print("="*80)
print("CATEGORY A: CAN DELEGATE")
print("="*80)
print(f"Total: {len(category_a)} methods\n")
for m in sorted(category_a, key=lambda x: x['line']):
    print(f"{m['line']:5d}: {m['name']:45s} -> {m['ops_class']}")
    if 'note' in m:
        print(f"       Note: {m['note']}")

print("\n" + "="*80)
print("CATEGORY B: SHOULD KEEP")
print("="*80)
print(f"Total: {len(category_b)} methods\n")
for m in sorted(category_b, key=lambda x: x['line']):
    print(f"{m['line']:5d}: {m['name']:45s} - {m['reason']}")

print("\n" + "="*80)
print("CATEGORY C: NEEDS INVESTIGATION")
print("="*80)
print(f"Total: {len(category_c)} methods\n")
for m in sorted(category_c, key=lambda x: x['line']):
    print(f"{m['line']:5d}: {m['name']:45s} - {m['note']}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total public methods:     {len(methods)}")
print(f"Already delegated:        {len(already_delegated)}")
print(f"Category A (Can delegate): {len(category_a)}")
print(f"Category B (Should keep):  {len(category_b)}")
print(f"Category C (Investigate):  {len(category_c)}")
print(f"Accounted for:            {len(already_delegated) + len(category_a) + len(category_b) + len(category_c)}")
