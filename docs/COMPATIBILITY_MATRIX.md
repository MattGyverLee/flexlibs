# flexlibs Compatibility Matrix

**Document Version:** 1.0
**Last Updated:** 2025-12-05
**Maintained By:** Programmer Team 1

## Overview

This document tracks version compatibility between flexlibs, FieldWorks Language Explorer (FLEx), the Language and Culture Model (LCM), and Python versions. Understanding these dependencies is critical for:

- **Installation Planning**: Ensuring compatible versions are installed
- **Upgrade Decisions**: Understanding which FLEx versions work with which flexlibs versions
- **Support**: Troubleshooting version-related issues
- **Development**: Targeting the right API versions

---

## Current Release Compatibility

### flexlibs 2.0.0 (Current Release)

**Release Date:** November 24, 2025
**Status:** ✅ Current Stable Release

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| **Python** | 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 | Must match FW architecture (32/64-bit) |
| **FieldWorks (FLEx)** | 9.0.17 - 9.3.1 | Tested with 9.1.x and 9.3.x |
| **Python.NET** | 3.0.3+ | Required dependency |
| **LCM API** | FLEx 9.x series | Compatible with FLEx 9 LCM API |
| **Operating System** | Windows | Primary platform |

**Key Features**:
- 44 Operations classes with 793+ methods
- Complete CRUD operations for all major FLEx data types
- Full backward compatibility with v1.x API
- Organized code structure matching FLEx architecture

**Architecture Requirements**:
- **32-bit FLEx** requires **32-bit Python**
- **64-bit FLEx** requires **64-bit Python**
- Mismatch will result in initialization failure

---

## Version History Matrix

### flexlibs 2.x Series

| flexlibs | Release Date | Python | FLEx | LCM | Status | Notes |
|----------|--------------|--------|------|-----|--------|-------|
| **2.0.0** | 2025-11-24 | 3.8-3.13 | 9.0.17-9.3.1 | FLEx 9.x | ✅ Current | Major release with Operations classes |

### flexlibs 1.x Series

| flexlibs | Release Date | Python | FLEx | LCM | Status | Notes |
|----------|--------------|--------|------|-----|--------|-------|
| **1.2.8** | 2025-09-10 | 3.8-3.13 | 9.0.17-9.3.1 | FLEx 9.x | ⚠️ Legacy | Last 1.x release |
| **1.2.7** | 2025-08-25 | 3.8-3.13 | 9.0.17-9.3.1 | FLEx 9.x | ⚠️ Legacy | Added custom field list support |
| **1.2.6** | 2025-06-26 | 3.8-3.13 | 9.0.17-9.2.8 | FLEx 9.x | ⚠️ Legacy | |
| **1.2.5** | 2025-06-13 | 3.8-3.13 | 9.0.17-9.2.8 | FLEx 9.x | ⚠️ Legacy | Added OpenProjectInFW |
| **1.2.4** | 2024-08-14 | 3.8-3.12 | 9.0.x-9.2.x | FLEx 9.x | ⚠️ Legacy | |

**Legend**:
- ✅ **Current**: Actively maintained, recommended for new projects
- ⚠️ **Legacy**: Still functional but not actively maintained
- ❌ **Deprecated**: No longer supported

---

## LCM API Version Compatibility

The Language and Culture Model (LCM) is the core API used by FLEx. flexlibs interfaces with LCM through Python.NET.

### LCM API Stability

| LCM Component | Stability | Impact on flexlibs |
|---------------|-----------|-------------------|
| **Core Interfaces** (ILexEntry, ILexSense, etc.) | High | Breaking changes rare |
| **Repositories** (ILexEntryRepository, etc.) | High | Stable across versions |
| **Factories** (ILexEntryFactory, etc.) | High | Stable across versions |
| **ITsString / TsStringUtils** | Very High | Critical dependency, very stable |
| **Tags Classes** (LexEntryTags, etc.) | Medium | Field IDs may change |
| **UI Components** | Low | Used minimally in flexlibs |

### Known LCM Changes by FLEx Version

#### FLEx 9.3.x
- **Status**: Fully compatible
- **LCM Changes**: Minor updates, no breaking changes affecting flexlibs
- **Notes**: Latest supported version

#### FLEx 9.2.x
- **Status**: Fully compatible
- **LCM Changes**: No breaking changes
- **Notes**: Stable version

#### FLEx 9.1.x
- **Status**: Fully compatible
- **LCM Changes**: Custom field enhancements
- **Notes**: Widely deployed version

#### FLEx 9.0.17+
- **Status**: Fully compatible
- **LCM Changes**: Baseline version
- **Notes**: Minimum supported version

---

## Python Version Compatibility

### Python 3.13 (Latest)
- **Status**: ✅ Fully Supported
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Newest Python version, fully compatible

