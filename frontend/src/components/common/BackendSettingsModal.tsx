import React, { useState } from 'react'
import { CornerGrid } from './CornerGrid'
import { Server, Check, X, RefreshCw, AlertCircle, Key, Eye, EyeOff } from 'lucide-react'
import {
  getBackendBaseUrl,
  setBackendBaseUrl,
  getApiKey,
  setApiKey,
  DEFAULT_API_KEY,
  testBackendConnection,
} from '../../utils/apiConfig'

interface BackendSettingsModalProps {
  isOpen: boolean
  onClose: () => void
  onConnectionChanged: () => void
}

export const BackendSettingsModal: React.FC<BackendSettingsModalProps> = ({
  isOpen,
  onClose,
  onConnectionChanged,
}) => {
  const [url, setUrl] = useState<string>(getBackendBaseUrl())
  const [apiKey, setApiKeyState] = useState<string>(getApiKey())
  const [showKey, setShowKey] = useState<boolean>(false)
  const [testing, setTesting] = useState<boolean>(false)
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null)

  if (!isOpen) return null

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    const res = await testBackendConnection(url, apiKey)
    setTestResult(res)
    setTesting(false)
  }

  const handleSave = () => {
    setBackendBaseUrl(url)
    setApiKey(apiKey)
    onConnectionChanged()
    onClose()
  }

  const handleReset = () => {
    setUrl('')
    setBackendBaseUrl('')
    setApiKeyState(DEFAULT_API_KEY)
    setApiKey(DEFAULT_API_KEY)
    setTestResult(null)
    onConnectionChanged()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-md rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-2xl space-y-4 animate-in fade-in duration-150">
        <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-3">
          <div className="flex items-center gap-2">
            <CornerGrid />
            <span className="section-label flex items-center gap-1.5 text-[var(--text-primary)]">
              <Server className="h-3.5 w-3.5 text-[var(--accent-red)]" />
              BACKEND CONNECTION & SECURITY
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] p-1 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-3">
          <p className="font-mono-tech text-xs text-[var(--text-secondary)]">
            Connect your Vercel web app to your backend processing service via secure HTTPS:
          </p>

          <div>
            <label className="section-label block mb-1">Backend Base URL</label>
            <input
              type="text"
              className="nothing-input text-xs"
              placeholder="e.g. https://smartinvoice.onrender.com or http://localhost:8000"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value)
                setTestResult(null)
              }}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="section-label flex items-center gap-1">
                <Key className="h-3 w-3 text-[var(--accent-red)]" />
                API Key (X-API-Key)
              </label>
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="font-mono-tech text-[10.5px] text-[var(--text-muted)] hover:text-[var(--text-primary)] flex items-center gap-1"
              >
                {showKey ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                <span>{showKey ? 'Hide' : 'Show'}</span>
              </button>
            </div>
            <input
              type={showKey ? 'text' : 'password'}
              className="nothing-input text-xs font-mono-tech"
              placeholder="smartinvoice-secret-key-2026"
              value={apiKey}
              onChange={(e) => {
                setApiKeyState(e.target.value)
                setTestResult(null)
              }}
            />
          </div>

          <div className="flex items-center justify-between gap-2 pt-1">
            <button
              type="button"
              onClick={handleTest}
              disabled={testing}
              className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <RefreshCw className={`h-3 w-3 text-[var(--accent-red)] ${testing ? 'animate-spin' : ''}`} />
              <span>{testing ? 'TESTING...' : 'TEST CONNECTION'}</span>
            </button>

            <button
              type="button"
              onClick={handleReset}
              className="font-mono-tech text-[10.5px] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              Reset to Local
            </button>
          </div>

          {testResult && (
            <div
              className={`rounded-lg p-2.5 text-xs font-mono-tech flex items-center gap-2 border ${
                testResult.ok
                  ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                  : 'border-[var(--accent-red)]/30 bg-[var(--accent-red)]/10 text-[var(--accent-red)]'
              }`}
            >
              {testResult.ok ? <Check className="h-4 w-4 shrink-0" /> : <AlertCircle className="h-4 w-4 shrink-0" />}
              <span>{testResult.message}</span>
            </div>
          )}

          <div className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-3 text-[10.5px] font-mono-tech text-[var(--text-secondary)] space-y-1">
            <div className="text-[var(--text-primary)] font-bold">Quick Guide:</div>
            <div>• Local Dev: Leave URL empty or <code>http://localhost:8000</code></div>
            <div>• Render Cloud: Set to your Render URL (e.g. <code>https://smartinvoice-backend.onrender.com</code>).</div>
            <div>• Keep your API Key secret so unauthorized visitors cannot access your backend.</div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-[var(--border-color)]">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            CANCEL
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="btn-primary text-xs py-1.5 px-4 flex items-center gap-1.5"
          >
            <Check className="h-3.5 w-3.5" />
            <span>SAVE & APPLY</span>
          </button>
        </div>
      </div>
    </div>
  )
}
