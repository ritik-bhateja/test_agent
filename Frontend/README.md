# Sentra - Banking Chatbot UI

A modern, dark-mode banking AI chatbot interface built with React and Vite.

## Features

- 🔐 Simple login page (any credentials work)
- 💬 Natural language query interface
- 📊 Dynamic chart rendering (Bar, Line, Pie, Scatter)
- 👤 Customer profile cards with dynamic fields
- 📋 Chart/Table toggle view
- 💾 Session persistence with localStorage
- 🎨 Clean, professional dark mode design
- 📱 Responsive layout for desktop and mobile
- ⚡ Typing animation and loading indicators
- 📂 Sidebar with session history
- ✏️ Rename and delete chat sessions
- 👥 User profile modal

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Customer Photos

Store customer profile photos in `public/images/customers/` directory.

### Photo Storage Options:

**Option 1: Local Storage (Recommended for development)**
```
public/
  └── images/
      └── customers/
          ├── customer_12345.jpg
          ├── john_anderson.png
          └── jane_doe.jpg
```

**Option 2: External CDN/URL**
Use full URLs in your API response:
```json
{
  "photo": "https://your-cdn.com/photos/customer_12345.jpg"
}
```

**Option 3: Base64 Encoded**
Include base64 image data directly:
```json
{
  "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

## API Integration

### Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update the API endpoint in `.env`:
```env
VITE_API_ENDPOINT=https://your-api-id.execute-api.ap-south-1.amazonaws.com/invoke
```

3. Replace `<api-id>` with your actual AWS API Gateway ID

The application will automatically use this endpoint for all queries. If the API fails, it will fallback to mock data for development purposes.

### Request Format

The application sends POST requests with the following body:
```json
{
  "user_query": "Show sales by quarter",
  "customer_specific": false
}
```

- `user_query`: The user's natural language query
- `customer_specific`: Boolean indicating if customer mode is active

## API Response Formats

### 1. Chart Data Response
```json
{
  "type": "bar|line|pie|scatter",
  "data": [
    {"label": "Label1", "value": 123},
    {"label": "Label2", "value": 456}
  ],
  "explanation": "Explanation text here",
  "query": "SELECT * FROM table" // Optional SQL query
}
```

### 2. Customer Profile Response (Dynamic Fields)
```json
{
  "type": "customer",
  "data": {
    "name": "John Anderson",
    "photo": "/images/customers/john_anderson.jpg",
    "status": "Active",
    // Any additional fields will be displayed dynamically
    "email": "john@example.com",
    "phone": "+1 555-123-4567",
    "accountNumber": "ACC-123456",
    "balance": 125750.50,
    "customField1": "Any value",
    "customField2": "Another value"
  },
  "explanation": "Customer profile retrieved successfully."
}
```

**Note:** The customer card is fully dynamic and will display any fields you provide. Reserved fields are:
- `name` - Customer name (required)
- `photo` - Photo URL (optional)
- `status` - Account status (optional, defaults to "Active")

All other fields will be automatically formatted and displayed with appropriate icons.

### 3. Text-Only Response
```json
{
  "type": "text",
  "data": "Simple text response",
  "explanation": "Explanation text here"
}
```

## Dynamic Field Formatting

The customer card automatically formats fields based on their names:
- **Balance/Amount fields**: Formatted as currency ($123,456.78)
- **Date fields**: Formatted as readable dates (January 15, 2024)
- **Boolean fields**: Displayed as Yes/No
- **Long text**: Automatically spans full width

## Tech Stack

- React 18
- Vite
- Recharts (for data visualization)
- CSS3 (custom styling)
- LocalStorage (for session persistence)

## Project Structure

```
src/
├── components/
│   ├── Login.jsx/css          # Login page
│   ├── ChatInterface.jsx/css  # Main chat interface
│   ├── ChatMessage.jsx/css    # Message display
│   ├── ChartView.jsx/css      # Chart rendering
│   ├── CustomerCard.jsx/css   # Customer profile card
│   ├── Sidebar.jsx/css        # Chat history sidebar
│   └── UserProfile.jsx/css    # User profile modal
├── App.jsx
├── main.jsx
└── index.css

public/
└── images/
    └── customers/             # Store customer photos here
```

## Features in Detail

### Customer Profile Cards
- Displays customer photo or initials avatar
- Status badges (Active/Inactive/Pending)
- Dynamically renders any fields from backend
- Automatic field grouping (Contact, Account, Additional)
- Smart formatting based on field names
- Responsive design for mobile and desktop

### Chart Visualizations
- Bar charts for comparisons
- Line charts for trends
- Pie charts for distributions
- Scatter plots for correlations
- Toggle between chart and table view
- View SQL queries used to generate data

### Session Management
- Auto-save conversations to localStorage
- Rename chat sessions
- Delete unwanted chats
- Session history in sidebar
- Persistent across page reloads

## Mobile Responsive

Fully optimized for mobile devices with:
- Collapsible sidebar
- Touch-friendly controls
- Responsive charts
- Optimized spacing and typography
- Hamburger menu navigation

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)
