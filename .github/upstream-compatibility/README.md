# Upstream LibLCM Compatibility Monitoring

This directory contains configuration and tracking data for monitoring compatibility with the upstream [sillsdev/liblcm](https://github.com/sillsdev/liblcm) repository.

## Overview

The GitHub Actions workflow in [`.github/workflows/upstream-compatibility-check.yml`](../workflows/upstream-compatibility-check.yml) automatically monitors the upstream liblcm repository for breaking changes that could affect flexlibs.

## How It Works

1. **Scheduled Checks**: The workflow runs weekly (every Monday at 9 AM UTC) to check for new upstream commits
2. **Test Execution**: Runs the flexlibs test suite against the latest upstream liblcm version
3. **Result Tracking**: Records the last known working upstream commit in `last-working-commit.txt`
4. **Issue Creation**: Automatically creates a GitHub issue when breaking changes are detected
5. **Manual Triggers**: Can be run on-demand to test specific upstream branches or FieldWorks versions

## Workflow Triggers

### Automatic (Scheduled)
- Runs every Monday at 9 AM UTC
- Tests against the latest `master` branch of sillsdev/liblcm
- Creates issues automatically on failures

### Manual (workflow_dispatch)
You can manually trigger the workflow from the GitHub Actions tab with these options:
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

## FieldWorks Installation Challenge

**Note**: The current workflow has a placeholder for FieldWorks installation. This is a significant challenge because:

1. FieldWorks is a large Windows application
2. Silent installation may require specific flags/configuration
3. May need to be pre-installed on a custom GitHub runner
4. Alternative: Use a Docker container with FieldWorks pre-installed

### Possible Solutions

1. **Custom GitHub Runner**: Set up a self-hosted runner with FieldWorks pre-installed
2. **Cached Installation**: Cache the FieldWorks installation between workflow runs
3. **Docker Container**: Create a Docker image with FieldWorks for testing
4. **Mock Testing**: Create mock tests that don't require full FieldWorks installation (limited value)

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

## Benefits

1. **Early Detection**: Catch breaking changes before they impact users
2. **Automated Monitoring**: No manual checking required
3. **Historical Tracking**: Know exactly when compatibility broke
4. **Documentation**: Issues provide a record of upstream changes
5. **Proactive Maintenance**: Stay ahead of compatibility issues

## Limitations

1. **FieldWorks Installation**: Currently requires implementation of automated installation
2. **Windows Only**: FieldWorks is primarily a Windows application
3. **Test Coverage**: Only catches breaks that existing tests cover
4. **Resource Usage**: Uses GitHub Actions minutes (free tier: 2000 min/month for private repos, unlimited for public)

## Future Enhancements

- Implement automated FieldWorks installation
- Add notification via email/Slack when breaking changes detected
- Test against multiple FieldWorks versions simultaneously
- Generate compatibility matrix showing which upstream versions work
- Add performance regression detection
- Integration with upstream release notes/changelog
- Bisect to find exact breaking commit if multiple commits since last test
