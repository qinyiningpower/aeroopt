# Project notes and interview preparation

## Ownership

The owner confirmed their role as **Team Leader & Backend Developer**: leading the competition team and handling backend development. The supplied folder includes team application materials: a browser frontend, Flask AI service, case exports, and region-generation scripts. Individual authorship of each module has not yet been established. The separate research model is not included.

## Original work represented by the supplied materials

- Paired geometry/pressure result processing into front, roof, side, and rear summaries.
- A Flask interface serving cases and region summaries.
- AI prompts grounded in case data, including specialized shape, pressure, and drag explanations.
- A browser experience connecting vehicle selection, saved visualizations, and AI interaction.

## Publication improvements

This portfolio edition adds same-origin hosting, configurable credentials, a no-key browsing path, request-local case handling, safer AI text rendering, input checks, a configurable postprocessing CLI, automated checks, and English documentation. These changes were made while preparing the repository for publication and should not be described as historical competition deliverables.

## Resume wording

The confirmed role is Team Leader & Backend Developer. The following wording keeps leadership and technical responsibilities distinct:

> **AeroOpt — MBTMY Vibathon 2026, AI Defined Vehicle | Team Leader & Backend Developer**
> Led the competition team and developed the backend integration for a vehicle aerodynamics prototype, connecting precomputed research outputs to interactive visualization and AI-assisted interpretation. Structured regional geometry and pressure summaries for a Flask API supporting seven vehicle case exports.

Do not add awards, deployment scale, response-time gains, model accuracy, or validated drag-reduction percentages without evidence. Do not describe all frontend or AI code as your sole work.

## Interview walkthrough

1. **Problem:** research model outputs are difficult to inspect directly; an engineer needs a clear way to compare cases and ask focused questions.
2. **Boundary:** expensive scientific computation runs separately; the application consumes a stable, lightweight result contract.
3. **Implementation:** paired meshes are summarized into regions, loaded by Flask, and rendered as comparative views with optional AI interpretation.
4. **Tradeoff:** precomputed cases make the application easy to run without a GPU, while limiting it to saved scenarios.
5. **Reliability:** explicit request case IDs prevent cross-user state leakage; no API key is needed for recorded results.
6. **Scientific limits:** rounded export values and AI explanations cannot substitute for a reproducible evaluation or CFD validation.

## Information to complete later

The owner confirmed that `Vibathon26AIDVStudentGuide.pdf` is the slide deck distributed for the competition. It identifies Mercedes-Benz Tech Malaysia, MBTMY Vibathon 2026, and the AI Defined Vehicle category. The deck is used as background evidence and is not included in the repository. Exact event dates, team attribution, repository-specific authorship, research model architecture/paper link, and the dataset DOI/sample mapping should be added when confirmed by the owner. These omissions do not prevent demonstrating the application but limit historical and scientific claims.
