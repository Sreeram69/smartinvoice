import React from 'react'

export type NavTab = 'invoice' | 'address' | 'booking'

interface SegmentedNavProps {
  activeTab: NavTab
  onSelectTab: (tab: NavTab) => void
}

export const SegmentedNav: React.FC<SegmentedNavProps> = ({ activeTab, onSelectTab }) => {
  const tabs: { id: NavTab; label: string }[] = [
    { id: 'invoice', label: 'INVOICE' },
    { id: 'address', label: 'ADDRESS' },
    { id: 'booking', label: 'BOOKING AWB' },
  ]

  const activeIndex = tabs.findIndex((t) => t.id === activeTab)

  return (
    <div className="max-w-xl mx-auto my-3.5 w-full px-2">
      <div className="relative flex p-1 rounded-full border border-[var(--border-color)] bg-[var(--bg-surface)] backdrop-blur shadow-sm">
        {/* Smooth Sliding Pill Indicator */}
        <div
          className="absolute top-1 bottom-1 rounded-full bg-[var(--nav-active-bg)] transition-transform duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] shadow-md"
          style={{
            width: `calc((100% - 8px) / ${tabs.length})`,
            transform: `translateX(${activeIndex * 100}%)`,
          }}
        />

        {/* Tab Buttons */}
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onSelectTab(tab.id)}
              className={`relative z-10 flex-1 py-1.5 text-center font-mono-tech text-xs font-bold tracking-wider transition-colors duration-200 cursor-pointer select-none ${
                isActive
                  ? 'text-[var(--nav-active-text)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              }`}
            >
              {tab.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
