# Performance Insight & CTA Formatting Update

## Summary
Enhanced the Performance Insight (nudge) and CTA sections to properly render markdown formatting (bold text with `**text**`) and organize multiple entities into structured, readable cards.

## Problem
The backend was returning nudge and CTA content with markdown bold formatting like:
```
1. **Kanpur Office (BR-60)**: ₹6,073 total premium...
```

But the frontend was displaying it as plain text with the `**` symbols visible, making it look unprofessional and hard to read.

## Solution

### 1. Added Inline Markdown Parser
**File:** `Frontend/src/components/ChatMessage.jsx`

Created a `parseInlineFormatting()` function that:
- Detects `**bold text**` patterns
- Converts them to `<strong>` HTML elements
- Preserves the rest of the text as-is

```javascript
function parseInlineFormatting(text) {
  const boldRegex = /\*\*([^*]+)\*\*/g
  // Replaces **text** with <strong>text</strong>
}
```

### 2. Updated Insight Section
**File:** `Frontend/src/components/ChatMessage.jsx`

Enhanced the insight section to:
- Parse numbered sections (e.g., "1. **Kanpur Office**:")
- Extract entity names from bold text
- Display each entity in a separate card with:
  - Numbered badge (①, ②, ③, etc.)
  - Entity name as header (extracted from bold text)
  - Formatted content with bold text rendered properly

**Before:**
```
💡 Performance Insight
1. **Kanpur Office (BR-60)**: ₹6,073 total premium (82% below average)...
2. **Pimpri-Chinchwad Office (BR-37)**: ₹12,059 total premium...
```

**After:**
```
┌────────────────────────────────────────────┐
│ 💡 Performance Insight                     │
│ Data-driven analysis...                    │
├────────────────────────────────────────────┤
│ ┌──────────────────────────────────────┐  │
│ │ ① Kanpur Office (BR-60)              │  │
│ │ ────────────────────────────────────  │  │
│ │ ₹6,073 total premium (82% below      │  │
│ │ average), worst performing branch... │  │
│ └──────────────────────────────────────┘  │
│                                            │
│ ┌──────────────────────────────────────┐  │
│ │ ② Pimpri-Chinchwad Office (BR-37)    │  │
│ │ ────────────────────────────────────  │  │
│ │ ₹12,059 total premium (64% below...  │  │
│ └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

### 3. Updated CTA Section
**File:** `Frontend/src/components/ChatMessage.jsx`

Applied the same inline formatting to CTA content:
- Bold text is now rendered properly
- Action items are more readable
- Priority levels and metrics stand out

### 4. Added CSS Styling
**File:** `Frontend/src/components/ChatMessage.css`

Added styling for bold text:
```css
.markdown-bold {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
}

/* Amber color for bold text in insight section */
.insight-entity-text .markdown-bold {
  color: #fbbf24;
}

/* Blue color for bold text in CTA section */
.cta-action-text .markdown-bold {
  color: #3b82f6;
}
```

## Visual Comparison

### Before (Plain Text with ** symbols):
```
1. **Kanpur Office (BR-60)**: ₹6,073 total premium (82% below West Zone 
branch average of ₹33,413), worst performing branch. Detailed analysis: 
Single agent Suhani Viswanathan with **Health Secure Group** policy...
```

### After (Formatted with Bold Text):
```
┌──────────────────────────────────────────────────┐
│ ① Kanpur Office (BR-60)                          │
│ ──────────────────────────────────────────────── │
│ ₹6,073 total premium (82% below West Zone branch │
│ average of ₹33,413), worst performing branch.    │
│ Detailed analysis: Single agent Suhani           │
│ Viswanathan with Health Secure Group policy...   │
└──────────────────────────────────────────────────┘
```

Where "Kanpur Office (BR-60)" and "Health Secure Group" appear in bold amber color.

## Key Features

1. **Automatic Entity Detection**: Detects numbered sections starting with `\d+\. \*\*`
2. **Entity Name Extraction**: Extracts text between `**` as the entity name
3. **Bold Text Rendering**: Converts all `**text**` to properly styled bold text
4. **Color Coding**: 
   - Insight section: Amber (#fbbf24) for bold text
   - CTA section: Blue (#3b82f6) for bold text
5. **Structured Layout**: Each entity gets its own card with header and content
6. **Responsive Design**: Works on mobile and desktop

## Technical Details

### Regex Pattern for Entity Detection
```javascript
/^\d+\.\s+\*\*/  // Matches "1. **" at start of line
```

### Regex Pattern for Entity Name Extraction
```javascript
/^\d+\.\s+\*\*([^*]+)\*\*/  // Captures text between ** **
```

### Regex Pattern for Bold Text
```javascript
/\*\*([^*]+)\*\*/g  // Matches **text** globally
```

## Testing

To test the formatting:

1. Start backend: `python Backend/Agent_Trigger.py`
2. Start frontend: `npm run dev` (in Frontend directory)
3. Send query: "Show branches with minimum premium in West Zone"
4. Verify:
   - Bold text renders without `**` symbols
   - Entity names appear in card headers
   - Content is properly formatted
   - Colors match the design (amber for insight, blue for CTA)

## Benefits

1. **Professional Appearance**: No more visible `**` symbols
2. **Better Readability**: Bold text stands out appropriately
3. **Structured Layout**: Multiple entities are clearly separated
4. **Visual Hierarchy**: Entity names, numbers, and content are distinct
5. **Consistent Design**: Matches the overall UI aesthetic
6. **Maintainable**: Uses simple regex patterns that are easy to understand

## Related Files

- `Frontend/src/components/ChatMessage.jsx` - Component logic
- `Frontend/src/components/ChatMessage.css` - Styling
- `Frontend/src/utils/markdownParser.jsx` - Markdown utilities (reference)
- `Backend/agent/prompt.py` - Nudge/CTA content generation

## Date
December 19, 2025
