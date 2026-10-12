import React from 'react'

interface ToastBannerProps {
  message: string
  visible: boolean
}

export const ToastBanner: React.FC<ToastBannerProps> = ({ message, visible }) => {
  if (!visible) return null

  return (
    <div className="toast-banner">
      <span className="toast-dot-pulse" />
      <span>{message.toUpperCase()}</span>
    </div>
  )
}
