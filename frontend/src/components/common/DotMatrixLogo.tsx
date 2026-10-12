import React from 'react'

export const DotMatrixLogo: React.FC = () => {
  return (
    <div className="flex items-center gap-2.5 select-none">
      {/* 3x3 Dot-Matrix Hardware Glyph */}
      <div className="grid grid-cols-3 gap-[3px] p-1.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] shadow-inner">
        <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--text-secondary)] opacity-60" />
        <span className="h-1 w-1 rounded-full bg-[var(--accent-red)]" />
      </div>

      {/* Neat, Simple Dot-Matrix Styled Brand Name */}
      <div className="flex items-center gap-2">
        <span className="font-mono-tech text-sm sm:text-base font-extrabold tracking-[0.22em] text-[var(--text-primary)] uppercase">
          SMARTINVOICE
        </span>
        <span className="rounded bg-[var(--accent-red)] px-1.5 py-0.5 font-mono-tech text-[9px] font-black text-white tracking-widest uppercase shadow-sm">
          AI
        </span>
      </div>
    </div>
  )
}
