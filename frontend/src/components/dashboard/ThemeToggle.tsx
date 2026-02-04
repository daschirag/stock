'use client'

import { Sun, Moon } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')

  useEffect(() => {
    const root = document.documentElement
    const stored = (typeof window !== 'undefined' && (localStorage.getItem('theme') as 'dark' | 'light')) || 'dark'
    setTheme(stored)
    root.classList.toggle('dark', stored === 'dark')
    root.classList.toggle('light', stored === 'light')
  }, [])

  const toggle = () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    localStorage.setItem('theme', next)
    document.documentElement.classList.toggle('dark', next === 'dark')
    document.documentElement.classList.toggle('light', next === 'light')
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className="p-2 rounded-lg bg-background-tertiary hover:bg-accent-gold/20 transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
