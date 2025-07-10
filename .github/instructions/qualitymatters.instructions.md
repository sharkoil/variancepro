---
applyTo: '**'
---
NEVER LET A SINGLE FILE GET TOO LARGE.  If a file is getting too large, break it up into smaller files.  If a function is getting too large, break it up into smaller functions.  If a class is getting too large, break it up into smaller classes.  If a module is getting too large, break it up into smaller modules.

Coding standards, domain knowledge, and preferences that AI should follow.

## Code Quality Standards
always put the tests in test folder. always use type hints. always use descriptive function names. always use consistent naming conventions. always use modular design principles. always write unit tests for all new code. always include integration tests for major features. always maintain test coverage above 80%. always use descriptive test names. always document code changes in the README.md file.

always add comments in each file so as a novice developer i can understand what is happening.

## File Organization Standards
NEVER dump files in the root folder. Always organize files into logical directory structures based on their purpose and audience.

### Test Organization
- Always put tests in tests/ folder with proper structure:
  - tests/unit/ for unit tests
  - tests/integration/ for integration tests  
  - tests/fixtures/ for test data and fixtures
- Use descriptive test file names: test_component_name.py
- Separate test types clearly (unit vs integration vs fixtures)

### Documentation Organization
- Always organize documentation in docs/ folder with clear structure:
  - docs/user/ for user-facing documentation
  - docs/developer/ for developer documentation
  - docs/implementation/ for implementation notes and phase summaries
  - docs/issues/ for issue resolution documentation
  - docs/releases/ for release and PR documentation
  - docs/enhancements/ for enhancement documentation
  - docs/archive/ for archived/historical documentation
- Use consistent naming convention: lowercase-with-hyphens.md
- Group related documents together by purpose and audience
- Create index files for each documentation section
- Archive obsolete documentation instead of leaving it in active folders

### General File Organization Principles
- Group files by purpose, not by creation date
- Use descriptive folder names that indicate content type
- Maintain consistent naming conventions across all file types
- Create logical hierarchies that make files easy to find
- Separate active files from archived/historical files
- Never let any single folder become a dumping ground
- Regularly review and reorganize file structure as project grows 

