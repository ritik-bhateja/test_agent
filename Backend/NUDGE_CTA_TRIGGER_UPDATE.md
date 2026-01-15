# Nudge & CTA Trigger Update

## Summary
Enhanced the nudge and CTA functionality to trigger when users ask about "least" or its synonyms in insurance queries.

## Changes Made

### 1. Updated Nudge Rules Section
**File:** `Backend/agent/prompt.py`

Added explicit trigger rule:
```
⚠️ CRITICAL: When user asks about "least", "minimum", "smallest", "lowest", "minimal" or any synonym → ALWAYS include nudge AND CTA
```

### 2. Expanded "Least Performing" Query Examples
Added comprehensive examples for all synonyms:
- "Show minimum premium agents" → Include nudge
- "Which agent has the smallest sales" → Include nudge
- "Show lowest performing zones" → Include nudge
- "Show minimal revenue regions" → Include nudge

### 3. Updated Trigger Keywords
The system now recognizes these keywords as triggers for nudge + CTA:
- **least** - "Show least performing agents"
- **minimum** - "Show minimum premium agents"
- **smallest** - "Which agent has the smallest sales"
- **lowest** - "Show lowest performing zones"
- **minimal** - "Show minimal revenue regions"
- **worst** - "Show worst performing regions"
- **bottom** - "Show bottom 5 agents"
- **underperforming** - "Show underperforming zones"

## Behavior

When a user asks any insurance query containing these keywords:

1. **Nudge Field**: System will identify 1-4 least performing entities and provide detailed, fact-based analysis
2. **CTA Field**: System will provide specific, actionable recommendations based on the data analysis

## Examples

### Query: "Show agents with minimum premium"
**Response includes:**
- Chart/data showing all agents sorted by premium
- **Nudge**: Detailed analysis of 1-4 lowest premium agents with facts from database
- **CTA**: Specific actions to improve performance of those agents

### Query: "Which zone has the smallest policy count"
**Response includes:**
- Data showing zone with smallest count
- **Nudge**: Comprehensive analysis of underperforming zone(s) with metrics
- **CTA**: Actionable steps to increase policy count in that zone

### Query: "Show lowest performing regions"
**Response includes:**
- Chart/data of all regions by performance
- **Nudge**: Fact-based analysis of 1-4 lowest performing regions
- **CTA**: Specific recommendations for each underperforming region

## Testing

To test this functionality:

1. Start the backend server: `python Backend/Agent_Trigger.py`
2. Use the frontend or API to send queries with trigger keywords
3. Verify that responses include both `nudge` and `cta` fields
4. Confirm that nudge contains detailed facts and CTA contains specific actions

## Notes

- This functionality applies **ONLY to insurance queries** (insurance_db)
- Banking queries (sentra_db) do not include nudge/CTA
- The number of entities in nudge depends on total result count:
  - 1-5 results: 1 entity
  - 6-15 results: 2 entities
  - 16-30 results: 3 entities
  - 31+ results: 4 entities

## Date
December 19, 2025
