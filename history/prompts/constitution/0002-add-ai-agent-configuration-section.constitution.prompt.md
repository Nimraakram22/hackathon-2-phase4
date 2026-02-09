---
id: 0002
title: Add AI Agent Configuration Section
stage: constitution
date: 2026-01-28
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: habib
command: /sp.constitution
labels: ["constitution", "amendment", "ai-agents", "llm-configuration", "cost-optimization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none (documentation artifact)
---

## Prompt

User requested to update the constitution with a new section on AI Agent Configuration for the OpenAI Agents SDK.

**Requirement**: Add guidance for configuring agents to use free LLM providers (Google Gemini) instead of paid OpenAI models.

**Configuration Levels Provided**:
1. **Agent Level** (PREFERRED) - Per-agent configuration for optimal model selection
2. **Run Level** - Per-execution configuration for runtime switching
3. **Global Level** - Application-wide configuration for simple cases

**Code Examples**: User provided complete working examples for all three configuration approaches using Google Gemini 2.0 Flash via OpenAI-compatible API.

**Key Requirements**:
- Mandate Agent Level configuration as the default approach
- Support per-agent model selection for optimal performance
- Use free models (gemini-2.0-flash) to reduce operational costs
- Load API keys from environment variables (never hardcode)
- Document model selection rationale in code comments

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 (MINOR version bump).

**Added Section**: "AI Agent Configuration" under Technology Standards

**Content Added**:
- Rationale for using free LLM providers (cost reduction while maintaining functionality)
- Three configuration levels with complete code examples
- Mandatory requirement to use Agent Level configuration
- Enforcement rules: API keys from env vars, document model selection, test with free models first
- Recommended models: gemini-2.0-flash (primary), gemini-1.5-flash (fallback), gemini-2.0-flash-thinking-exp (complex reasoning)

**Code Examples Included**:
1. Agent Level configuration (PREFERRED) - 25 lines with AsyncOpenAI client setup
2. Run Level configuration (alternative) - 20 lines with RunConfig
3. Global Level configuration (simple apps only) - 18 lines with global client setup

**Version Bump Rationale**: MINOR (1.0.0 → 1.1.0) because this adds a new section and guidance without breaking existing principles or removing content. This is an enhancement that expands the Technology Standards section.

**Sync Impact Report Updated**: Documented the amendment with change type, rationale, and template status verification.

## Outcome

- ✅ Impact: Added mandatory AI agent configuration guidance to ensure cost-effective LLM usage across all agents in the project
- 🧪 Tests: N/A (documentation artifact, no code tests required)
- 📁 Files: Updated `.specify/memory/constitution.md` (v1.0.0 → v1.1.0, added ~130 lines for AI Agent Configuration section)
- 🔁 Next prompts: `/sp.specify` to create feature specification, ensuring agent implementations follow the new configuration requirements
- 🧠 Reflection: Amendment successfully adds actionable guidance with three configuration approaches and clear preference for Agent Level configuration. Code examples are complete and production-ready with proper error handling considerations.

## Evaluation notes (flywheel)

- Failure modes observed: None - amendment applied cleanly with proper version bump
- Graders run and results (PASS/FAIL):
  - ✅ PASS: Version bumped correctly (1.0.0 → 1.1.0 MINOR)
  - ✅ PASS: Sync Impact Report updated with amendment rationale
  - ✅ PASS: Code examples are complete and syntactically correct
  - ✅ PASS: Enforcement rules clearly stated
  - ✅ PASS: Dates updated (Last Amended: 2026-01-28)
  - ✅ PASS: No unresolved placeholders
- Prompt variant (if applicable): Constitution amendment workflow
- Next experiment (smallest change to try): Validate that agent implementations in `/sp.plan` phase reference this configuration section and use Agent Level setup
