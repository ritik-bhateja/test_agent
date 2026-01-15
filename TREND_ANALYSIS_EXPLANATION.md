# How Trend Analysis Works in Sentra

## Overview

Trend Analysis is an **automatic, client-side feature** in the Sentra Banking & Insurance chatbot that provides intelligent insights on chart data. It analyzes patterns in the data and provides actionable suggestions without requiring any backend processing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Agent)                          │
│  - Generates SQL query                                      │
│  - Executes query on Athena                                 │
│  - Returns raw data + chart type                            │
│  - NO trend calculation here                                │
└────────────────┬────────────────────────────────────────────┘
                 │ JSON Response
                 │ {type: "bar", data: [...], explanation: "..."}
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ChatMessage.jsx                                     │  │
│  │  - Receives response                                 │  │
│  │  - Detects chart data (Array)                        │  │
│  │  - Renders tabs: Chart | Table | Query              │  │
│  │  - Calls TrendSummary component                      │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│                   ▼                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TrendSummary Component                              │  │
│  │  ✓ Calculates highest/lowest values                 │  │
│  │  ✓ Calculates average                                │  │
│  │  ✓ Compares first half vs second half               │  │
│  │  ✓ Determines trend direction (↗ or ↘)              │  │
│  │  ✓ Calculates trend percentage                       │  │
│  │  ✓ Generates smart suggestions                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works (Step-by-Step)

### Step 1: Backend Returns Chart Data

When a user asks a question like **"Show premium by agent"**, the backend:

1. Identifies it as an insurance query
2. Generates SQL: `SELECT agent_name, SUM(gwp) FROM insurance_data GROUP BY agent_name`
3. Executes on Athena
4. Returns JSON response:

```json
{
  "type": "bar",
  "data": [
    {"label": "Agent Kumar", "value": "45000"},
    {"label": "Agent Sharma", "value": "62000"},
    {"label": "Agent Patel", "value": "38000"},
    {"label": "Agent Singh", "value": "71000"}
  ],
  "explanation": "Premium distribution across agents shows Agent Singh leading with ₹71,000.",
  "customer_specific": "False",
  "query_executed": "SELECT agent_name, SUM(gwp) FROM insurance_data GROUP BY agent_name"
}
```

### Step 2: Frontend Detects Chart Data

In `ChatMessage.jsx`, the component checks:

```javascript
const isChartData = Array.isArray(content.data) && content.type !== 'text'
```

If true, it renders:
- **Chart View** (using ChartView.jsx)
- **Table View** (data in table format)
- **Query View** (SQL query)
- **Trend Summary** (automatic analysis)

### Step 3: TrendSummary Component Analyzes Data

The `TrendSummary` component in `ChatMessage.jsx` performs calculations:

```javascript
function TrendSummary({ data }) {
  // Extract numeric values
  const values = data.map(item => Number(item.value) || 0)
  
  // Calculate statistics
  const total = values.reduce((sum, val) => sum + val, 0)
  const average = total / values.length
  const max = Math.max(...values)
  const min = Math.min(...values)
  
  // Find items with max/min values
  const maxItem = data[values.indexOf(max)]
  const minItem = data[values.indexOf(min)]
  
  // Calculate trend by comparing first half vs second half
  const midPoint = Math.floor(values.length / 2)
  const firstHalfAvg = values.slice(0, midPoint).reduce((sum, val) => sum + val, 0) / midPoint
  const secondHalfAvg = values.slice(midPoint).reduce((sum, val) => sum + val, 0) / (values.length - midPoint)
  
  // Calculate percentage change
  const trendPercentage = ((secondHalfAvg - firstHalfAvg) / firstHalfAvg * 100).toFixed(1)
  const isIncreasing = secondHalfAvg > firstHalfAvg
  
  // Render analysis...
}
```

### Step 4: Display Trend Analysis

The component displays:

```
┌─────────────────────────────────────────────────────────┐
│ 📈 Trend Analysis                                       │
├─────────────────────────────────────────────────────────┤
│ Highest:  Agent Singh (71,000)                          │
│ Lowest:   Agent Patel (38,000)                          │
│ Average:  54,000.00                                     │
│ Trend:    ↗ 15.3%                                       │
├─────────────────────────────────────────────────────────┤
│ Suggestion: Positive momentum detected. Consider        │
│ capitalizing on this upward trend by maintaining        │
│ current strategies.                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Trend Calculation Logic

### How Trend Direction is Determined

The trend is calculated by **comparing the first half of data points to the second half**:

**Example with 4 agents:**
```
Data: [45000, 62000, 38000, 71000]

First Half:  [45000, 62000]  → Average = 53,500
Second Half: [38000, 71000]  → Average = 54,500

Trend = (54,500 - 53,500) / 53,500 × 100 = +1.87%
Direction: ↗ (Increasing)
```

**Example with 6 months:**
```
Data: [30, 25, 22, 28, 32, 35]

First Half:  [30, 25, 22]  → Average = 25.67
Second Half: [28, 32, 35]  → Average = 31.67

