import React, { useState, useRef, useEffect } from 'react'
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react'
import { getIndiaDate } from '../../utils/dateUtils'

interface NothingDatePickerProps {
  value: string // Format: YYYY-MM-DD
  onChange: (val: string) => void
  label?: string
}

export const NothingDatePicker: React.FC<NothingDatePickerProps> = ({
  value,
  onChange,
  label = 'Document Date',
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const [viewYear, setViewYear] = useState<number>(() => {
    const d = value ? new Date(value + 'T00:00:00') : new Date()
    return isNaN(d.getTime()) ? new Date().getFullYear() : d.getFullYear()
  })
  const [viewMonth, setViewMonth] = useState<number>(() => {
    const d = value ? new Date(value + 'T00:00:00') : new Date()
    return isNaN(d.getTime()) ? new Date().getMonth() : d.getMonth()
  })

  // Keep view in sync when value changes externally
  useEffect(() => {
    if (value) {
      const d = new Date(value + 'T00:00:00')
      if (!isNaN(d.getTime())) {
        setViewYear(d.getFullYear())
        setViewMonth(d.getMonth())
      }
    }
  }, [value])

  // Close popover on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick)
    }
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [isOpen])

  const monthNames = [
    'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
    'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
  ]

  const daysOfWeek = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']

  const prevMonth = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (viewMonth === 0) {
      setViewMonth(11)
      setViewYear(viewYear - 1)
    } else {
      setViewMonth(viewMonth - 1)
    }
  }

  const nextMonth = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (viewMonth === 11) {
      setViewMonth(0)
      setViewYear(viewYear + 1)
    } else {
      setViewMonth(viewMonth + 1)
    }
  }

  const handleSelectDay = (day: number) => {
    const yyyy = viewYear
    const mm = String(viewMonth + 1).padStart(2, '0')
    const dd = String(day).padStart(2, '0')
    onChange(`${yyyy}-${mm}-${dd}`)
    setIsOpen(false)
  }

  const handleSelectToday = (e: React.MouseEvent) => {
    e.stopPropagation()
    const todayStr = getIndiaDate()
    onChange(todayStr)
    const [y, m] = todayStr.split('-').map(Number)
    setViewYear(y)
    setViewMonth(m - 1)
    setIsOpen(false)
  }

  // Calculate calendar days
  const firstDayIndex = new Date(viewYear, viewMonth, 1).getDay()
  const daysInCurrentMonth = new Date(viewYear, viewMonth + 1, 0).getDate()
  const daysInPrevMonth = new Date(viewYear, viewMonth, 0).getDate()

  const calendarCells = []

  // Fill padding from previous month
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    calendarCells.push({
      day: daysInPrevMonth - i,
      currentMonth: false,
      year: viewMonth === 0 ? viewYear - 1 : viewYear,
      month: viewMonth === 0 ? 11 : viewMonth - 1,
    })
  }

  // Fill current month days
  for (let d = 1; d <= daysInCurrentMonth; d++) {
    calendarCells.push({
      day: d,
      currentMonth: true,
      year: viewYear,
      month: viewMonth,
    })
  }

  // Fill padding for trailing next month
  const totalSlots = Math.ceil(calendarCells.length / 7) * 7
  const trailingCount = totalSlots - calendarCells.length
  for (let i = 1; i <= trailingCount; i++) {
    calendarCells.push({
      day: i,
      currentMonth: false,
      year: viewMonth === 11 ? viewYear + 1 : viewYear,
      month: viewMonth === 11 ? 0 : viewMonth + 1,
    })
  }

  return (
    <div className="relative" ref={containerRef}>
      {label && <label className="section-label block mb-1">{label}</label>}

      {/* Styled Input Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="nothing-input flex items-center justify-between text-left cursor-pointer group hover:border-[var(--accent-red)] transition-colors"
      >
        <span className="font-mono-tech text-xs tracking-wider text-[var(--text-primary)]">
          {value || 'SELECT DATE'}
        </span>
        <CalendarIcon className="h-4 w-4 text-[var(--accent-red)] group-hover:scale-105 transition-transform" />
      </button>

      {/* Custom Nothing OS Calendar Popover */}
      {isOpen && (
        <div className="absolute z-50 mt-1.5 w-72 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-3.5 shadow-2xl animate-in fade-in zoom-in-95 duration-150 backdrop-blur-md">
          {/* Calendar Header */}
          <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-2.5 mb-2.5">
            <span className="font-mono-tech text-xs font-bold tracking-wider text-[var(--text-primary)]">
              {monthNames[viewMonth]} {viewYear}
            </span>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={prevMonth}
                className="p-1 rounded hover:bg-[var(--bg-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                title="Previous Month"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={nextMonth}
                className="p-1 rounded hover:bg-[var(--bg-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                title="Next Month"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Days of week header */}
          <div className="grid grid-cols-7 gap-1 text-center mb-1.5">
            {daysOfWeek.map((day) => (
              <span
                key={day}
                className="font-mono-tech text-[10px] font-bold text-[var(--text-muted)] tracking-wider"
              >
                {day}
              </span>
            ))}
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7 gap-1 text-center">
            {calendarCells.map((cell, idx) => {
              const yyyy = cell.year
              const mm = String(cell.month + 1).padStart(2, '0')
              const dd = String(cell.day).padStart(2, '0')
              const cellDateStr = `${yyyy}-${mm}-${dd}`
              const isSelected = cellDateStr === value
              const todayStr = getIndiaDate()
              const isToday = cellDateStr === todayStr

              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectDay(cell.day)}
                  className={`h-7 w-7 mx-auto rounded-full font-mono-tech text-[11px] flex items-center justify-center transition-all ${

                    isSelected
                      ? 'bg-[var(--accent-red)] text-white font-bold shadow-md scale-105'
                      : cell.currentMonth
                      ? 'text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]'
                      : 'text-[var(--text-muted)] opacity-30 hover:opacity-70'
                  } ${isToday && !isSelected ? 'border border-[var(--accent-red)]' : ''}`}
                >
                  {cell.day}
                </button>
              )
            })}
          </div>

          {/* Quick Select Today Footer */}
          <div className="mt-3 pt-2 border-t border-[var(--border-color)] flex items-center justify-between">
            <span className="font-mono-tech text-[10px] text-[var(--text-muted)]">
              TODAY (IST): {getIndiaDate()}
            </span>
            <button
              type="button"
              onClick={handleSelectToday}
              className="font-mono-tech text-[10.5px] font-bold text-[var(--accent-red)] hover:underline"
            >
              SELECT TODAY
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
