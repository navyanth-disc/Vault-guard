---
name: project-brain-setup
description: >-
  Sets up the 5-layer AI Agent Brain (.agents/ directory) in any new project.
  Use this whenever starting a new project, onboarding a new codebase, or when
  the user asks for agent memory, knowledge persistence, or project documentation structure.
---

# Project Brain Setup Skill

This skill creates the complete 5-layer Agent Brain system that gives AI agents
persistent memory across sessions. Without this, every new conversation starts
from zero.

## The 5 Layers

```
.agents/
├── AGENTS.md              ← Layer 1: Rules (behavioral constraints)
├── STATE.md               ← Layer 2: State (current architecture snapshot)
├── CHANGELOG.md           ← Layer 3: History (timestamped action log)
├── skills/                ← Layer 4: Skills (procedural "how to" memory)
│   └── <skill-name>/
│       └── SKILL.md
├── walkthroughs/          ← Layer 5: Knowledge (deep "why" explanations)
│   └── phase<N>_<name>.md
└── rules/                 ← Persistent /learn rules
    └── <rule-name>.md
```

## Instructions

### Step 1: Create the Directory Structure

Create all directories and placeholder files:

```bash
mkdir -p .agents/skills .agents/walkthroughs .agents/rules
```

### Step 2: Create AGENTS.md (Layer 1 — Rules)

This is the most important file. It contains:
- Project identity (name, language, workspace root)
- Environment rules (venv path, interpreter selection)
- Code style rules (type hints, line length, docstrings)
- Known bugs and lessons learned
- References to STATE.md and CHANGELOG.md

**Template structure:**
```markdown
# Project Rules

## Project Identity
- Project: <name>
- Language: <language> <version>

## Environment Rules
- Virtual environment: ./venv/
- Package manager: pip / npm / etc.

## Code Style Rules
- <list project conventions>

## Known Bugs & Lessons
- <append as they're discovered>
```

### Step 3: Create STATE.md (Layer 2 — State)

Write a plain English description of the project's current architecture.
Any agent from anywhere should read this and instantly understand:
- What the project does
- What technologies it uses
- What's been built so far
- What's planned next

**Rule**: Update STATE.md whenever a fundamental architectural change is made.

### Step 4: Create CHANGELOG.md (Layer 3 — History)

Start with:
```markdown
# Project Changelog

Changes are appended with timestamp format: `dd/mm/yyyy HH:MM`.

---

**<today's date>**
- Initialized project brain (.agents/ directory).
```

**Rule**: Every agent MUST append to this before completing a task.

### Step 5: Create Skills (Layer 4 — Procedural Memory)

Skills are created as needed using `/learn` or manually. Each skill needs:
- A `SKILL.md` with YAML frontmatter (name, description)
- Optional: `scripts/`, `examples/`, `resources/`, `references/`

### Step 6: Create Walkthroughs (Layer 5 — Deep Knowledge)

After completing any significant phase/milestone, create a walkthrough at:
```
.agents/walkthroughs/phase<N>_<short_name>.md
```

**The Symmetry Rule**: No completed phase should lack a walkthrough. If Phase 2
has a deep dive but Phase 1 doesn't, the brain is asymmetric.

## Why This Matters

| Without Brain | With Brain |
|---|---|
| Every session starts from zero | Every session starts with full context |
| Agent forgets what was done | CHANGELOG tracks all actions |
| Agent doesn't know architecture | STATE.md explains everything |
| Agent repeats mistakes | Known bugs are documented |
| Deep knowledge is lost | Walkthroughs preserve the "why" |
