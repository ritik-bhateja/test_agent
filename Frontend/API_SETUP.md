# API Integration Guide

## Quick Setup

1. **Configure the API endpoint:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and replace `<api-id>` with your actual AWS API Gateway ID:**
   ```env
   VITE_API_ENDPOINT=https://your-actual-api-id.execute-api.ap-south-1.amazonaws.com/invoke
   ```

3. **Restart the development server:**
   ```bash
   npm run dev
   ```

## What Changed

### 1. API Integration
- Replaced mock API calls with actual endpoint
- Added environment variable support for easy configuration
- Implemented error handling with fallback to mock data

### 2. Icon Updates
- Replaced emoji icons with professional SVG icons:
  - 📊 → Bar chart icon (Chart view)
  - 📋 → Table grid icon (Table view)
  - 🔍 → Code brackets icon (Query view)

### 3. Configuration Files
- `.env` - Your local API configuration (not committed to git)
- `.env.example` - Template for other developers
- Updated `.gitignore` to exclude `.env` files

## API Request Format

```json
{
  "user_query": "Show sales by quarter",
  "customer_specific": false
}
```

## Expected Response Formats

### Chart Data
```json
{
  "type": "bar|line|pie|scatter",
  "data": [
    {"label": "Q1", "value": 45000},
    {"label": "Q2", "value": 52000}
  ],
  "explanation": "Sales performance shows strong growth...",
  "query": "SELECT quarter, SUM(revenue) as value FROM sales_data..."
}
```

### Customer Data
```json
{
  "type": "customer",
  "data": {
    "name": "John Anderson",
    "photo": "/images/customers/john_anderson.jpg",
    "email": "john@example.com",
    "phone": "+1 555-123-4567",
    "accountNumber": "ACC-123456",
    "balance": 125750.50,
    "status": "Active"
  },
  "explanation": "Customer profile retrieved successfully."
}
```

### Text Response
```json
{
  "type": "text",
  "data": "Simple text response",
  "explanation": "Additional context or explanation"
}
```

## Testing

1. Start the development server
2. Try a query in the chat interface
3. Check browser console for API requests/responses
4. If API fails, mock data will be used automatically

## Troubleshooting

- **CORS errors**: Ensure your API Gateway has CORS enabled
- **404 errors**: Verify the API endpoint URL is correct
- **Authentication**: Add auth headers if required by your API
- **Mock data showing**: Check console for API errors

## Next Steps

- Update the API endpoint in `.env`
- Test with real queries
- Adjust response format if needed
- Add authentication if required
