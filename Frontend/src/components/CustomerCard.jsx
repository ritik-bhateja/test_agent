import './CustomerCard.css'

function CustomerCard({ customer }) {
  // Reserved fields that have special handling
  const reservedFields = ['name', 'customer_name', 'photo', 'status', 'customer_status', 'cif_no']
  
  // Get name - check both 'name' and 'customer_name' fields
  const name = customer.name || customer.customer_name || 'Unknown Customer'
  
  // If cif_no exists, use it to construct photo path, otherwise use provided photo
  const photo = customer.cif_no 
    ? `/images/customers/${customer.cif_no}.jpg` 
    : customer.photo
  
  // Get status - check both 'status' and 'customer_status' fields
  // Only show status if it exists in the response
  const status = customer.status || customer.customer_status || null

  // Get all other fields dynamically
  const dynamicFields = Object.entries(customer)
    .filter(([key]) => !reservedFields.includes(key))
    .map(([key, value]) => ({
      key,
      label: formatLabel(key),
      value: formatValue(key, value),
      icon: getIcon(key)
    }))

  function formatLabel(key) {
    // Convert camelCase or snake_case to Title Case
    return key
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .trim()
  }

  function formatValue(key, value) {
    if (value === null || value === undefined) return 'N/A'
    
    // Format based on key name
    const lowerKey = key.toLowerCase()
    
    if (lowerKey.includes('balance') || lowerKey.includes('amount') || lowerKey.includes('salary')) {
      return `$${Number(value).toLocaleString()}`
    }
    
    if (lowerKey.includes('date')) {
      return new Date(value).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No'
    }
    
    if (typeof value === 'object' && !Array.isArray(value)) {
      // Format object as readable key-value pairs
      return Object.entries(value)
        .map(([k, v]) => {
          const formattedKey = k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
          return `${formattedKey}: ${v}`
        })
        .join(', ')
    }
    
    if (Array.isArray(value)) {
      return value.join(', ')
    }
    
    // Format large numbers with commas
    if (typeof value === 'number') {
      return value.toLocaleString()
    }
    
    return String(value)
  }

  function getIcon(key) {
    const lowerKey = key.toLowerCase()
    
    if (lowerKey.includes('email')) return '📧'
    if (lowerKey.includes('phone') || lowerKey.includes('mobile')) return '📱'
    if (lowerKey.includes('address') || lowerKey.includes('location')) return '📍'
    if (lowerKey.includes('account')) return '🏦'
    if (lowerKey.includes('balance') || lowerKey.includes('amount')) return '💰'
    if (lowerKey.includes('date') || lowerKey.includes('time')) return '📅'
    if (lowerKey.includes('type') || lowerKey.includes('category')) return '💳'
    if (lowerKey.includes('score') || lowerKey.includes('rating')) return '⭐'
    if (lowerKey.includes('transaction')) return '🔄'
    if (lowerKey.includes('id') || lowerKey.includes('number')) return '🔢'
    if (lowerKey.includes('city') || lowerKey.includes('country')) return '🌍'
    if (lowerKey.includes('age')) return '🎂'
    if (lowerKey.includes('gender')) return '👤'
    if (lowerKey.includes('occupation') || lowerKey.includes('job')) return '💼'
    
    return '📋'
  }

  // Group fields into sections (optional - can be customized)
  const contactFields = dynamicFields.filter(f => 
    f.key.toLowerCase().includes('email') || 
    f.key.toLowerCase().includes('phone') || 
    f.key.toLowerCase().includes('address')
  )
  
  const accountFields = dynamicFields.filter(f => 
    f.key.toLowerCase().includes('account') || 
    f.key.toLowerCase().includes('balance') || 
    f.key.toLowerCase().includes('type')
  )
  
  const otherFields = dynamicFields.filter(f => 
    !contactFields.includes(f) && !accountFields.includes(f)
  )

  return (
    <div className="customer-card">
      <div className="customer-header">
        <div className="customer-photo">
          {photo ? (
            <img src={photo} alt={name} onError={(e) => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'flex'
            }} />
          ) : null}
          <div className="customer-avatar" style={{ display: photo ? 'none' : 'flex' }}>
            {name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
          </div>
        </div>
        <div className="customer-basic-info">
          <h3>{name}</h3>
          {status && (
            <span className={`status-badge ${status.toLowerCase()}`}>
              {status}
            </span>
          )}
        </div>
      </div>

      <div className="customer-details">
        {contactFields.length > 0 && (
          <div className="detail-section">
            <h4>Contact Information</h4>
            <div className="detail-grid">
              {contactFields.map(field => (
                <div 
                  key={field.key} 
                  className={`detail-item ${field.value.length > 50 ? 'full-width' : ''}`}
                >
                  <span className="detail-label">{field.icon} {field.label}</span>
                  <span className="detail-value">{field.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {accountFields.length > 0 && (
          <div className="detail-section">
            <h4>Account Details</h4>
            <div className="detail-grid">
              {accountFields.map(field => (
                <div key={field.key} className="detail-item">
                  <span className="detail-label">{field.icon} {field.label}</span>
                  <span className={`detail-value ${field.key.toLowerCase().includes('balance') ? 'balance' : ''}`}>
                    {field.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {otherFields.length > 0 && (
          <div className="detail-section">
            <h4>Additional Information</h4>
            <div className="detail-grid">
              {otherFields.map(field => (
                <div 
                  key={field.key} 
                  className={`detail-item ${field.value.length > 50 ? 'full-width' : ''}`}
                >
                  <span className="detail-label">{field.icon} {field.label}</span>
                  <span className="detail-value">{field.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CustomerCard