Trend = (31.67 - 25.67) / 25.67 × 100 = +23.4%
Direction: ↗ (Increasing)
```

### Trend Indicators

| Trend | Symbol | Meaning |
|-------|--------|---------|
| Positive | ↗ | Second half average > First half average |
| Negative | ↘ | Second half average < First half average |

---

## Smart Suggestions

Based on the trend direction, the system provides contextual suggestions:

### Upward Trend (↗)
```
"Positive momentum detected. Consider capitalizing on this upward 
trend by maintaining current strategies."
```

### Downward Trend (↘)
```
"Declining trend observed. Review strategies and consider adjustments 
to reverse the downward movement."
```

---

## When Trend Analysis Appears

Trend Analysis is **automatically displayed** for:

✅ **Chart responses** (bar, line, pie, scatter)
- Premium by agent
- Policies by zone
- Monthly sales trends
- Regional distribution

❌ **NOT displayed** for:
- Text responses (simple answers)
- Customer-specific data (profile information)
- Single value responses (counts, totals)

---

## Chart Types and Trend Analysis

### Bar Charts
**Use Case:** Categorical comparisons
**Example:** "Show premium by agent"
**Trend Logic:** Compares first half of agents vs second half

### Line Charts
**Use Case:** Time-series data
**Example:** "Show monthly policy trends"
**Trend Logic:** Compares first half of time period vs second half (most meaningful)

### Pie Charts
**Use Case:** Percentage distributions
**Example:** "Show policy type distribution"
**Trend Logic:** Compares first half of categories vs second half

### Scatter Charts
**Use Case:** Correlations
**Example:** "Premium vs sum insured"
**Trend Logic:** Compares first half of data points vs second half

---

## Key Features

### 1. **Automatic Calculation**
- No backend processing required
- Instant analysis on client side
- Works with any chart data

### 2. **Statistical Insights**
- Highest value and label
- Lowest value and label
- Average across all data points
- Trend percentage with direction

### 3. **Smart Suggestions**
- Context-aware recommendations
- Based on trend direction
- Actionable insights

### 4. **Visual Indicators**
- Color-coded trend arrows
- Green for upward (↗)
- Red for downward (↘)

---

## Code Location

| Component | File | Purpose |
|-----------|------|---------|
| Trend Calculation | `Frontend/src/components/ChatMessage.jsx` | TrendSummary component |
| Chart Rendering | `Frontend/src/components/ChartView.jsx` | Recharts integration |
| Styling | `Frontend/src/components/ChatMessage.css` | Trend summary styles |

---

## Example Scenarios

### Scenario 1: Insurance Premium Analysis

**User Query:** "Show premium by zone"

**Backend Response:**
```json
{
  "type": "bar",
  "data": [
    {"label": "North Zone", "value": "125000"},
    {"label": "South Zone", "value": "98000"},
    {"label": "East Zone", "value": "87000"},
    {"label": "West Zone", "value": "142000"}
  ],
  "explanation": "Premium distribution across zones..."
}
```

**Trend Analysis Output:**
```
📈 Trend Analysis
Highest:  West Zone (142,000)
Lowest:   East Zone (87,000)
Average:  113,000.00
Trend:    ↗ 18.9%

Suggestion: Positive momentum detected...
```

### Scenario 2: Monthly Sales Trend

**User Query:** "Show monthly policy trends for 2025"

**Backend Response:**
```json
{
  "type": "line",
  "data": [
    {"label": "Jan", "value": "45"},
    {"label": "Feb", "value": "52"},
    {"label": "Mar", "value": "48"},
    {"label": "Apr", "value": "61"},
    {"label": "May", "value": "58"},
    {"label": "Jun", "value": "67"}
  ],
  "explanation": "Monthly policy trends show growth..."
}
```

**Trend Analysis Output:**
```
📈 Trend Analysis
Highest:  Jun (67)
Lowest:   Jan (45)
Average:  55.17
Trend:    ↗ 26.4%

Suggestion: Positive momentum detected...
```

---

## Benefits

1. **No Backend Load:** All calculations happen in the browser
2. **Instant Insights:** No API calls needed for trend analysis
3. **Consistent Experience:** Same analysis for all chart types
4. **User-Friendly:** Non-technical users get actionable insights
5. **Scalable:** Works with any size dataset

---

## Limitations

1. **Simple Trend Logic:** Only compares first half vs second half (not sophisticated time-series analysis)
2. **Order Dependent:** Trend calculation depends on data order (meaningful for time-series, less so for categorical)
3. **No Historical Context:** Doesn't consider previous queries or historical patterns
4. **Fixed Suggestions:** Generic suggestions based only on direction (up/down)

---

## Future Enhancements

Potential improvements to trend analysis:

1. **Advanced Algorithms:** Moving averages, exponential smoothing
2. **Seasonal Detection:** Identify recurring patterns
3. **Anomaly Detection:** Flag unusual data points
4. **Predictive Insights:** Forecast future trends
5. **Comparative Analysis:** Compare to previous periods
6. **Custom Thresholds:** User-defined alert levels

---

## Summary

Trend Analysis in Sentra is a **lightweight, client-side feature** that automatically provides statistical insights and smart suggestions for any chart data. It enhances the user experience by turning raw data into actionable intelligence without requiring additional backend processing.

**Key Takeaway:** The backend focuses on data retrieval, while the frontend adds intelligence through automatic trend analysis.
