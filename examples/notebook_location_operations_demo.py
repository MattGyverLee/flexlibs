#!/usr/bin/env python3
"""
Demonstration of LocationOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_location():
    """Demonstrate LocationOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("LocationOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        locations = project.Location.GetAll(flat=True)
        count = 0
        for location in locations:
            try:
                name = project.Location.GetName(location)
                coords = project.Location.GetCoordinates(location)
                info = f"{name} - Coords: {coords if coords else '(none)'}"
                print(f"   Location: {info}")
            except UnicodeEncodeError:
                print(f"   Location: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Village"
        if not project.Location.Exists(test_name):
            location = project.Location.Create(test_name, alias="DEMO")
            print(f"   Created: {project.Location.GetName(location)}")
        else:
            location = project.Location.Find(test_name)
            print(f"   Location already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        location = project.Location.Find("Demo Village")
        if location:
            print(f"   Found by name: {project.Location.GetName(location)}")
            guid = project.Location.GetGuid(location)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Coordinate operations
    print("\n4. Testing Coordinate operations:")
    try:
        if location:
            # Set coordinates
            project.Location.SetCoordinates(location, -1.2345, -70.6789)
            coords = project.Location.GetCoordinates(location)
            if coords:
                lat, lon = coords
                print(f"   Coordinates: Lat={lat:.4f}, Lon={lon:.4f}")

            # Set elevation
            project.Location.SetElevation(location, 150)
            elevation = project.Location.GetElevation(location)
            print(f"   Elevation: {elevation} meters")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Name and Alias operations
    print("\n5. Testing Name and Alias operations:")
    try:
        if location:
            alias = project.Location.GetAlias(location)
            print(f"   Alias: {alias}")

            project.Location.SetDescription(location, "Demo location for testing")
            desc = project.Location.GetDescription(location)
            print(f"   Description: {desc}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n6. Testing Hierarchy operations:")
    try:
        if location:
            subloc_name = "Demo Sublocation"
            existing_subs = [project.Location.GetName(s)
                           for s in project.Location.GetSublocations(location)]
            if subloc_name not in existing_subs:
                subloc = project.Location.CreateSublocation(
                    location, subloc_name, alias="SUB"
                )
                print(f"   Created sublocation: {project.Location.GetName(subloc)}")

            subs = project.Location.GetSublocations(location)
            print(f"   Sublocations count: {len(subs)}")

            if subs:
                parent = project.Location.GetRegion(subs[0])
                if parent:
                    print(f"   Parent of sublocation: {project.Location.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Query operations
    print("\n7. Testing Query operations (FindByCoordinates):")
    try:
        if location and project.Location.GetCoordinates(location):
            nearby = project.Location.GetNearby(location, radius_km=100)
            print(f"   Locations within 100km: {len(nearby)}")
            if nearby:
                for loc, distance in nearby[:3]:
                    try:
                        name = project.Location.GetName(loc)
                        print(f"     {name}: {distance:.1f} km away")
                    except UnicodeEncodeError:
                        print(f"     [Unicode name]: {distance:.1f} km away")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n8. Testing Metadata operations:")
    try:
        if location:
            created = project.Location.GetDateCreated(location)
            modified = project.Location.GetDateModified(location)
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
    demo_location()
