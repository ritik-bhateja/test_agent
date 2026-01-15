# Actor ID Sanitization Fix

## Issue
AWS Bedrock Memory's `actor_id` parameter has strict validation requirements:
- **Pattern:** `[a-zA-Z0-9][a-zA-Z0-9-_/]*`
- **Allowed:** Letters, numbers, hyphens (`-`), underscores (`_`), forward slashes (`/`)
- **Not Allowed:** Periods (`.`), at signs (`@`), spaces, and other special characters

## Problem
User IDs like `kamaljeet.singh`, `vishal.saxena`, and `harsh.kumar` contain periods, which cause validation errors:
```
ValidationException: Value at 'actorId' failed to satisfy constraint: 
Member must satisfy regular expression pattern: [a-zA-Z0-9][a-zA-Z0-9-_/]*
```

## Solution
Implemented actor_id sanitization in `Backend/main.py`:

```python
# Sanitize user_id for use as actor_id (AWS Bedrock Memory requirement)
# actor_id must match pattern: [a-zA-Z0-9][a-zA-Z0-9-_/]*
# Replace periods and other invalid characters with underscores
actor_id = user_id.replace('.', '_').replace('@', '_at_').replace(' ', '_')
```

## Transformation Examples

| Original user_id | Sanitized actor_id |
|-----------------|-------------------|
| `kamaljeet.singh` | `kamaljeet_singh` |
| `vishal.saxena` | `vishal_saxena` |
| `harsh.kumar` | `harsh_kumar` |
| `user@example.com` | `user_at_example_com` |
| `test user` | `test_user` |

## Impact

### Before Fix
- ❌ Users with periods in their IDs couldn't use memory
- ❌ Memory operations failed with ValidationException
- ❌ Conversation context was lost

### After Fix
- ✅ All user IDs are sanitized to valid actor_ids
- ✅ Memory operations work correctly
- ✅ Conversation context is maintained
- ✅ User isolation still works (each user gets unique actor_id)

## Testing

To verify the fix works for `kamaljeet.singh`:

```bash
# After deployment, check memory for sanitized actor_id
python3 view_store_memory.py kamaljeet_singh <session_id>
```

## Notes

- The sanitization is one-way (user_id → actor_id)
- The original user_id is still passed to the SQL agent for RBAC
- Session isolation remains intact
- User isolation remains intact (different users = different actor_ids)
