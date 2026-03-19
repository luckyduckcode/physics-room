# Manifold Physics Engine: Roadmap (2026)

## Vision
Build a robust, extensible simulation platform for dynamical systems, supporting scientific experiments, educational tools, and game prototyping. Evolve from a research-grade engine to a flexible foundation for interactive physics-based applications.

---

## 1. Core Engine & Taxonomy
### 1.1. Taxonomy Module
- [x] Robust CSV parsing, error handling, and indexing
- [x] Advanced query API (search, filter, group, related)
- [x] CLI for taxonomy exploration and scripting
- [ ] **Edge-case test coverage** (add 5–8 more tests)
- [ ] **Documentation**: API, CLI, and CSV schema

### 1.2. Engine Integration
- [x] Taxonomy in session metadata/events
- [x] HTTP API (FastAPI) exposes taxonomy
- [x] gRPC API parity (taxonomy fields)
- [ ] **Schema/contract tests** for HTTP/gRPC taxonomy fields
- [ ] **Configurable taxonomy source** (CSV, DB, remote)

---

## 2. Scientific Experiment Pipeline
### 2.1. Experiment Matrix Export
- [x] Export utility (CSV/JSON) for experiment conditions
- [x] Notebook-ready output for analysis
- [x] Tests for export correctness
- [ ] **Support for custom experiment schemas**
- [ ] **Batch export and manifest tools**

### 2.2. Analysis & Visualization
- [ ] Example Jupyter notebooks (analysis, plotting)
- [ ] Integration with pandas, matplotlib, seaborn
- [ ] Tutorials for scientific workflows

---

## 3. Game & Interactive Prototyping
### 3.1. Prototype Game
- [ ] Define core loop and success metrics (1-page spec)
- [ ] Implement minimal game prototype (CLI or simple GUI)
- [ ] Integrate engine session/events into gameplay
- [ ] Playtest and iterate (collect feedback)

### 3.2. Engine Extraction
- [ ] Refactor for modularity (engine vs. game code)
- [ ] Plugin system for custom rules/logic
- [ ] Scripting API (Python, possibly Lua)

---

## 4. Usability & Developer Experience
- [ ] Improve CLI UX (help, autocompletion, examples)
- [ ] Add config file support (YAML/TOML)
- [ ] Better error messages and logging
- [ ] Interactive docs (Swagger/OpenAPI, gRPC reflection)
- [ ] VS Code devcontainer and launch configs

---

## 5. Testing & Quality
- [x] Pytest suite for taxonomy, engine, API, experiments
- [ ] 90%+ code coverage (add missing tests)
- [ ] Continuous Integration (GitHub Actions)
- [ ] Linting, type checking (mypy, flake8, black)
- [ ] Fuzz/robustness tests for API and engine

---

## 6. Documentation & Community
- [x] HOW_TO_USE.md, README.md, EXPERIMENT_DESIGN_GUIDE.md
- [ ] API reference (Sphinx or MkDocs)
- [ ] Tutorials and example projects
- [ ] Contribution guide and code of conduct
- [ ] Community Q&A (Discussions, Issues)

---

## 7. Stretch Goals
- [ ] Web-based dashboard (React/FastAPI)
- [ ] Real-time multiplayer support
- [ ] Physics visualization (WebGL, PyGame, or similar)
- [ ] Integration with external data sources (OpenAI Gym, etc.)
- [ ] Export to standard formats (SBML, JSON-LD)

---

## Milestones & Next Steps
1. **Complete edge-case taxonomy tests and schema/contract tests**
2. **Draft prototype game spec and implement minimal version**
3. **Expand experiment export and analysis tools**
4. **Improve documentation and developer onboarding**
5. **Iterate based on user feedback and scientific/game use cases**

---

*This roadmap is a living document. Update as features are completed or priorities shift.*
