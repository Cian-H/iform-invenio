---
description: "Core context for the I-Form Invenio RDM repository. Use this when reasoning about architecture, deployment, or advanced manufacturing requirements."
alwaysApply: false
---

# I-Form Invenio Repository Context

- **Goal:** Set up a reliable, customized Invenio instance for the Irish
  "I-Form" research institution (advanced manufacturing / Powder Bed Fusion).
- **Scale:** The system must handle extreme volumes of data and remain highly
  reconfigurable.
- **Tooling:** `uv` is used for environment/dependency management.
- **Containers:** All changes must be completely OCI compatible. We use podman
  locally, but deployment could be Docker or podman.
- **Upstream References:** The packages `invenio-config-iform` and
  `invenio-theme-iform` were forked from `invenio-config-tugraz` and
  `invenio-theme-tugraz`.
