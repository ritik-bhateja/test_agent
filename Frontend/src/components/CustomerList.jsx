import { useState, useEffect } from 'react'
import './CustomerList.css'

function CustomerList({ onSelectCustomer }) {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const userId = localStorage.getItem('sentra_user_id') || 'unknown'
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userId
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Fetched customer data:', data)
      
      if (data.status === 'ok' && data.rows && Array.isArray(data.rows)) {
        setCustomers(data.rows)
        setError(null)
      } else {
        console.error('Invalid data format:', data)
        setError('Invalid data format received')
      }
    } catch (err) {
      setError(`Error: ${err.message}`)
      console.error('Error fetching customers:', err)
    } finally {
      setLoading(false)
    }
  }

  const getPhotoUrl = (cifNo) => {
    if (!cifNo) return null
    // Extract numeric part from CIF_NO (e.g., "CIF200000" -> "200000")
    // const numericPart = cifNo.replace(/[^0-9]/g, '')
    return `/images/customers/${cifNo}.jpg`
  }

  const getInitials = (name) => {
    if (!name) return '??'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  // Filter customers based on search query
  const filteredCustomers = customers.filter(customer => {
    const searchLower = searchQuery.toLowerCase()
    const name = (customer.CUSTOMER_NAME || '').toLowerCase()
    const cif = (customer.CIF_NO || '').toLowerCase()
    const phone = (customer.MOBILE_PHONE || '').toLowerCase()
    const email = (customer.EMAIL_ADDRESS || '').toLowerCase()
    
    return name.includes(searchLower) || 
           cif.includes(searchLower) || 
           phone.includes(searchLower) || 
           email.includes(searchLower)
  })

  if (loading) {
    return (
      <div className="customer-list-loading">
        <div className="spinner"></div>
        <p>Loading customers...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="customer-list-error">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M12 8V12M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        <p>{error}</p>
        <button onClick={fetchCustomers}>Retry</button>
      </div>
    )
  }

  return (
    <div className="customer-list">
      <h3>All Customers ({customers.length})</h3>
      
      <div className="customer-search-container">
        <svg className="customer-search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M7.33333 12.6667C10.2789 12.6667 12.6667 10.2789 12.6667 7.33333C12.6667 4.38781 10.2789 2 7.33333 2C4.38781 2 2 4.38781 2 7.33333C2 10.2789 4.38781 12.6667 7.33333 12.6667Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 14L11.1 11.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <input
          type="text"
          placeholder="Search customers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="customer-search-input"
        />
        {searchQuery && (
          <button className="customer-search-clear" onClick={() => setSearchQuery('')}>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        )}
      </div>

      {filteredCustomers.length === 0 && searchQuery ? (
        <div className="customer-no-results">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <path d="M17.5 31.6667C25.3239 31.6667 31.6667 25.3239 31.6667 17.5C31.6667 9.67609 25.3239 3.33334 17.5 3.33334C9.67609 3.33334 3.33334 9.67609 3.33334 17.5C3.33334 25.3239 9.67609 31.6667 17.5 31.6667Z" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M36.6667 36.6667L27.375 27.375" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <p>No customers found</p>
          <span>Try a different search term</span>
        </div>
      ) : (
        <div className="customer-list-items">
          {filteredCustomers.map((customer, index) => (
          <div
            key={customer.CIF_NO || index}
            className="customer-list-item"
            onClick={() => onSelectCustomer && onSelectCustomer(customer)}
          >
            <div className="customer-list-photo">
              {customer.CIF_NO && (
                <img 
                  src={getPhotoUrl(customer.CIF_NO)} 
                  alt={customer.CUSTOMER_NAME}
                  onError={(e) => {
                    e.target.style.display = 'none'
                    e.target.nextSibling.style.display = 'flex'
                  }}
                />
              )}
              <div 
                className="customer-list-avatar" 
                style={{ display: customer.CIF_NO ? 'none' : 'flex' }}
              >
                {getInitials(customer.CUSTOMER_NAME)}
              </div>
            </div>
            <div className="customer-list-info">
              <div className="customer-list-name">{customer.CUSTOMER_NAME || 'Unknown'}</div>
              <div className="customer-list-cif">{customer.CIF_NO || 'N/A'}</div>
              {customer.MOBILE_PHONE && (
                <div className="customer-list-phone">📱 {customer.MOBILE_PHONE}</div>
              )}
              {customer.EMAIL_ADDRESS && (
                <div className="customer-list-email">📧 {customer.EMAIL_ADDRESS}</div>
              )}
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  )
}

export default CustomerList
