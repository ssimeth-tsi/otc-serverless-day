# PR Pipeline Test

This document is created to test the PR preview deployment pipeline.

## Features being tested:
- Automatic deployment on PR creation
- Performance testing against deployed endpoints
- PR comment with performance results
- Terraform workspace isolation
- Cleanup on PR close

## Expected behavior:
1. PR created → Preview environment deployed
2. Performance tests run automatically
3. Results posted as PR comment
4. Environment destroyed when PR is closed

Test timestamp: $(date)