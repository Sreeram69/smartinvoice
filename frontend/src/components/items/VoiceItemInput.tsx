import React, { useState } from 'react'
import { Mic, MicOff, Sparkles } from 'lucide-react'
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition'
import { parseSpokenItemClient } from '../../utils/itemParser'
import { CornerGrid } from '../common/CornerGrid'
import type { ItemLine } from '../../types/item'

interface VoiceItemInputProps {
  onAddItem: (item: Omit<ItemLine, 'id'>) => void
  onNotify: (msg: string) => void
}

export const VoiceItemInput: React.FC<VoiceItemInputProps> = ({ onAddItem, onNotify }) => {
  const [lastParsed, setLastParsed] = useState<Omit<ItemLine, 'id'> | null>(null)

  const handleSpeechResult = (finalText: string) => {
    if (!finalText.trim()) return
    const parsed = parseSpokenItemClient(finalText)
    setLastParsed(parsed)
    onAddItem(parsed)
    onNotify(`Added "${parsed.name}" (Count: ${parsed.count}, Price: ${parsed.price})`)
  }

  const {
    isListening,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
  } = useSpeechRecognition(handleSpeechResult)

  const toggleMic = () => {
    if (isListening) {
      stopListening()
    } else {
      setLastParsed(null)
      startListening()
    }
  }

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm cursor-default">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label">VOICE ITEM RECOGNITION</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono-tech text-[10px] text-[var(--text-secondary)]">
            {isListening ? 'LISTENING (SPEAK NOW)...' : isSupported ? 'IDLE - READY' : 'SPEECH API NOT SUPPORTED'}
          </span>
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              isListening
                ? 'bg-[var(--accent-red)] shadow-[0_0_8px_var(--accent-red)] animate-pulse'
                : isSupported
                ? 'bg-emerald-500'
                : 'bg-amber-500'
            }`}
          />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4">
        {/* Hardware Mic Button */}
        <button
          type="button"
          onClick={toggleMic}
          disabled={!isSupported}
          className={`relative flex h-14 w-14 shrink-0 items-center justify-center rounded-full border transition-all cursor-pointer ${
            isListening
              ? 'border-[var(--accent-red)] bg-[var(--accent-red)] text-white shadow-[0_0_20px_rgba(235,0,41,0.5)] scale-105'
              : 'border-[var(--border-color)] bg-[var(--bg-card)] text-[var(--text-primary)] hover:border-[var(--accent-red)] hover:text-[var(--accent-red)]'
          } ${!isSupported ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}
          title={isListening ? 'Click to stop listening' : 'Click to speak item'}
        >
          {isListening ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
          {isListening && (
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-red)] opacity-75" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--accent-red)]" />
            </span>
          )}
        </button>

        {/* Status & Spoken Transcript */}
        <div className="flex-1 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-3 shadow-sm">
          {isListening ? (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[var(--accent-red)] animate-pulse" />
                <span className="font-mono-tech text-[10px] uppercase tracking-wider text-[var(--accent-red)] font-bold">
                  Listening...
                </span>
              </div>
              <p className="font-mono-tech text-xs text-[var(--text-primary)] italic">
                {transcript || 'Speak now (e.g. "2 sarees price 3000")...'}
              </p>
            </div>
          ) : lastParsed ? (
            <div className="space-y-1">
              <span className="font-mono-tech text-[10px] text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 font-bold">
                <Sparkles className="h-3 w-3" /> Voice Item Added
              </span>
              <p className="font-mono-tech text-xs text-[var(--text-primary)]">
                <strong className="text-[var(--text-primary)]">{lastParsed.name}</strong> • Count: {lastParsed.count} • Price: ₹{lastParsed.price}
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              <span className="font-mono-tech text-[10px] text-[var(--text-secondary)] uppercase tracking-wider">
                Click microphone and speak:
              </span>
              <p className="font-mono-tech text-xs text-[var(--text-muted)]">
                "Boxes count 10 price 2500" &nbsp;•&nbsp; "2 sarees price 3000" &nbsp;•&nbsp; "Laptop 45000"
              </p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 text-xs font-mono-tech text-[var(--accent-red)] p-2.5 rounded border border-[var(--accent-red)]/30 bg-[var(--accent-red)]/10">
          ⚠️ {error}
        </div>
      )}
    </div>
  )
}
