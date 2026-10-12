import React from 'react'
import { DotMatrixLogo } from '../common/DotMatrixLogo'
import { Sun, Moon } from 'lucide-react'

interface HeaderProps {
  theme: 'dark' | 'light'
  onToggleTheme: () => void
}

export const Header: React.FC<HeaderProps> = ({ theme, onToggleTheme }) => {
  return (
    <header className="border-b border-[var(--border-color)] bg-[var(--bg-surface)] px-4 py-3 sm:px-8 transition-colors duration-200">
      <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between">
        {/* Brand: Dot-Matrix SMARTINVOICE AI */}
        <DotMatrixLogo />

        {/* Short & Simple Dark / Light Theme Toggle */}
        <button
          type="button"
          onClick={onToggleTheme}
          className="flex items-center gap-1.5 rounded-full border border-[var(--border-color)] bg-[var(--bg-card)] px-3 py-1.5 font-mono-tech text-[10.5px] font-bold tracking-wider text-[var(--text-primary)] hover:border-[var(--text-secondary)] transition-all cursor-pointer shadow-sm active:scale-95"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? (
            <>
              <Sun className="h-3.5 w-3.5 text-amber-400 shrink-0" />
              <span>LIGHT</span>
            </>
          ) : (
            <>
              <Moon className="h-3.5 w-3.5 text-indigo-500 shrink-0" />
              <span>DARK</span>
            </>
          )}
        </button>
      </div>
    </header>
  )
}
