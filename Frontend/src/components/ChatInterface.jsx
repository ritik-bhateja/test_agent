import { useState, useEffect, useRef } from 'react'
import Sidebar from './Sidebar'
import ChatMessage from './ChatMessage'
import UserProfile from './UserProfile'
import './ChatInterface.css'

function ChatInterface({ onLogout }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [showProfile, setShowProfile] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef(null)
  const abortControllerRef = useRef(null)

  const userId = localStorage.getItem('sentra_user_id') || 'default'

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    if (currentSessionId) {
      loadSession(currentSessionId)
    }
  }, [currentSessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadSessions = () => {
    const sessionKey = `sentra_sessions_${userId}`
    const savedSessions = JSON.parse(localStorage.getItem(sessionKey) || '[]')
    setSessions(savedSessions)
    if (savedSessions.length > 0) {
      setCurrentSessionId(savedSessions[0].id)
    } else {
      createNewSession()
    }
  }

  const loadSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setMessages(session.messages || [])
    }
  }

  const saveSession = (sessionId, updatedMessages) => {
    const sessionKey = `sentra_sessions_${userId}`
    const updatedSessions = sessions.map(s => 
      s.id === sessionId ? { ...s, messages: updatedMessages, updatedAt: Date.now() } : s
    )
    setSessions(updatedSessions)
    localStorage.setItem(sessionKey, JSON.stringify(updatedSessions))
  }

  const createNewSession = () => {
    const sessionKey = `sentra_sessions_${userId}`
    
    // Generate session ID with exactly 33 characters (AWS Bedrock requirement)
    // Format: timestamp (13 chars) + underscore (1 char) + random alphanumeric (19 chars) = 33 chars
    const timestamp = Date.now().toString() // 13 characters
    const randomChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let randomSuffix = ''
    for (let i = 0; i < 19; i++) {
      randomSuffix += randomChars.charAt(Math.floor(Math.random() * randomChars.length))
    }
    const sessionId = `${timestamp}_${randomSuffix}` // Total: 33 characters
    
    const newSession = {
      id: sessionId,
      title: 'New Chat',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    const updatedSessions = [newSession, ...sessions]
    setSessions(updatedSessions)
    setCurrentSessionId(newSession.id)
    setMessages([])
    localStorage.setItem(sessionKey, JSON.stringify(updatedSessions))
  }

  const renameSession = (sessionId, newTitle) => {
    const sessionKey = `sentra_sessions_${userId}`
    const updatedSessions = sessions.map(s =>
      s.id === sessionId ? { ...s, title: newTitle } : s
    )
    setSessions(updatedSessions)
    localStorage.setItem(sessionKey, JSON.stringify(updatedSessions))
  }

  const deleteSession = (sessionId) => {
    const sessionKey = `sentra_sessions_${userId}`
    const updatedSessions = sessions.filter(s => s.id !== sessionId)
    setSessions(updatedSessions)
    localStorage.setItem(sessionKey, JSON.stringify(updatedSessions))
    
    if (currentSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        setCurrentSessionId(updatedSessions[0].id)
      } else {
        createNewSession()
      }
    }
  }

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setLoading(false)
    }
  }

  const handleSelectCustomer = (customer) => {
    // Create a query to show customer details
    const query = `Tell me concise description for customer ${customer.CUSTOMER_NAME} (${customer.CIF_NO})`
    setInput(query)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }

    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController()

    // Update session title if it's the first message
    if (messages.length === 0) {
      const sessionKey = `sentra_sessions_${userId}`
      const updatedSessions = sessions.map(s => 
        s.id === currentSessionId ? { ...s, title: input.trim().slice(0, 30) + '...' } : s
      )
      setSessions(updatedSessions)
      localStorage.setItem(sessionKey, JSON.stringify(updatedSessions))
    }

    try {
      // Call the actual API endpoint
      const apiEndpoint = `${import.meta.env.VITE_API_URL}/query`
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_query: input.trim(),
          user_id: userId,
          session_id: currentSessionId
        }),
        signal: abortControllerRef.current.signal
      })
      

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: data,
        timestamp: Date.now()
      }

      const finalMessages = [...updatedMessages, botMessage]
      setMessages(finalMessages)
      saveSession(currentSessionId, finalMessages)
    } catch (error) {
      // Check if the request was aborted
      if (error.name === 'AbortError') {
        console.log('Request was cancelled by user')
        // Don't add any bot message when stopped
        saveSession(currentSessionId, updatedMessages)
        return
      }
      
      console.error('API Error:', error)
      
      // Fallback to mock response if API fails
      const mockResponse = generateMockResponse(input.trim())
      
      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: mockResponse,
        timestamp: Date.now()
      }

      const finalMessages = [...updatedMessages, botMessage]
      setMessages(finalMessages)
      saveSession(currentSessionId, finalMessages)
    } finally {
      setLoading(false)
      abortControllerRef.current = null
    }
  }

  const getRandomCustomerPhoto = () => {
    const photos = [
      '/images/customers/CIF100000.jpg',
      '/images/customers/CIF100002.jpg',
      '/images/customers/CIF100003.jpg',
      '/images/customers/CIF100004.jpg',
      '/images/customers/CIF100005.jpg',
      '/images/customers/CIF100006.jpg',
      '/images/customers/CIF100007.jpg',
      '/images/customers/CIF100008.jpg',
      '/images/customers/CIF100009.jpg'
    ]
    return photos[Math.floor(Math.random() * photos.length)]
  }

  const getCustomerByName = (query) => {
    const lowerQuery = query.toLowerCase()
    
    // Check for specific customer names
    if (lowerQuery.includes('john')) {
      return {
        name: 'John Anderson',
        photo: '/images/customers/john_anderson.jpg',
        email: 'john.anderson@email.com',
        phone: '+1 (555) 123-4567',
        accountNumber: 'ACC-2024-789456',
        accountType: 'Premium Savings',
        balance: 125750.50,
        joinDate: '2020-01-15',
        status: 'Active',
        address: '123 Main Street, New York, NY 10001',
        lastTransaction: 'December 18, 2024 - $2,500 deposit',
        creditScore: 785,
        cifNumber: 'CIF100000'
      }
    }
    
    // Check for CIF numbers
    const cifMatch = lowerQuery.match(/cif\s*(\d+)/)
    if (cifMatch) {
      const cifNumber = `CIF${cifMatch[1]}`
      const photoPath = `/images/customers/${cifNumber}.jpg`
      
      return {
        name: `Customer ${cifMatch[1]}`,
        photo: photoPath,
        email: `customer${cifMatch[1]}@email.com`,
        phone: `+1 (555) ${cifMatch[1].slice(0, 3)}-${cifMatch[1].slice(3)}`,
        accountNumber: `ACC-2024-${cifMatch[1]}`,
        accountType: 'Savings Account',
        balance: Math.floor(Math.random() * 200000) + 10000,
        joinDate: '2021-06-20',
        status: 'Active',
        cifNumber: cifNumber,
        creditScore: Math.floor(Math.random() * 200) + 600
      }
    }
    
    // Default random customer
    const randomId = Math.floor(Math.random() * 9)
    const cifNumber = `CIF10000${randomId}`
    
    return {
      name: `Customer ${randomId}`,
      photo: getRandomCustomerPhoto(),
      email: `customer${randomId}@email.com`,
      phone: `+1 (555) 100-000${randomId}`,
      accountNumber: `ACC-2024-${randomId}`,
      accountType: 'Checking Account',
      balance: Math.floor(Math.random() * 150000) + 5000,
      joinDate: '2022-03-10',
      status: 'Active',
      cifNumber: cifNumber,
      creditScore: Math.floor(Math.random() * 200) + 650
    }
  }

  const generateMockResponse = (query) => {
    const lowerQuery = query.toLowerCase()
    
    // Return customer data if explicitly asked
    if (lowerQuery.includes('customer') || lowerQuery.includes('client') || lowerQuery.includes('john') || lowerQuery.includes('user') || lowerQuery.includes('cif')) {
      const customerData = getCustomerByName(query)
      
      return {
        type: 'customer',
        data: customerData,
        explanation: `Customer profile retrieved successfully. ${customerData.name} is an active member with ${customerData.accountType} and excellent standing.`
      }
    } else if (lowerQuery.includes('sales') || lowerQuery.includes('revenue')) {
      return {
        type: 'bar',
        data: [
          { label: 'Q1', value: 45000 },
          { label: 'Q2', value: 52000 },
          { label: 'Q3', value: 48000 },
          { label: 'Q4', value: 61000 }
        ],
        explanation: 'Sales performance shows strong growth in Q4, with a 27% increase compared to Q3. Overall annual trend is positive with total revenue of $206,000.',
        query_executed: 'SELECT quarter, SUM(revenue) as value FROM sales_data WHERE year = 2024 GROUP BY quarter ORDER BY quarter'
      }
    } else if (lowerQuery.includes('region')) {
      return {
        type: 'pie',
        data: [
          { label: 'North America', value: 45 },
          { label: 'Europe', value: 30 },
          { label: 'Asia', value: 20 },
          { label: 'Other', value: 5 }
        ],
        explanation: 'Regional distribution shows North America as the dominant market at 45%, followed by Europe at 30%. Consider expanding efforts in Asia for growth opportunities.',
        query_executed: 'SELECT region as label, (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers)) as value FROM customers GROUP BY region'
      }
    } else if (lowerQuery.includes('trend') || lowerQuery.includes('growth')) {
      return {
        type: 'line',
        data: [
          { label: 'Jan', value: 12 },
          { label: 'Feb', value: 19 },
          { label: 'Mar', value: 15 },
          { label: 'Apr', value: 25 },
          { label: 'May', value: 22 },
          { label: 'Jun', value: 30 }
        ],
        explanation: 'Growth trend analysis reveals consistent upward momentum with a 150% increase from January to June. Recommend maintaining current strategies.',
        query_executed: 'SELECT DATE_FORMAT(date, "%b") as label, SUM(growth_metric) as value FROM metrics WHERE YEAR(date) = 2024 GROUP BY MONTH(date) ORDER BY date'
      }
    } else {
      return {
        type: 'text',
        data: 'Based on your query, I found relevant information in our banking system.',
        explanation: 'I can help you analyze sales data, regional performance, growth trends, and other banking metrics. Try asking about "sales by quarter", "regional distribution", or "customer details".'
      }
    }
  }

  return (
    <div className="chat-interface">
      <Sidebar 
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={setCurrentSessionId}
        onNewSession={createNewSession}
        onRenameSession={renameSession}
        onDeleteSession={deleteSession}
        onLogout={onLogout}
        isOpen={sidebarOpen}
        onToggle={setSidebarOpen}
        onSelectCustomer={handleSelectCustomer}
      />
      <div className={`chat-main ${!sidebarOpen ? 'sidebar-closed' : ''}`}>
        <div className="chat-header">
          <div className="header-left">
            {!sidebarOpen && (
              <button className="open-sidebar-btn" onClick={() => setSidebarOpen(true)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M3 10H17M3 5H17M3 15H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            )}
            <h2>Sentra RM Assistant</h2>
          </div>
          <button className="user-profile-btn" onClick={() => setShowProfile(true)}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 10C12.7614 10 15 7.76142 15 5C15 2.23858 12.7614 0 10 0C7.23858 0 5 2.23858 5 5C5 7.76142 7.23858 10 10 10Z" fill="currentColor"/>
              <path d="M10 12C4.477 12 0 14.686 0 18V20H20V18C20 14.686 15.523 12 10 12Z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h3>Welcome to Sentra RM Assistant</h3>
              <p>Ask me anything about your banking data, sales, regions, or trends.</p>
              <div className="suggestions">
                <button onClick={() => setInput('Show sales by quarter')}>Sales by quarter</button>
                <button onClick={() => setInput('Regional distribution')}>Regional distribution</button>
                <button onClick={() => setInput('Growth trends')}>Growth trends</button>
                <button onClick={() => setInput('Show customer John details')}>Customer details</button>
              </div>
            </div>
          )}
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {loading && (
            <div className="loading-message">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <button className="stop-button" onClick={handleStop}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="3" width="10" height="10" fill="currentColor" rx="1"/>
                </svg>
                Stop
              </button>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about sales, regions, trends, or customer details..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M2 10L18 2L10 18L9 11L2 10Z" fill="currentColor"/>
            </svg>
          </button>
        </form>
      </div>
      {showProfile && (
        <UserProfile 
          onClose={() => setShowProfile(false)} 
          onLogout={onLogout}
        />
      )}
    </div>
  )
}

export default ChatInterface
