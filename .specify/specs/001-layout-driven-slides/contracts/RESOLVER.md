# Resolver Contract

## `resolve_deck(data: dict) -> dict`

Takes a validated DeckData dict. Returns a new dict with cross-slide attributes assigned.

### Preconditions
- Input has been validated against the Pydantic model (all layout values are known, required fields present)
- Slides are in display order
- `id` is non-empty for every slide

### Postconditions
- Every slide has `data_id` (str, unique per slide)
- Every slide in a multi-step group (size >= 2) has `auto_animate=true` and matching `auto_animate_group_id`
- Every slide in a single-step group has `auto_animate=false` and `auto_animate_group_id=null`
- Every slide has `element_ids` dict mapping element names to consistent data-id values across steps
- Every slide has `fragment_index` (int, sequential 1..N across entire deck)
- Input dict is never mutated (pure function)

### Algorithm
1. Group slides by `id` → `dict[str, list[SlideRecord]]`
2. For each group:
   - If size >= 2: assign `auto_animate=true`, generate shared `auto_animate_group_id`
   - If size == 1: assign `auto_animate=false`, `auto_animate_group_id=null`
   - Generate `element_ids` from group id + element name
3. For each slide in display order:
   - Generate `data_id` from id + step
   - Assign sequential `fragment_index`
4. Return new dict with resolved fields added

### Edge Cases
- Group of size 1: no auto-animate attributes (`auto_animate=false`, `auto_animate_group_id=null`)
- Group of size 3+: all share the same `auto_animate_group_id`, `element_ids` consistent across all steps
- `raw` layout slides: `fragment_index` and `data_id` assigned. `auto_animate=false`, `auto_animate_group_id=null`, `element_ids={}` (empty — no element matching needed). No auto-animate group participation.
- Empty slides list: return as-is
- Slides with no `id` match: treated as size-1 groups
