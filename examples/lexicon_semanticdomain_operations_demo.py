#!/usr/bin/env python3
"""
Demonstration of SemanticDomainOperations for flexlibs

This script demonstrates the comprehensive SemanticDomainOperations class
for managing semantic domains in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_semanticdomain_operations():
    """Demonstrate SemanticDomainOperations functionality."""

    # Initialize FieldWorks
    FLExInitialize()

    # Open project
    project = FLExProject()
    try:
        project.OpenProject(r"C:\ProgramData\SIL\FieldWorks\Projects\Kenyang-M\Kenyang-M.fwdata", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("SemanticDomainOperations Demonstration")
    print("=" * 60)

    # --- 1. GetAll - List all semantic domains ---
    print("\n1. Getting all semantic domains (flat list):")
    try:
        all_domains = project.SemanticDomains.GetAll(flat=True)
        print(f"   Total semantic domains: {len(all_domains)}")

        count = 0
        for domain in all_domains:
            number = project.SemanticDomains.GetNumber(domain)
            name = project.SemanticDomains.GetName(domain)
            try:
                print(f"   {number} - {name}")
            except UnicodeEncodeError:
                print(f"   {number} - [Unicode name]")
            count += 1
            if count >= 10:  # Show first 10 only
                print("   ...")
                break
    except Exception as e:
        print(f"   ERROR in GetAll: {e}")

    # --- 2. GetAll (hierarchical) - Get top-level domains ---
    print("\n2. Getting top-level semantic domains:")
    try:
        top_level = project.SemanticDomains.GetAll(flat=False)
        print(f"   Top-level domains: {len(top_level)}")
        for domain in top_level[:5]:  # Show first 5
            number = project.SemanticDomains.GetNumber(domain)
            name = project.SemanticDomains.GetName(domain)
            try:
                print(f"   {number} - {name}")
            except UnicodeEncodeError:
                print(f"   {number} - [Unicode name]")
    except Exception as e:
        print(f"   ERROR in GetAll (hierarchical): {e}")

    # --- 3. Find - Find a domain by number ---
    print("\n3. Finding semantic domains by number:")
    test_domain = None
    try:
        # Try to find a common domain
        domain = project.SemanticDomains.Find("1.1")
        if domain:
            number = project.SemanticDomains.GetNumber(domain)
            name = project.SemanticDomains.GetName(domain)
            try:
                print(f"   Found domain 1.1: {name}")
            except UnicodeEncodeError:
                print(f"   Found domain 1.1: [Unicode name]")
            test_domain = domain
        else:
            print("   Domain 1.1 not found")
    except Exception as e:
        print(f"   ERROR in Find: {e}")

    # --- 4. FindByName - Find a domain by name ---
    print("\n4. Finding semantic domains by name:")
    try:
        # Try common domain names
        for search_name in ["Sky", "Person", "Walk"]:
            domain = project.SemanticDomains.FindByName(search_name)
            if domain:
                number = project.SemanticDomains.GetNumber(domain)
                name = project.SemanticDomains.GetName(domain)
                try:
                    print(f"   Found '{search_name}': {number} - {name}")
                except UnicodeEncodeError:
                    print(f"   Found '{search_name}': {number} - [Unicode]")
                break
    except Exception as e:
        print(f"   ERROR in FindByName: {e}")

    # --- 5. Exists - Check domain existence ---
    print("\n5. Checking domain existence:")
    try:
        print(f"   Domain '1.1' exists: {project.SemanticDomains.Exists('1.1')}")
        print(f"   Domain '999.999' exists: {project.SemanticDomains.Exists('999.999')}")
    except Exception as e:
        print(f"   ERROR in Exists: {e}")

    # --- 6. GetName - Get domain name ---
    print("\n6. Getting domain names:")
    try:
        if test_domain:
            name = project.SemanticDomains.GetName(test_domain)
            try:
                print(f"   Domain name: {name}")
            except UnicodeEncodeError:
                print(f"   Domain name: [Unicode]")
    except Exception as e:
        print(f"   ERROR in GetName: {e}")

    # --- 7. GetDescription - Get domain description ---
    print("\n7. Getting domain description:")
    try:
        if test_domain:
            desc = project.SemanticDomains.GetDescription(test_domain)
            if desc:
                # Show first 100 characters
                desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                try:
                    print(f"   Description: {desc_short}")
                except UnicodeEncodeError:
                    print(f"   Description: [Unicode description]")
            else:
                print("   No description set")
    except Exception as e:
        print(f"   ERROR in GetDescription: {e}")

    # --- 8. GetNumber - Get domain number ---
    print("\n8. Getting domain numbers:")
    try:
        if test_domain:
            number = project.SemanticDomains.GetNumber(test_domain)
            print(f"   Domain number: {number}")

            # Show hierarchy level
            depth = project.SemanticDomains.GetDepth(test_domain)
            print(f"   Domain depth: {depth}")
    except Exception as e:
        print(f"   ERROR in GetNumber: {e}")

    # --- 9. GetSubdomains - Get child domains ---
    print("\n9. Getting subdomains:")
    try:
        if test_domain:
            subdomains = project.SemanticDomains.GetSubdomains(test_domain)
            print(f"   Subdomains: {len(subdomains)}")
            for subdomain in subdomains[:5]:  # Show first 5
                number = project.SemanticDomains.GetNumber(subdomain)
                name = project.SemanticDomains.GetName(subdomain)
                try:
                    print(f"   - {number}: {name}")
                except UnicodeEncodeError:
                    print(f"   - {number}: [Unicode name]")
    except Exception as e:
        print(f"   ERROR in GetSubdomains: {e}")

    # --- 10. GetParent - Get parent domain ---
    print("\n10. Getting parent domain:")
    try:
        if test_domain:
            parent = project.SemanticDomains.GetParent(test_domain)
            if parent:
                parent_number = project.SemanticDomains.GetNumber(parent)
                parent_name = project.SemanticDomains.GetName(parent)
                try:
                    print(f"   Parent domain: {parent_number} - {parent_name}")
                except UnicodeEncodeError:
                    print(f"   Parent domain: {parent_number} - [Unicode]")
            else:
                print("   This is a top-level domain")
    except Exception as e:
        print(f"   ERROR in GetParent: {e}")

    # --- 11. GetSensesInDomain - Get senses using this domain ---
    print("\n11. Getting senses in domain:")
    try:
        if test_domain:
            senses = project.SemanticDomains.GetSensesInDomain(test_domain)
            print(f"   Senses in this domain: {len(senses)}")

            count = 0
            for sense in senses:
                entry = sense.Entry
                headword = project.LexEntry.GetHeadword(entry)
                gloss = project.LexiconGetSenseGloss(sense)
                try:
                    print(f"   - {headword}: {gloss}")
                except UnicodeEncodeError:
                    print(f"   - [Unicode entry]")
                count += 1
                if count >= 5:  # Show first 5 only
                    print("   ...")
                    break
    except Exception as e:
        print(f"   ERROR in GetSensesInDomain: {e}")

    # --- 12. GetSenseCount - Count senses in domain ---
    print("\n12. Getting sense counts:")
    try:
        if test_domain:
            count = project.SemanticDomains.GetSenseCount(test_domain)
            number = project.SemanticDomains.GetNumber(test_domain)
            name = project.SemanticDomains.GetName(test_domain)
            try:
                print(f"   Domain {number} ({name}): {count} senses")
            except UnicodeEncodeError:
                print(f"   Domain {number}: {count} senses")
    except Exception as e:
        print(f"   ERROR in GetSenseCount: {e}")

    # --- 13. Create - Create a custom domain ---
    print("\n13. Creating a custom semantic domain:")
    custom_domain = None
    try:
        # Create a custom domain with high number to avoid conflicts
        if not project.SemanticDomains.Exists("999"):
            custom_domain = project.SemanticDomains.Create("Test Domain", "999")
            number = project.SemanticDomains.GetNumber(custom_domain)
            name = project.SemanticDomains.GetName(custom_domain)
            print(f"   Created domain: {number} - {name}")
        else:
            print("   Domain 999 already exists")
            custom_domain = project.SemanticDomains.Find("999")
    except Exception as e:
        print(f"   ERROR in Create: {e}")

    # --- 14. SetName - Update domain name ---
    print("\n14. Setting domain name:")
    try:
        if custom_domain:
            project.SemanticDomains.SetName(custom_domain, "Test Domain (Updated)")
            name = project.SemanticDomains.GetName(custom_domain)
            print(f"   Updated name: {name}")
    except Exception as e:
        print(f"   ERROR in SetName: {e}")

    # --- 15. SetDescription - Update domain description ---
    print("\n15. Setting domain description:")
    try:
        if custom_domain:
            project.SemanticDomains.SetDescription(custom_domain,
                "This is a test domain for demonstration purposes.")
            desc = project.SemanticDomains.GetDescription(custom_domain)
            print(f"   Updated description: {desc}")
    except Exception as e:
        print(f"   ERROR in SetDescription: {e}")

    # --- 16. Create subdomain ---
    print("\n16. Creating a subdomain:")
    custom_subdomain = None
    try:
        if custom_domain:
            if not project.SemanticDomains.Exists("999.1"):
                custom_subdomain = project.SemanticDomains.Create(
                    "Test Subdomain", "999.1", parent=custom_domain)
                number = project.SemanticDomains.GetNumber(custom_subdomain)
                name = project.SemanticDomains.GetName(custom_subdomain)
                print(f"   Created subdomain: {number} - {name}")
            else:
                print("   Subdomain 999.1 already exists")
                custom_subdomain = project.SemanticDomains.Find("999.1")
    except Exception as e:
        print(f"   ERROR in Create subdomain: {e}")

    # --- 17. Verify hierarchy ---
    print("\n17. Verifying domain hierarchy:")
    try:
        if custom_subdomain:
            parent = project.SemanticDomains.GetParent(custom_subdomain)
            if parent:
                parent_number = project.SemanticDomains.GetNumber(parent)
                print(f"   Parent of 999.1: {parent_number}")

            depth = project.SemanticDomains.GetDepth(custom_subdomain)
            print(f"   Depth of 999.1: {depth}")

        if custom_domain:
            subdomains = project.SemanticDomains.GetSubdomains(custom_domain)
            print(f"   Subdomains of 999: {len(subdomains)}")
    except Exception as e:
        print(f"   ERROR in hierarchy verification: {e}")

    # --- 18. Cleanup demonstration ---
    print("\n18. Cleanup (removing test domains):")
    try:
        if custom_subdomain:
            project.SemanticDomains.Delete(custom_subdomain)
            print("   Deleted subdomain 999.1")

        if custom_domain:
            project.SemanticDomains.Delete(custom_domain)
            print("   Deleted domain 999")
    except Exception as e:
        print(f"   ERROR in Cleanup: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
SemanticDomainOperations Demo
==============================

This demonstrates the comprehensive SemanticDomainOperations class with 20+ methods:

Core Read Operations:
  - GetAll()               - Get all semantic domains (flat or hierarchical)
  - Find()                 - Find domain by number (e.g., "1.1")
  - FindByName()           - Find domain by name
  - Exists()               - Check if domain exists

Domain Properties:
  - GetName()              - Get domain name
  - SetName()              - Set domain name
  - GetDescription()       - Get domain description
  - SetDescription()       - Set domain description
  - GetAbbreviation()      - Get domain abbreviation
  - GetNumber()            - Get domain number (e.g., "7.2.1")
  - GetQuestions()         - Get elicitation questions
  - GetOcmCodes()          - Get OCM (Outline of Cultural Materials) codes

Hierarchy Operations:
  - GetSubdomains()        - Get direct child subdomains
  - GetParent()            - Get parent domain
  - GetDepth()             - Get depth in hierarchy (0 for top-level)

Usage Operations:
  - GetSensesInDomain()    - Get all senses using this domain
  - GetSenseCount()        - Count senses in domain

Custom Domain Management:
  - Create()               - Create new semantic domain
  - Delete()               - Delete a semantic domain

Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_semanticdomain_operations()
