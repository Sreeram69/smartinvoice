import React, { useState } from 'react'
import { CornerGrid } from '../common/CornerGrid'
import { Download, FileText, CheckSquare, Square, Loader2, Tag, Clipboard } from 'lucide-react'
import { buildApiUrl, getAuthHeaders } from '../../utils/apiConfig'
import type { DocumentGenerationPayload } from '../../types/document'
import { NothingDatePicker } from '../common/NothingDatePicker'

interface DocumentDownloadCardProps {
  payload: DocumentGenerationPayload
  addressNumber?: string
  onUpdateField: (field: keyof DocumentGenerationPayload, value: any) => void
  onNotify: (msg: string) => void
  onSuccess?: () => void
  onAddressSuccess?: () => void
  mode?: 'invoice' | 'address'
}

export const DocumentDownloadCard: React.FC<DocumentDownloadCardProps> = ({
  payload,
  addressNumber,
  onUpdateField,
  onNotify,
  onSuccess,
  onAddressSuccess,
  mode = 'invoice',
}) => {
  const [isGeneratingInvoice, setIsGeneratingInvoice] = useState<boolean>(false)
  const [isGeneratingLabel, setIsGeneratingLabel] = useState<boolean>(false)

  const isInvoiceEnabled = payload.include_invoice !== false

  // Direct download Tax Invoice (PDF only, NO ZIP)
  const handleDownloadInvoice = async () => {
    if (!isInvoiceEnabled) {
      onNotify('Please enable the Tax Invoice checkbox first')
      return
    }

    setIsGeneratingInvoice(true)
    onNotify('Generating Tax Invoice (PDF)...')

    try {
      const response = await fetch(buildApiUrl('/api/v1/documents/generate-download'), {
        method: 'POST',
        headers: getAuthHeaders({
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
          ...payload,
          doc_type: 'invoice',
          include_address_label: false,
          invoice_format: 'pdf',
        }),
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized (401): Missing or invalid API key.')
        }
        let detail = response.statusText
        try {
          const errData = await response.json()
          if (errData.detail) detail = errData.detail
        } catch {
          // ignore
        }
        throw new Error(`Generation failed: ${detail}`)
      }

      let filename = `Invoice_${payload.doc_number}.pdf`
      const disposition = response.headers.get('Content-Disposition')
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^"]+)"?/)
        if (match && match[1]) {
          filename = match[1]
        }
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      onNotify(`Downloaded ${filename}`)
      if (onSuccess) {
        onSuccess()
      }
    } catch (err: any) {
      onNotify(`Error: ${err.message || 'Failed to download invoice'}`)
    } finally {
      setIsGeneratingInvoice(false)
    }
  }

  // Direct download Shipping Address Label (PDF only, named ADD-(country)-series.pdf, NO ZIP)
  const handleDownloadAddressLabel = async () => {
    if (!payload.include_address_label) {
      onNotify('Please enable the Shipping Address Label checkbox first')
      return
    }

    const targetDocNumber = mode === 'address' ? payload.doc_number : (addressNumber || payload.doc_number)

    setIsGeneratingLabel(true)
    onNotify(`Generating Shipping Address Label (${targetDocNumber})...`)

    try {
      const response = await fetch(buildApiUrl('/api/v1/documents/generate-download'), {
        method: 'POST',
        headers: getAuthHeaders({
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
          ...payload,
          doc_number: targetDocNumber,
          address_doc_number: targetDocNumber,
          doc_type: 'address',
          include_address_label: false,
          address_format: 'pdf',
        }),
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized (401): Missing or invalid API key.')
        }
        let detail = response.statusText
        try {
          const errData = await response.json()
          if (errData.detail) detail = errData.detail
        } catch {
          // ignore
        }
        throw new Error(`Generation failed: ${detail}`)
      }

      let filename = `${targetDocNumber}.pdf`
      const disposition = response.headers.get('Content-Disposition')
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^"]+)"?/)
        if (match && match[1]) {
          filename = match[1]
        }
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      onNotify(`Downloaded ${filename}`)
      if (mode === 'invoice') {
        if (onAddressSuccess) {
          onAddressSuccess()
        }
      } else {
        if (onSuccess) {
          onSuccess()
        }
      }
    } catch (err: any) {
      onNotify(`Error: ${err.message || 'Failed to download address label'}`)
    } finally {
      setIsGeneratingLabel(false)
    }
  }

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm cursor-default">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label">
            {mode === 'address' ? 'SHIPPING ADDRESS LABEL SETTINGS & DOWNLOAD' : 'DOCUMENT SETTINGS & SEPARATE DOWNLOADS'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {mode !== 'address' && isInvoiceEnabled && (
            <span className="font-mono-tech text-[10px] text-[var(--accent-red)] font-bold tracking-wider uppercase border border-[var(--accent-red)]/30 px-2 py-0.5 rounded">
              INVOICE PDF
            </span>
          )}
          {payload.include_address_label && (
            <span className="font-mono-tech text-[10px] text-[var(--accent-red)] font-bold tracking-wider uppercase border border-[var(--accent-red)]/30 px-2 py-0.5 rounded">
              LABEL PDF
            </span>
          )}
        </div>
      </div>

      {/* Row 1: Document Metadata */}
      {mode === 'address' ? (
        /* Address Mode: Address Number (ADD-COUNTRY-SERIES) + Document Date (Parcel Weight Removed) */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="input-container group">
            <label className="section-label block mb-1">
              Address Number
            </label>
            <input
              type="text"
              className="nothing-input font-bold"
              placeholder="e.g. ADD-USA-0001"
              value={payload.doc_number}
              onChange={(e) => onUpdateField('doc_number', e.target.value)}
            />
          </div>

          <div className="input-container group">
            <NothingDatePicker
              label="Document Date"
              value={payload.date}
              onChange={(val) => onUpdateField('date', val)}
            />
          </div>
        </div>
      ) : (
        /* Invoice Mode: Invoice Number + Date + Parcel Weight + AWB : + Contents Description */
        <div className="space-y-4 mb-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="input-container group">
              <label className="section-label block mb-1">
                Invoice Number
              </label>
              <input
                type="text"
                className="nothing-input font-bold"
                value={payload.doc_number}
                onChange={(e) => onUpdateField('doc_number', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <NothingDatePicker
                label="Document Date"
                value={payload.date}
                onChange={(val) => onUpdateField('date', val)}
              />
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">
                Parcel Weight / Pcs (Optional)
              </label>
              <input
                type="text"
                className="nothing-input font-mono-tech"
                placeholder="e.g. 14KG or 1PCS"
                value={payload.weight || ''}
                onChange={(e) => onUpdateField('weight', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <div className="flex items-center justify-between mb-1">
                <label className="section-label">
                  AWB : (Optional)
                </label>
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      const text = await navigator.clipboard.readText()
                      if (text) {
                        onUpdateField('awb_number', text.trim().toUpperCase())
                        onNotify(`Pasted AWB: ${text.trim().toUpperCase()}`)
                      }
                    } catch {
                      onNotify('Clipboard access denied or empty')
                    }
                  }}
                  className="font-mono-tech text-[10px] text-[var(--accent-red)] hover:underline flex items-center gap-1 cursor-pointer"
                  title="Paste AWB number from clipboard"
                >
                  <Clipboard className="h-3 w-3" />
                  <span>PASTE</span>
                </button>
              </div>
              <input
                type="text"
                className="nothing-input font-mono-tech font-bold uppercase text-[var(--accent-red)]"
                placeholder="e.g. AWB-USA-0001"
                value={payload.awb_number || ''}
                onChange={(e) => onUpdateField('awb_number', e.target.value.toUpperCase())}
              />
            </div>
          </div>

          {/* Contents Description */}
          <div className="input-container group">
            <label className="section-label block mb-1">
              Contents Description (Optional)
            </label>
            <input
              type="text"
              className="nothing-input font-mono-tech text-xs"
              placeholder="e.g. PERSONAL EFFECTS, CLOTHES, SWEETS, MEDICINES"
              value={payload.contents_description || ''}
              onChange={(e) => onUpdateField('contents_description', e.target.value)}
            />
          </div>
        </div>
      )}

      {/* Row 2: Document Downloads */}
      {mode === 'address' ? (
        /* Address Mode: ONLY Shipping Address Label container (Tax Invoice container removed) */
        <div className="mb-4">
          <div className={`rounded-lg border p-4 space-y-3 transition-colors ${
            payload.include_address_label
              ? 'border-[var(--border-color)] bg-[var(--bg-card)]'
              : 'border-[var(--border-color)]/60 bg-[var(--bg-card)]/50 opacity-75'
          }`}>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => onUpdateField('include_address_label', !payload.include_address_label)}
                className="flex items-center gap-2 text-left cursor-pointer group select-none"
              >
                {payload.include_address_label ? (
                  <CheckSquare className="h-4 w-4 text-[var(--accent-red)]" />
                ) : (
                  <Square className="h-4 w-4 text-[var(--text-muted)] group-hover:text-[var(--text-primary)]" />
                )}
                <span className="section-label text-[11px] font-bold text-[var(--text-primary)] group-hover:text-[var(--accent-red)] transition-colors flex items-center gap-1.5">
                  <Tag className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                  INCLUDE SHIPPING ADDRESS LABEL
                </span>
              </button>
              <span className="font-mono-tech text-[9px] text-[var(--text-secondary)]">LABEL PDF</span>
            </div>

            {payload.include_address_label ? (
              <div className="space-y-3 animate-in fade-in duration-150">
                <div className="flex items-center gap-2.5 p-2.5 rounded border border-[var(--border-color)] bg-[var(--bg-surface)]">
                  <Tag className="h-4 w-4 text-[var(--accent-red)] shrink-0" />
                  <div className="text-xs leading-snug">
                    <span className="font-bold font-mono-tech text-[var(--text-primary)]">Format: High-Contrast PDF</span>
                    <p className="text-[10px] text-[var(--text-muted)] font-mono-tech mt-0.5">
                      20pt bold shipping parcel print ready for thermal or A4 parcel printing
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={isGeneratingLabel}
                  onClick={handleDownloadAddressLabel}
                  className="w-full btn-primary py-2.5 px-4 text-xs flex items-center justify-center gap-2 cursor-pointer shadow-sm transition-all font-bold"
                >
                  {isGeneratingLabel ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>GENERATING LABEL (PDF)...</span>
                    </>
                  ) : (
                    <>
                      <Download className="h-3.5 w-3.5" />
                      <span>DOWNLOAD ADDRESS LABEL (PDF)</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="py-4 text-center">
                <p className="font-mono-tech text-[11px] text-[var(--text-muted)] italic">
                  Address label is unticked. Check the box above to enable and download.
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Invoice Mode: 2-Column Grid with Tax Invoice & Address Label */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Column 1: Tax Invoice */}
          <div className={`rounded-lg border p-4 space-y-3 transition-colors ${
            isInvoiceEnabled
              ? 'border-[var(--border-color)] bg-[var(--bg-card)]'
              : 'border-[var(--border-color)]/60 bg-[var(--bg-card)]/50 opacity-75'
          }`}>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => onUpdateField('include_invoice', !isInvoiceEnabled)}
                className="flex items-center gap-2 text-left cursor-pointer group select-none"
              >
                {isInvoiceEnabled ? (
                  <CheckSquare className="h-4 w-4 text-[var(--accent-red)]" />
                ) : (
                  <Square className="h-4 w-4 text-[var(--text-muted)] group-hover:text-[var(--text-primary)]" />
                )}
                <span className="section-label text-[11px] font-bold text-[var(--text-primary)] group-hover:text-[var(--accent-red)] transition-colors flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                  INCLUDE TAX INVOICE
                </span>
              </button>
              <span className="font-mono-tech text-[9px] text-[var(--text-secondary)]">INVOICE PDF</span>
            </div>

            {isInvoiceEnabled ? (
              <div className="space-y-3 animate-in fade-in duration-150">
                <div className="flex items-center gap-2.5 p-2.5 rounded border border-[var(--border-color)] bg-[var(--bg-surface)]">
                  <FileText className="h-4 w-4 text-[var(--accent-red)] shrink-0" />
                  <div className="text-xs leading-snug">
                    <span className="font-bold font-mono-tech text-[var(--text-primary)]">Format: Commercial PDF</span>
                    <p className="text-[10px] text-[var(--text-muted)] font-mono-tech mt-0.5">
                      Official single-page shipping layout with origin declaration & signature
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={isGeneratingInvoice}
                  onClick={handleDownloadInvoice}
                  className="w-full btn-primary py-2.5 px-4 text-xs flex items-center justify-center gap-2 cursor-pointer shadow-sm transition-all font-bold"
                >
                  {isGeneratingInvoice ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>GENERATING INVOICE (PDF)...</span>
                    </>
                  ) : (
                    <>
                      <Download className="h-3.5 w-3.5" />
                      <span>DOWNLOAD INVOICE (PDF)</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="py-4 text-center">
                <p className="font-mono-tech text-[11px] text-[var(--text-muted)] italic">
                  Tax invoice is unticked. Check the box above to enable and download.
                </p>
              </div>
            )}
          </div>

          {/* Column 2: Shipping Address Label */}
          <div className={`rounded-lg border p-4 space-y-3 transition-colors ${
            payload.include_address_label
              ? 'border-[var(--border-color)] bg-[var(--bg-card)]'
              : 'border-[var(--border-color)]/60 bg-[var(--bg-card)]/50 opacity-75'
          }`}>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => onUpdateField('include_address_label', !payload.include_address_label)}
                className="flex items-center gap-2 text-left cursor-pointer group select-none"
              >
                {payload.include_address_label ? (
                  <CheckSquare className="h-4 w-4 text-[var(--accent-red)]" />
                ) : (
                  <Square className="h-4 w-4 text-[var(--text-muted)] group-hover:text-[var(--text-primary)]" />
                )}
                <span className="section-label text-[11px] font-bold text-[var(--text-primary)] group-hover:text-[var(--accent-red)] transition-colors flex items-center gap-1.5">
                  <Tag className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                  INCLUDE SHIPPING ADDRESS LABEL
                </span>
              </button>
              <span className="font-mono-tech text-[9px] text-[var(--text-secondary)]">LABEL PDF</span>
            </div>

            {payload.include_address_label ? (
              <div className="space-y-3 animate-in fade-in duration-150">
                <div className="flex items-center gap-2.5 p-2.5 rounded border border-[var(--border-color)] bg-[var(--bg-surface)]">
                  <Tag className="h-4 w-4 text-[var(--accent-red)] shrink-0" />
                  <div className="text-xs leading-snug">
                    <span className="font-bold font-mono-tech text-[var(--text-primary)]">Format: High-Contrast PDF</span>
                    <p className="text-[10px] text-[var(--text-muted)] font-mono-tech mt-0.5">
                      20pt bold shipping print ready for thermal or A4 parcel printing
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={isGeneratingLabel}
                  onClick={handleDownloadAddressLabel}
                  className="w-full btn-primary py-2.5 px-4 text-xs flex items-center justify-center gap-2 cursor-pointer shadow-sm transition-all font-bold"
                >
                  {isGeneratingLabel ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>GENERATING LABEL (PDF)...</span>
                    </>
                  ) : (
                    <>
                      <Download className="h-3.5 w-3.5" />
                      <span>DOWNLOAD ADDRESS LABEL (PDF)</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="py-4 text-center">
                <p className="font-mono-tech text-[11px] text-[var(--text-muted)] italic">
                  Address label is unticked. Check the box above to enable and download.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
