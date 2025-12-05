# Upstream LibLCM Compatibility Monitoring

This directory contains configuration and tracking data for monitoring compatibility with the upstream [sillsdev/liblcm](https://github.com/sillsdev/liblcm) repository.

## Overview

FlexLibs uses a **three-tier testing strategy** to ensure compatibility with upstream LibLCM:

1. **Local Compatibility Check** (`local-compat-check.yml`) - Fast smoke tests on every commit
2. **API Monitor** (`upstream-api-monitor.yml`) - Daily monitoring of upstream API changes
3. **Full Compatibility Check** (`upstream-compatibility-check.yml`) - Weekly full testing with FLEx

## Three-Tier Testing Strategy

### Tier 1: Local Compatibility Check
**When:** Every push and pull request
**Duration:** ~2 minutes
**Requirements:** None (runs on standard GitHub runners)
**Purpose:** Quick feedback on code quality and structure

This lightweight workflow performs smoke tests without requiring FLEx:
- ✓ Validates Python syntax in all files
- ✓ Verifies Operations class structure
- ✓ Checks that critical methods exist
- ✓ Analyzes SIL.LCModel API usage patterns
- ✓ Ensures expected API surface is maintained

**Workflow:** [`.github/workflows/local-compat-check.yml`](../workflows/local-compat-check.yml)

### Tier 2: Upstream API Monitor
**When:** Daily at 2 AM UTC (or on-demand)
**Duration:** ~5 minutes
**Requirements:** None (runs on Ubuntu)
**Purpose:** Early detection of upstream changes

This workflow monitors the upstream repository for API changes:
- 📊 Tracks recent commits to liblcm
- 🔍 Performs deep API analysis comparing flexlibs usage with latest liblcm
- 🎯 Identifies which flexlibs-used classes exist in latest liblcm
- ⚠️ Detects potential breaking changes in commit messages
- 📝 Generates detailed monitoring reports
- 🚨 Creates issues for potential breaking changes

**Workflow:** [`.github/workflows/upstream-api-monitor.yml`](../workflows/upstream-api-monitor.yml)

### Tier 3: Full Compatibility Check
**When:** Weekly on Monday at 9 AM UTC (or on-demand)
**Duration:** ~30 minutes
**Requirements:** Self-hosted Windows runner with FLEx installed
**Purpose:** Full integration testing

This workflow runs the complete test suite against actual FLEx installation:
- 🧪 Runs full pytest test suite
- 🔧 Tests against latest upstream liblcm commit
- 📌 Tracks last known working commit
- 🐛 Creates issues when tests fail
- 💾 Commits successful test results

**Workflow:** [`.github/workflows/upstream-compatibility-check.yml`](../workflows/upstream-compatibility-check.yml)

## Workflow Triggers

### Local Compatibility Check
**Automatic:**
- Every push to main, develop, or feature branches
- Every pull request to main or develop

**Manual:**
- Can be triggered from GitHub Actions tab

### Upstream API Monitor
**Automatic:**
- Daily at 2 AM UTC

**Manual (workflow_dispatch):**
- **liblcm_ref**: Which commit/branch/tag to analyze (default: `master`)

### Full Compatibility Check
**Automatic:**
- Weekly on Monday at 9 AM UTC

**Manual (workflow_dispatch):**
- **liblcm_branch**: Which branch of liblcm to test against (default: `master`)
- **fieldworks_version**: Specific FLEx version to test (default: `latest`)
- **create_issue_on_failure**: Whether to create an issue on failure (default: `true`)

## Files in This Directory

- **`last-working-commit.txt`**: Contains the SHA of the last upstream liblcm commit that passed all tests
- **`README.md`**: This file, documenting the compatibility monitoring system

## Interpreting Results

### When Tests Pass ✅
- The workflow updates `last-working-commit.txt` with the latest upstream commit SHA
- No action needed - flexlibs is compatible with the latest upstream

### When Tests Fail ❌
- An issue is created with the label `upstream-breaking-change`
- The issue includes:
  - Link to the problematic upstream commit
  - Link to compare changes since last working version
  - Test environment details
  - Link to detailed test logs

## Responding to Breaking Changes

When a breaking change is detected:

1. **Review the upstream commit**: Check what changed in liblcm
2. **Examine the test failures**: Look at the workflow logs to see which tests failed
3. **Determine the cause**:
   - Is it a true API breaking change in liblcm?
   - Is it a new FieldWorks version requirement?
   - Is it a test environment issue?
4. **Update flexlibs** if needed:
   - Adapt to new liblcm API changes
   - Update version requirements
   - Fix any compatibility issues
5. **Update documentation**: Note any new requirements or breaking changes
6. **Close the issue** once resolved

## Self-Hosted Runner Setup

The **Full Compatibility Check** workflow requires a self-hosted Windows runner with FieldWorks pre-installed. This is necessary because:

1. FieldWorks is a large Windows application (~500MB+)
2. Installation requires Windows registry configuration
3. .NET Framework and specific dependencies are required
4. GitHub-hosted runners don't have FLEx pre-installed

### Setting Up a Self-Hosted Runner

#### Requirements
- Windows 10/11 or Windows Server 2019/2022
- .NET Framework 4.8 or higher
- FieldWorks 9.x or 10.x installed
- Stable internet connection
- At least 8GB RAM, 50GB free disk space

#### Step 1: Install FieldWorks
1. Download the latest FieldWorks installer from [software.sil.org/fieldworks](https://software.sil.org/fieldworks/download/)
2. Run the installer with full installation options
3. Verify FLEx launches successfully
4. Note the installation path (typically `C:\Program Files\SIL\FieldWorks 9`)

#### Step 2: Install GitHub Actions Runner
1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **Runners**
3. Click **"New self-hosted runner"**
4. Select **Windows** as the OS
5. Follow the provided download and configuration commands:

```powershell
# Create a folder for the runner
mkdir actions-runner ; cd actions-runner

# Download the latest runner package
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner-win-x64-2.311.0.zip

# Extract the installer
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/actions-runner-win-x64-2.311.0.zip", "$PWD")

# Create the runner and start the configuration
./config.cmd --url https://github.com/YOUR-ORG/flexlibs --token YOUR-TOKEN

# When prompted for labels, enter: windows,fieldworks
```

#### Step 3: Configure Runner Labels
When configuring the runner, add these labels:
- `self-hosted` (automatically added)
- `windows` (recommended)
- `fieldworks` (required - this is what the workflow looks for)

#### Step 4: Install Python
The runner needs Python for running tests:

```powershell
# Install Python 3.11 (or use Chocolatey/winget)
winget install Python.Python.3.11

# Verify installation
python --version

# Install Python 3.8 and 3.13 for matrix testing (optional)
winget install Python.Python.3.8
winget install Python.Python.3.13
```

#### Step 5: Run the Runner as a Service
For continuous availability, install the runner as a Windows service:

```powershell
# In the actions-runner directory, run:
./svc.sh install

# Start the service
./svc.sh start

# Check status
./svc.sh status
```

Alternatively, run interactively (for testing):
```powershell
./run.cmd
```

#### Step 6: Verify Setup
1. The runner should appear as "Idle" in GitHub Settings → Actions → Runners
2. Trigger the workflow manually to test
3. Check that the "Verify FLEx installation" step passes

### Runner Maintenance

#### Updating the Runner
```powershell
# Stop the service
./svc.sh stop

# Remove the service
./svc.sh uninstall

# Download and extract new version
# (follow download steps above)

# Reinstall service
./svc.sh install
./svc.sh start
```

#### Updating FieldWorks
1. Stop the runner service
2. Update FieldWorks through normal update process
3. Verify FLEx still launches correctly
4. Restart the runner service

#### Monitoring
- Check runner status regularly in GitHub Settings
- Monitor disk space (test artifacts can accumulate)
- Review workflow logs for FLEx version mismatches
- Set up Windows Event Viewer alerts for service failures

### Security Considerations
- ⚠️ **Self-hosted runners should only be used for public repositories you trust**
- Consider using a dedicated VM or machine for the runner
- Keep Windows and FLEx updated for security patches
- Don't store sensitive data on the runner machine
- Use Windows Firewall to restrict network access
- Review GitHub's [self-hosted runner security guide](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#self-hosted-runner-security)

### Troubleshooting

#### Runner Not Appearing
- Check Windows Firewall settings
- Verify internet connectivity
- Check GitHub token hasn't expired
- Review runner service logs in Event Viewer

#### FLEx Not Found
- Verify installation path matches expected locations
- Check that FieldWorks.exe exists and is executable
- Ensure .NET Framework dependencies are met
- Review "Verify FLEx installation" step output

#### Tests Failing
- Check Python version compatibility
- Verify all pip dependencies installed
- Check FLEx version matches liblcm version
- Review detailed test logs in workflow output

#### Performance Issues
- Ensure sufficient RAM available
- Check disk space
- Monitor CPU usage during test runs
- Consider SSD for faster I/O

## Configuration

### Adjusting Schedule
Edit the cron expression in the workflow file:
```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday at 9 AM UTC
```

Common schedules:
- Daily: `'0 9 * * *'`
- Twice weekly: `'0 9 * * 1,4'` (Monday and Thursday)
- Monthly: `'0 9 1 * *'` (1st of each month)

### Testing Multiple Versions
Expand the matrix strategy in the workflow:
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.11', '3.13']
    flex-version: ['9.1', '9.2', '9.3']
```

## Benefits of the Three-Tier Strategy

### Fast Feedback Loop
- **Tier 1** provides feedback in ~2 minutes on every commit
- Developers get immediate validation without waiting for FLEx tests
- Catches syntax errors and structural issues early

### Resource Efficiency
- **Tier 1** runs on free GitHub-hosted runners
- **Tier 2** uses minimal resources (Ubuntu, no FLEx)
- **Tier 3** only runs weekly, minimizing self-hosted runner usage

### Comprehensive Coverage
- **Tier 1** validates code structure and API patterns
- **Tier 2** monitors upstream for API changes before they affect us
- **Tier 3** confirms full integration with actual FLEx installation

### Early Warning System
- **Tier 2** detects upstream changes within 24 hours
- Issues created proactively before breaking changes reach releases
- Time to investigate and plan updates

### Development Workflow
1. Developer pushes code → **Tier 1** runs immediately
2. Code merged → **Tier 2** continues daily monitoring
3. Weekly → **Tier 3** validates full compatibility
4. Issues created only when necessary

## Limitations

1. **Self-Hosted Runner**: Tier 3 requires a self-hosted Windows runner with FLEx
2. **Windows Only**: Full tests require Windows (FieldWorks limitation)
3. **Test Coverage**: Only catches breaks that existing tests cover
4. **FLEx Version**: Tests against installed FLEx version (may not be absolute latest)
5. **Resource Usage**:
   - Tier 1: Uses GitHub Actions minutes (unlimited for public repos)
   - Tier 2: Minimal GitHub Actions usage
   - Tier 3: Requires self-hosted infrastructure

## Future Enhancements

### Tier 1 (Local Tests)
- Add mock testing for key Operations classes
- Validate docstring coverage
- Check for proper type hints
- Lint checks (flake8, mypy)

### Tier 2 (API Monitor)
- Email/Slack notifications for breaking changes
- Compare API surface over time (trend analysis)
- Track deprecation warnings
- Integration with upstream release notes
- Automated bisection to find exact breaking commit

### Tier 3 (Full Compatibility)
- Test against multiple FLEx versions simultaneously
- Generate compatibility matrix
- Performance regression detection
- Automated test expansion based on API usage
- Docker container option for easier runner setup

### Cross-Tier
- Dashboard showing all three tiers status
- Correlation of Tier 2 warnings with Tier 3 failures
- Automated PR creation to fix compatibility issues
- Integration with external CI/CD systems