### Python 3.12
- **Status**: ✅ Fully Supported
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Recommended for production

### Python 3.11
- **Status**: ✅ Fully Supported
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Good balance of features and stability

### Python 3.10
- **Status**: ✅ Fully Supported
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Stable, widely used

### Python 3.9
- **Status**: ✅ Fully Supported
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Stable

### Python 3.8
- **Status**: ✅ Fully Supported (Minimum)
- **Tested**: Yes
- **Python.NET**: 3.0.3+ required
- **Notes**: Minimum supported version

### Python 3.7 and Earlier
- **Status**: ❌ Not Supported
- **Notes**: Use flexlibs 1.x for Python 3.7 support

---

## Dependency Compatibility

### Required Dependencies

| Dependency | Version | Purpose | Notes |
|------------|---------|---------|-------|
| **Python.NET** | 3.0.3+ | .NET interop | Critical for LCM access |
| **FieldWorks** | 9.0.17-9.3.1 | Core application | Must be installed |

### Optional Dependencies

| Dependency | Version | Purpose | Notes |
|------------|---------|---------|-------|
| **pytest** | Latest | Testing | Development only |
| **sphinx** | Latest | Documentation | Development only |

---

## Platform Compatibility

### Windows
- **Status**: ✅ Primary Platform
- **Versions**: Windows 7+ (Windows 10/11 recommended)
- **Architecture**: 32-bit and 64-bit (must match FLEx)
- **Notes**: Fully supported and tested

### Linux
- **Status**: ⚠️ Experimental
- **Notes**: FLEx runs on Linux via Wine/Mono in some configurations
- **Limitations**: Not officially tested, may have issues with .NET interop
- **Recommendation**: Use Windows for production

### macOS
- **Status**: ❌ Not Supported
- **Notes**: FLEx does not support macOS natively
- **Alternative**: Use Windows VM or Wine (experimental)

---

## Breaking Changes and Migration

### v2.0.0 → Future Versions

**Backward Compatibility Commitment**:
- v2.x series will maintain API compatibility within the major version
- All v2.0.0 code will work in v2.x updates
- Deprecations will be announced in advance

**Potential Future Changes**:
- Python 3.8 support may be dropped in v2.1+
- Additional Operations classes may be added
- New methods may be added to existing Operations classes

### v1.x → v2.0.0

**Status**: ✅ Fully Backward Compatible

**No Breaking Changes**:
- All v1.x API methods remain available
- Existing code works without modification
- New Operations classes are additive

**Migration Recommendations**:
1. Test existing v1.x code with v2.0.0
2. Gradually adopt new Operations classes for new code
3. Consider refactoring to use Operations classes for better maintainability

---

## Testing Matrix

### Tested Configurations

The following configurations have been explicitly tested with flexlibs 2.0.0:

| Python | FLEx | Architecture | Platform | Status |
|--------|------|--------------|----------|--------|
| 3.13 | 9.3.1 | 64-bit | Windows 11 | ✅ Pass |
| 3.12 | 9.3.1 | 64-bit | Windows 11 | ✅ Pass |
| 3.11 | 9.2.8 | 64-bit | Windows 10 | ✅ Pass |
| 3.10 | 9.1.22 | 64-bit | Windows 10 | ✅ Pass |
| 3.9 | 9.1.22 | 32-bit | Windows 10 | ✅ Pass |
| 3.8 | 9.0.17 | 32-bit | Windows 10 | ✅ Pass |

### Recommended Configuration

**Production Use**:
- **Python**: 3.11 or 3.12
- **FLEx**: 9.3.1 (latest stable)
- **Architecture**: 64-bit (if available)
- **Platform**: Windows 10/11

**Development**:
- **Python**: 3.12 or 3.13
- **FLEx**: 9.3.1
- **Architecture**: 64-bit
- **Platform**: Windows 11

---

## Known Issues and Limitations

### Architecture Mismatch
**Issue**: Python architecture must match FLEx architecture
**Symptom**: Initialization failure, DLL load errors
**Solution**: Install matching architecture (32-bit with 32-bit, 64-bit with 64-bit)

### Python.NET Version
**Issue**: Old Python.NET versions may not work
**Symptom**: Import errors, .NET interop failures
**Solution**: Upgrade to Python.NET 3.0.3 or later

### FLEx Version Too Old
**Issue**: FLEx versions before 9.0.17 not supported
**Symptom**: LCM API differences, missing interfaces
**Solution**: Upgrade FLEx to 9.0.17 or later

### Multiple FLEx Installations
**Issue**: Multiple FLEx versions on same machine
**Symptom**: Wrong version loaded, unexpected behavior
**Solution**: Ensure PATH points to correct FLEx installation

---

## Version Determination

### How to Check Your Versions

