export const formatters = {
  formatDate: (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  },
  
  formatCurrency: (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  },
  
  formatPercent: (value) => {
    return `${parseFloat(value).toFixed(2)}%`
  }
}
