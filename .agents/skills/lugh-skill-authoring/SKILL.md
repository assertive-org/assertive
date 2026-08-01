---
name: lugh-skill-authoring
description: Maintain this repository's consumer-facing Lugh skills under .lugh/skills. Use when changing or reviewing public APIs, configuration, installation, examples, or recommended package usage.
---

<!-- lugh:producer-skill:start -->
# Maintain Lugh consumer skills

Use this workflow when a change may affect how consumers install, configure, or use this package.

1. Inventory the consumer skills under `.lugh/skills` and identify which ones the change affects.
2. Update affected skills alongside the public behavior they document. Verify APIs and examples against the current source and the repository's applicable tests.
3. Keep guidance consumer-facing. Do not include repository internals, CI or release procedures, test-fixture details, credentials, or private infrastructure.
4. Run the repository checks that apply to changed APIs and examples.
5. Report which consumer skills changed, or explicitly report that no skill change was required and why.
<!-- lugh:producer-skill:end -->