#### Check flexlibs Version
```python
import flexlibs
print(flexlibs.__version__)  # Expected: "2.0.0"
```

#### Check Python Version
```bash
python --version
# Expected: Python 3.8.x - 3.13.x
```

#### Check Python Architecture
```python
import platform
print(platform.architecture()[0])
# Expected: "32bit" or "64bit"
```

#### Check FLEx Version
1. Open FieldWorks Language Explorer
2. Go to Help → About
3. Check version number (e.g., 9.3.1)

Or programmatically:
```python
import flexlibs
flexlibs.FLExInitialize()
project = flexlibs.FLExProject()
# Check FLEx installation via registry or file system
```

#### Check Python.NET Version
```python
import clr
print(clr.__version__)
# Expected: 3.0.3 or higher
```

---

## Updating This Matrix

### When to Update

Update this compatibility matrix when:

1. **New flexlibs Release**: Add new version row
2. **New FLEx Version Tested**: Update FLEx version range
3. **Python Version Support Changes**: Update Python compatibility
4. **LCM API Changes Detected**: Document in LCM section
5. **Platform Support Changes**: Update platform section

### How to Update

1. **Test New Configuration**:
   ```bash
   pytest flexlibs/tests/
   python -m flexlibs.tests.integration_test
   ```

2. **Document Results**:
   - Add row to version history matrix
   - Update tested configurations
   - Document any breaking changes

3. **Update Version Numbers**:
   - Update "Document Version" at top
   - Update "Last Updated" date
   - Increment document version

4. **Verify LCM Compatibility**:
   - Run API extraction: `python tools/extract_api_usage.py --summary`
   - Check for new LCM interfaces or deprecated ones
   - Update LCM API Compatibility section if needed

### Testing Checklist

Before declaring a version compatible:

- [ ] Install specific Python version
- [ ] Install specific FLEx version
- [ ] Verify architecture match
- [ ] Run unit tests (`pytest`)
- [ ] Run integration tests
- [ ] Test project open/close
- [ ] Test basic CRUD operations
- [ ] Test v1.x API compatibility
- [ ] Test v2.x Operations classes
- [ ] Document any issues or limitations

---

## Support and Troubleshooting

### Getting Help

**For Version Compatibility Issues**:
1. Check this compatibility matrix first
2. Verify your configuration matches a tested configuration
3. Check for architecture mismatch
4. Review error messages for .NET/Python.NET issues

**Common Solutions**:
- **DLL Load Errors**: Architecture mismatch - reinstall matching Python
- **Import Errors**: Python.NET version - upgrade to 3.0.3+
- **LCM Errors**: FLEx version too old - upgrade FLEx
- **Initialization Failures**: Multiple issues - verify entire configuration

### Reporting Compatibility Issues

When reporting a compatibility issue, include:

1. **flexlibs version**: `import flexlibs; print(flexlibs.__version__)`
2. **Python version**: `python --version`
3. **Python architecture**: `import platform; print(platform.architecture())`
4. **FLEx version**: From Help → About
5. **Operating system**: Windows version
6. **Error message**: Full traceback
7. **Configuration**: How FLEx and Python were installed

---

## Future Compatibility Planning

### Upcoming Changes

**Python 3.14 (Expected 2026)**:
- Plan to support upon release
- Will test with pre-release versions
- No anticipated compatibility issues

**FLEx 10.x (Future)**:
- If released, will require compatibility testing
- May require LCM API updates
- Will maintain v2.x branch for FLEx 9.x if needed

**Python 3.8 End-of-Life**:
- Python 3.8 reaches end-of-life in October 2024
- May drop support in flexlibs v2.1 or v3.0
- Will announce deprecation in advance

### Long-Term Support Strategy

- **Current Release (2.0.x)**: Full support
- **Previous Major (1.2.x)**: Security fixes only
- **Older Versions**: No support (upgrade recommended)

---

## Appendix: Version History Details

### Version Numbering Scheme

flexlibs uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Examples:
- `2.0.0` → `2.1.0`: New Operations classes added (backward compatible)
- `2.1.0` → `2.1.1`: Bug fixes
- `2.x.x` → `3.0.0`: Breaking changes (rare)

### Release Cadence

- **Major Releases**: As needed (when breaking changes required)
- **Minor Releases**: 2-4 times per year (new features)
- **Patch Releases**: As needed (bug fixes)

---

## Related Documentation

- **API Surface Documentation**: `docs/API_SURFACE.md`
- **LCM Dependency Matrix**: `docs/LCM_API_DEPENDENCY_MATRIX.md`
- **Change History**: `history.md`
- **Installation Guide**: `README.rst`
- **API Reference**: Generated via Sphinx

---

**Document Version**: 1.0
**Last Updated**: 2025-12-05
**Maintained By**: Programmer Team 1
**Review Cycle**: Update with each release and quarterly
