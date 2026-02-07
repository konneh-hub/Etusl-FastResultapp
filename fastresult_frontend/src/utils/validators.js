export const validators = {
  isValidEmail: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  },
  
  isValidMatricNumber: (matricNumber) => {
    return matricNumber && matricNumber.length >= 5
  },
  
  isValidScore: (score) => {
    return score >= 0 && score <= 100
  }
}
