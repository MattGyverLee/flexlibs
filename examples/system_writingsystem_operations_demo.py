#!/usr/bin/env python3
"""
Demonstration of WritingSystemOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_writingsystem():
    """Demonstrate WritingSystemOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("WritingSystemOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        writing_systems = project.WritingSystem.GetAll()
        count = 0
        for ws in writing_systems:
            try:
                code = project.WritingSystem.GetCode(ws)
                name = project.WritingSystem.GetName(ws)
                info = f"{code} - {name}"
                print(f"   Writing System: {info}")
            except UnicodeEncodeError:
                print(f"   Writing System: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Analysis vs Vernacular
    print("\n2. Testing Analysis vs Vernacular WS:")
    try:
        analysis_ws = project.WritingSystem.GetAnalysisWritingSystems()
        print(f"   Analysis WS count: {len(analysis_ws)}")
        for i, ws in enumerate(analysis_ws[:3]):
            try:
                code = project.WritingSystem.GetCode(ws)
                print(f"     {i+1}. {code}")
            except:
                pass

        vernacular_ws = project.WritingSystem.GetVernacularWritingSystems()
        print(f"   Vernacular WS count: {len(vernacular_ws)}")
        for i, ws in enumerate(vernacular_ws[:3]):
            try:
                code = project.WritingSystem.GetCode(ws)
                print(f"     {i+1}. {code}")
            except:
                pass
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        # Try to find common writing systems
        for code in ["en", "es", "fr"]:
            ws = project.WritingSystem.Find(code)
            if ws:
                name = project.WritingSystem.GetName(ws)
                print(f"   Found: {code} - {name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        all_ws = project.WritingSystem.GetAll()
        if all_ws:
            ws = all_ws[0]
            code = project.WritingSystem.GetCode(ws)
            name = project.WritingSystem.GetName(ws)
            abbr = project.WritingSystem.GetAbbreviation(ws)

            print(f"   Code: {code}")
            print(f"   Name: {name}")
            print(f"   Abbreviation: {abbr if abbr else '(none)'}")

            # Test direction
            is_rtl = project.WritingSystem.IsRightToLeft(ws)
            print(f"   Is RTL: {is_rtl}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Font operations
    print("\n5. Testing Font operations:")
    try:
        all_ws = project.WritingSystem.GetAll()
        if all_ws:
            ws = all_ws[0]
            font = project.WritingSystem.GetDefaultFont(ws)
            print(f"   Default font: {font if font else '(none)'}")

            font_size = project.WritingSystem.GetDefaultFontSize(ws)
            print(f"   Default font size: {font_size if font_size else '(none)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Locale operations
    print("\n6. Testing Locale operations:")
    try:
        all_ws = project.WritingSystem.GetAll()
        if all_ws:
            ws = all_ws[0]
            locale = project.WritingSystem.GetLocale(ws)
            print(f"   Locale: {locale if locale else '(none)'}")

            language = project.WritingSystem.GetLanguageName(ws)
            print(f"   Language: {language if language else '(none)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Default WS
    print("\n7. Testing Default Writing Systems:")
    try:
        default_anal = project.WritingSystem.GetDefaultAnalysis()
        if default_anal:
            code = project.WritingSystem.GetCode(default_anal)
            print(f"   Default analysis: {code}")

        default_vern = project.WritingSystem.GetDefaultVernacular()
        if default_vern:
            code = project.WritingSystem.GetCode(default_vern)
            print(f"   Default vernacular: {code}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Keyboard operations
    print("\n8. Testing Keyboard operations:")
    try:
        all_ws = project.WritingSystem.GetAll()
        if all_ws:
            ws = all_ws[0]
            keyboard = project.WritingSystem.GetKeyboard(ws)
            print(f"   Keyboard: {keyboard if keyboard else '(none)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_writingsystem()
