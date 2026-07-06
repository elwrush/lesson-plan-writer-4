# Constitution

## Article 1 — Propose before build
No feature gets implemented without a proposal. The proposal defines WHAT and WHY before any HOW. A feature without a proposal is a guess.

## Article 2 — Red-green TDD
Every code change MUST have a test that fails (red phase) before the implementation (green phase). Tests that never failed are dead weight.

## Article 3 — Pydantic gate
Every JSON output MUST be validated through a Pydantic `model_validate()` call before being written to disk. Unvalidated data IS bugs.

## Article 4 — Response format for LLM calls
Every LLM call expecting structured output MUST use `response_format={"type": "json_object"}`. Prompt instructions alone are not reliable enough.

## Article 5 — Verify before done
A feature is not complete until `/verify` reports no drift between spec and implementation. Done criteria from the proposal MUST be demonstrably met.

## Article 6 — Brownfield awareness
Before proposing a change, survey what already exists. Prefer extending existing patterns over introducing new ones. Speculative abstraction is waste.

---

**Version:** 1.0  
**Ratified:** 2026-07-05
