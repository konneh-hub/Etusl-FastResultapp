/**
 * Theme provider and utilities
 */

export const themes = {
  light: {
    background: '#ffffff',
    foreground: '#000000',
    primary: '#3b82f6',
    secondary: '#6366f1',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#0ea5e9'
  },
  dark: {
    background: '#1f2937',
    foreground: '#f3f4f6',
    primary: '#60a5fa',
    secondary: '#818cf8',
    success: '#34d399',
    warning: '#fbbf24',
    danger: '#f87171',
    info: '#38bdf8'
  }
}

export const useTheme = () => {
  const theme = localStorage.getItem('theme') || 'light'
  return themes[theme]
}

export const setTheme = (theme) => {
  if (themes[theme]) {
    localStorage.setItem('theme', theme)
    applyTheme(theme)
  }
}

export const applyTheme = (theme) => {
  const root = document.documentElement
  const colors = themes[theme]

  Object.entries(colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value)
  })

  if (theme === 'dark') {
    document.body.classList.add('dark')
  } else {
    document.body.classList.remove('dark')
  }
}

export const toggleTheme = () => {
  const current = localStorage.getItem('theme') || 'light'
  const next = current === 'light' ? 'dark' : 'light'
  setTheme(next)
  return next
}

export const getCurrentTheme = () => {
  return localStorage.getItem('theme') || 'light'
}
