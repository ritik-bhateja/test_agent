# API Response Format Guide

This document explains the three types of responses the Sentra Banking Assistant can handle.

## Response Type 1: Chart Data (List of Dictionaries)

**When to use:** For data visualization needs - sales, trends, distributions, comparisons, etc.

**Response Format:**
```json
{
  "type": "bar|line|pie|scatter",
  "data": [
    {"label": "India", "value": "25"},
    {"label": "America", "value": "29"},
    {"label": "Africa", "value": "21"}
  ],
  "explanation": "Regional distribution shows America leading with 29 units, followed by India with 25 units.",
  "customer_specific": "False",
  "query_executed": "SELECT region, COUNT(*) as count FROM customers GROUP BY region"
}
```

**Supported Chart Types:**
- `bar` - Bar chart for comparisons
- `line` - Line chart for trends over time
- `pie` - Pie chart for distributions
- `scatter` - Scatter plot for correlations

**Frontend Behavior:**
1. Renders the appropriate chart based on `type`
2. Provides toggle between:
   - **Chart View** - Visual representation
   - **Table View** - Data in tabular format
   - **Query View** - SQL query used (if provided)
3. Shows explanation text with insights
4. Displays automatic trend analysis including:
   - Highest and lowest values
   - Average value
   - Trend direction and percentage
   - Smart suggestions based on trend

**Optional Fields:**
- `query_executed` - SQL query or command executed to generate the data (shown in Query tab)

---

## Response Type 2: Simple Text Response

**When to use:** For simple answers, confirmations, or when no visualization is needed.

**Response Format:**
```json
{
  "type": "text",
  "data": "123",
  "explanation": "The total number of active accounts is 123.",
  "customer_specific": "False",
  "query_executed": "SELECT COUNT(*) FROM accounts WHERE status = 'active'"
}
```

**Frontend Behavior:**
1. Does NOT show any chart
2. Displays the `explanation` text in a styled response box
3. If `query_executed` is provided, shows a Query tab to view the executed query
4. The `data` field is ignored (only explanation is shown)
5. Clean, simple text presentation

**Use Cases:**
- Simple counts or totals
- Yes/No answers
- Status confirmations
- General information queries

---

## Response Type 3: Customer-Specific Data (Dictionary)

**When to use:** For customer profile information, account details, or any customer-specific queries.

**Response Format:**
```json
{
  "type": "text",
  "data": {
    "name": "John Anderson",
    "age": "23",
    "state": "California",
    "email": "john@example.com",
    "phone": "+1 555-123-4567",
    "accountNumber": "ACC-2024-789456",
    "balance": "125750.50",
    "status": "Active"
  },
  "explanation": "Customer profile retrieved successfully. John Anderson is an active member with excellent standing.",
  "customer_specific": "True"
}
```

**Frontend Behavior:**
1. Renders a professional customer profile card
2. Displays customer photo (automatically loaded from `/images/customers/{cif_no}.png` if `cif_no` provided) or initials avatar
3. Shows all fields dynamically with smart formatting:
   - Balance/amount fields → Currency format ($125,750.50)
   - Date fields → Readable date format
   - Boolean fields → Yes/No
   - Status → Colored badge (Active/Inactive/Pending)
4. Shows explanation text as a summary
5. If `query_executed` is provided, shows a Query tab to view the executed query
6. Responsive card layout

**Special Fields:**
- `name` or `customer_name` - Customer name (required, either fi
- `cif_no` - Customer CIF number (automatically used to load photo from `/images/customers/{cif_no}.png`)
- `photo` - Photo URL or path (optional, overridden by cif_no if present)
- `status` - Account status with colored badge (optional)

**Dynamic Field Support:**
All other fields are automatically displayed with appropriate icons and formatting. You can include any custom fields and they will be rendered properly.

---

## Important Notes

### customer_specific Field
- Must be `"True"` (string) or `true` (boolean) for customer data
- Must be `"False"` (string) or `false` (boolean) for other responses
- This field determines whether to show customer card or regular response

### Data Type Detection
The frontend automatically detects the response type based on:
1. `customer_specific` flag
2. `data` structure (array vs object vs string)
3. `type` field

### Value Formatting
- Numeric values in chart data can be strings or numbers
- The frontend automatically converts and formats them
- Use locale-appropriate number formatting (commas, decimals)

---

## Example API Responses

### Example 1: Sales by Quarter (Bar Chart)
```json
{
  "type": "bar",
  "data": [
    {"label": "Q1 2024", "value": "45000"},
    {"label": "Q2 2024", "value": "52000"},
    {"label": "Q3 2024", "value": "48000"},
    {"label": "Q4 2024", "value": "61000"}
  ],
  "explanation": "Sales performance shows strong growth in Q4, with a 27% increase compared to Q3. Overall annual trend is positive with total revenue of $206,000.",
  "customer_specific": "False",
  "query_executed": "SELECT quarter, SUM(revenue) as value FROM sales_data WHERE year = 2024 GROUP BY quarter"
}
```

### Example 2: Account Count (Text)
```json
{
  "type": "text",
  "data": "1,247",
  "explanation": "There are currently 1,247 active customer accounts in the system. This represents a 12% increase from last quarter.",
  "customer_specific": "False",
  "query_executed": "SELECT COUNT(*) FROM accounts WHERE status = 'active'"
}
```

### Example 3: Customer Profile (Customer Data)
```json
{
  "type": "text",
  "data": {
    "name": "Sarah Johnson",
    "cif_no": "CIF100002",
    "age": "34",
    "state": "New York",
    "email": "sarah.johnson@email.com",
    "phone": "+1 555-987-6543",
    "accountNumber": "ACC-2024-123456",
    "accountType": "Premium Checking",
    "balance": "87500.25",
    "joinDate": "2019-03-15",
    "status": "Active",
    "creditScore": "785",
    "lastTransaction": "2024-01-15"
  },
  "explanation": "Customer profile for Sarah Johnson retrieved successfully. She is a premium member with excellent credit standing and has been with us since 2019.",
  "customer_specific": "True"
}
```

**Note:** When `cif_no` is provided, the system automatically loads the customer photo from `/images/customers/{cif_no}.png`. For example, if `cif_no` is "CIF100002", it will load `/images/customers/CIF100002.png`.

---

## Testing Your API

### Test Response Type 1 (Chart):
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Show sales by region"}'
```

### Test Response Type 2 (Text):
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "How many accounts are active?"}'
```

### Test Response Type 3 (Customer):
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Show customer John Anderson details"}'
```

---

## Error Handling

If the API fails or returns an error, the frontend will:
1. Log the error to console
2. Fall back to mock data for development
3. Display the response normally

Make sure your API returns proper HTTP status codes:
- `200` - Success
- `400` - Bad request
- `500` - Server error
