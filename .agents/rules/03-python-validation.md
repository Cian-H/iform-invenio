---
description: "Strict LSP and syntax validation rules."
globs: ["**/*.py"]
alwaysApply: false
---

# Python Validation & Editing Rules

- **Mandatory Planning:** Before modifying any files, you must outline the files
  you intend to touch.
- **LSP Checking:** After editing or removing boilerplate, you MUST query the
  LSP server (e.g., ruff) to check for broken references, undefined variables,
  or unused imports.
- **Zero Warnings:** The file is not considered "clean" until the LSP returns
  zero warnings for the section you modified.
- **Revert on Failure:** If your cleanup causes cascading errors in other files,
  revert your change and ask the user how they want to proceed.
