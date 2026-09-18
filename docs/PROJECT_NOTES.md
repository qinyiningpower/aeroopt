# My AeroOpt implementation

## What I built

I developed AeroOpt end to end for the MBTMY Vibathon 2026 AI Defined Vehicle competition. I built the browser frontend, Flask backend, result-processing pipeline, and AI assistant integration. I connected precomputed research outputs to interactive visualization and AI-assisted interpretation across seven vehicle cases. My separate research model is not included in this repository.

## Implementation

- I built the vehicle-selection and comparison interface for geometry, pressure, and drag results.
- I developed the Flask APIs and case loader that serve result data to the frontend.
- I processed paired geometry and pressure outputs into front, roof, side, and rear summaries.
- I integrated the AI assistant with case data and specialized prompts for shape, pressure, and drag explanations.
- I connected the frontend, backend, and AI workflow so that users can inspect results and ask case-specific questions.

## Engineering details

The application uses same-origin hosting, configurable credentials, browsing without an API key, request-scoped case selection, input validation, and safe text rendering. A configurable postprocessing CLI converts paired VTP meshes into regional JSON summaries. Automated checks cover the API and case artifacts.

## Project introduction

> **AeroOpt — Automotive Aerodynamics Analysis and AI Assistant**
> I built an end-to-end vehicle aerodynamics prototype for MBTMY Vibathon 2026, integrating a browser frontend, Flask APIs, regional geometry and pressure processing, and an AI assistant. I connected seven precomputed vehicle cases to interactive comparisons and case-grounded explanations.

## My technical walkthrough

1. **Problem:** I wanted to make research model outputs easier to inspect, compare, and interpret.
2. **Architecture:** I separated expensive scientific computation from the application, which consumes lightweight saved results.
3. **Data flow:** I summarize paired meshes into regions, expose the results through Flask, and display comparisons with optional AI interpretation.
4. **Tradeoff:** I use precomputed cases so the application can run without a GPU, with exploration limited to saved scenarios.
5. **Reliability:** Explicit case IDs keep requests isolated; recorded results remain available without an AI API key.
6. **Scientific scope:** The exported demo values and AI explanations do not substitute for a reproducible model evaluation or CFD validation.

## External research and data

I keep the research model separate from this application. I use the DrivAerNet collection hosted on Harvard Dataverse; the exact release, dataset DOI, and sample mapping remain to be documented. The competition guide is background material and is not distributed in this repository.
