import React from 'react'

export const CornerGrid: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`corner-grid ${className}`} aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
      <span />
    </div>
  )
}
