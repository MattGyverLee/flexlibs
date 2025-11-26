#!/usr/bin/env python3
"""
Demonstration of AgentOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_agent():
    """Demonstrate AgentOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("AgentOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        agents = project.Agent.GetAll(flat=True)
        count = 0
        for agent in agents:
            try:
                name = project.Agent.GetName(agent)
                abbr = project.Agent.GetAbbreviation(agent)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Agent: {info}")
            except UnicodeEncodeError:
                print(f"   Agent: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Agent"
        if not project.Agent.Exists(test_name):
            agent = project.Agent.Create(test_name, "DA")
            print(f"   Created: {project.Agent.GetName(agent)}")
        else:
            agent = project.Agent.Find(test_name)
            print(f"   Agent already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        agent = project.Agent.Find("Demo Agent")
        if agent:
            print(f"   Found by name: {project.Agent.GetName(agent)}")
            guid = project.Agent.GetGuid(agent)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if agent:
            # Test abbreviation
            abbr = project.Agent.GetAbbreviation(agent)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.Agent.SetDescription(agent, "Demo analyzing agent for testing")
            desc = project.Agent.GetDescription(agent)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if agent:
            subagent_name = "Demo Sub-Agent"
            existing_subs = [project.Agent.GetName(s)
                           for s in project.Agent.GetSubitems(agent)]
            if subagent_name not in existing_subs:
                subagent = project.Agent.CreateSubitem(agent, subagent_name, "DSA")
                print(f"   Created subitem: {project.Agent.GetName(subagent)}")

            subs = project.Agent.GetSubitems(agent)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.Agent.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.Agent.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n6. Testing Metadata operations:")
    try:
        if agent:
            created = project.Agent.GetDateCreated(agent)
            modified = project.Agent.GetDateModified(agent)
            print(f"   Created: {created}")
            print(f"   Modified: {modified}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_agent()
