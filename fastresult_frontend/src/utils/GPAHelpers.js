export const GPAHelpers = {
  calculateGPA: (scores, credits) => {
    const totalPoints = scores.reduce((sum, score, i) => sum + score * credits[i], 0)
    const totalCredits = credits.reduce((sum, credit) => sum + credit, 0)
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : 0
  },
  
  getGradeColor: (grade) => {
    const colors = {
      'A': '#28a745',
      'B': '#17a2b8',
      'C': '#ffc107',
      'D': '#fd7e14',
      'F': '#dc3545'
    }
    return colors[grade] || '#6c757d'
  }
}
