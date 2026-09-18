# Release validation

Verification for my AeroOpt application:

- 18 pytest checks passed: request-scoped case selection, malformed JSON, unknown cases, AI-disabled behavior, mocked AI context, invalid regions, static pages, private-file exclusion, and all seven case bundles.
- The configurable VTP processor reproduced both original case-01 region JSON files exactly from the original paired meshes. This checks export consistency, not model accuracy.
- Python compilation and JavaScript syntax checks passed.
- A running local Flask server returned HTTP 200 for the homepage.
- Secret-pattern and file-selection review excluded `.env`, virtual environments, raw meshes, model weights, and personal registration materials.

The tests use a mocked AI provider. No paid model requests were made. The research model, its reported performance, and exact data lineage were not independently reproduced. Browser visual and interaction acceptance remains pending because the available in-app browser blocked the local development URL. GitHub CI passed after the complete application was published: https://github.com/qinyiningpower/aeroopt/actions/runs/35289076073 .
