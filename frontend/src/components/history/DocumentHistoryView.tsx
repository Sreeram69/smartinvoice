import React, { useState, useEffect } from 'react'
import { CornerGrid } from '../common/CornerGrid'
import {
  FileText,
  Search,
  RefreshCw,
  ArrowUpRight,
  Trash2,
  CloudCheck,
  Tag,
  Plus,
} from 'lucide-react'
import { buildApiUrl, getAuthHeaders } from '../../utils/apiConfig'

interface DocumentHistoryViewProps {
  onLoadDocument: (doc: any) => void
  onNotify: (msg: string) => void
  defaultFilter?: 'invoice' | 'address' | 'booking'
  onNewClick?: () => void
  newButtonLabel?: string
  title?: string
}

export const DocumentHistoryView: React.FC<DocumentHistoryViewProps> = ({
  onLoadDocument,
  onNotify,
  defaultFilter = 'invoice',
  onNewClick,
  newButtonLabel = 'NEW',
  title,
}) => {
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const filterType = defaultFilter

  const fetchHistory = React.useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(buildApiUrl('/api/v1/documents'), {
        headers: getAuthHeaders(),
      })
      if (res.status === 401) {
        onNotify('Unauthorized: Check your API key')
        return
      }
      if (res.ok) {
        const data = await res.json()
        setDocuments(data.documents || [])
      }
    } catch {
      onNotify('Could not load history')
    } finally {
      setLoading(false)
    }
  }, [onNotify])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  const filteredDocs = documents.filter((doc) => {
    const isBooking = doc.doc_type === 'booking' || doc.doc_type === 'awb' || doc.doc_number?.startsWith('AWB-')
    const isAddress = doc.doc_type === 'address' || doc.doc_number?.startsWith('ADD-')
    const isInvoice = !isBooking && !isAddress

    if (filterType === 'invoice' && !isInvoice) return false
    if (filterType === 'address' && !isAddress) return false
    if (filterType === 'booking' && !isBooking) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchNum = doc.doc_number?.toLowerCase().includes(q)
      const matchCust = doc.customer?.name?.toLowerCase().includes(q)
      const matchCity = doc.customer?.city?.toLowerCase().includes(q)
      const matchPhone = doc.customer?.phone?.toLowerCase().includes(q)
      return matchNum || matchCust || matchCity || matchPhone
    }
    return true
  })

  // Delete Document directly
  const handleDeleteDocument = async (docNumber: string) => {
    if (!window.confirm(`Delete document #${docNumber}?`)) return
    try {
      const res = await fetch(buildApiUrl(`/api/v1/documents/${encodeURIComponent(docNumber)}`), {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      if (res.ok) {
        onNotify(`Deleted document #${docNumber}`)
        setDocuments((prev) => prev.filter((d) => d.doc_number !== docNumber))
      } else {
        onNotify(`Failed to delete document #${docNumber}`)
      }
    } catch {
      onNotify('Error deleting document')
    }
  }

  // Download PDF directly (Invoice, Shipping Address Label, or Booking AWB)
  const handleDownloadDirect = async (doc: any) => {
    const isBooking = doc.doc_type === 'booking' || doc.doc_type === 'awb' || doc.doc_number?.startsWith('AWB-')
    const isAddress = doc.doc_type === 'address' || doc.doc_number?.startsWith('ADD-')
    const docType = isBooking ? 'booking' : (isAddress ? 'address' : 'invoice')
    const docTitle = isBooking ? 'Booking AWB' : (isAddress ? 'Address Label' : 'Invoice')
    onNotify(`Generating ${docTitle} PDF for ${doc.doc_number}...`)

    try {
      const res = await fetch(buildApiUrl('/api/v1/documents/generate-download'), {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          doc_type: docType,
          doc_number: doc.doc_number,
          date: doc.date,
          sender: doc.sender,
          customer: doc.customer,
          items: doc.items || [],
          total: doc.total || '0.00',
          service_partner: doc.service_partner,
          package_type: doc.package_type,
          pieces: doc.pieces,
          actual_weight: doc.actual_weight || doc.weight,
          volumetric_weight: doc.volumetric_weight,
          chargeable_weight: doc.chargeable_weight || doc.weight,
          rate_per_kg: doc.rate_per_kg,
          freight_amount: doc.freight_amount,
          other_charges: doc.other_charges,
          discount: doc.discount,
          payment_status: doc.payment_status,
          payment_mode: doc.payment_mode,
          contents_description: doc.contents_description,
          destination_country: doc.destination_country,
          include_address_label: false,
          address_format: 'pdf',
          invoice_format: 'pdf',
        }),
      })

      if (res.ok) {
        let filename = `${doc.doc_number}.pdf`
        if (docType === 'invoice' && !doc.doc_number?.startsWith('INV-')) {
          filename = `Invoice_${doc.doc_number}.pdf`
        }
        const disposition = res.headers.get('Content-Disposition')
        if (disposition && disposition.includes('filename=')) {
          const match = disposition.match(/filename="?([^"]+)"?/)
          if (match && match[1]) filename = match[1]
        }

        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
        onNotify(`Downloaded ${filename}`)
      } else {
        onNotify('Download failed')
      }
    } catch {
      onNotify('Download failed')
    }
  }

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-6 shadow-sm">
      {/* Archive Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label">{title || 'SUPABASE CLOUD ARCHIVE'}</span>
          <span className="flex items-center gap-1 font-mono-tech text-[9.5px] text-emerald-400 bg-[var(--bg-card)] border border-[var(--border-color)] px-2 py-0.5 rounded shadow-sm">
            <CloudCheck className="h-3 w-3 text-emerald-400" /> LIVE SYNC
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={fetchHistory}
            className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3 cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>REFRESH</span>
          </button>
          {onNewClick && (
            <button
              type="button"
              onClick={onNewClick}
              className="btn-primary text-xs flex items-center gap-1.5 py-1.5 px-3.5 cursor-pointer shadow-md font-bold tracking-wider"
            >
              <Plus className="h-4 w-4" />
              <span>{(newButtonLabel || 'NEW').replace(/^\+\s*/, '')}</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="font-mono-tech text-xs text-[var(--text-secondary)] font-bold">
            {filteredDocs.length} {filteredDocs.length === 1 ? 'FILE' : 'FILES'} STORED
          </span>
        </div>

        {/* Search Input */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--text-muted)] pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search doc, customer, city..."
            className="nothing-input !pl-9 text-xs"
            style={{ paddingLeft: '2.25rem' }}
          />
        </div>
      </div>

      {/* Documents Table */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="py-12 text-center text-xs text-[var(--text-secondary)] font-mono-tech">
            CONNECTING TO SUPABASE CLOUD...
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="py-12 text-center text-xs text-[var(--text-muted)] font-mono-tech space-y-2">
            <div>
              {filterType === 'invoice'
                ? 'NO SAVED INVOICES FOUND.'
                : filterType === 'address'
                ? 'NO SAVED ADDRESS LABELS FOUND.'
                : filterType === 'booking'
                ? 'NO SAVED BOOKING AWBS FOUND.'
                : 'NO RECORDS FOUND IN ARCHIVE.'}
            </div>
            {onNewClick && (
              <button
                type="button"
                onClick={onNewClick}
                className="btn-secondary text-xs inline-flex items-center gap-1.5 py-1.5 px-3 cursor-pointer mt-2"
              >
                <Plus className="h-3.5 w-3.5 text-[var(--accent-red)]" />
                <span>
                  CREATE {filterType === 'invoice' ? 'INVOICE' : filterType === 'address' ? 'ADDRESS LABEL' : 'BOOKING'}
                </span>
              </button>
            )}
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-color)] text-[var(--text-secondary)] font-mono-tech text-[10px] uppercase tracking-wider">
                <th className="py-2.5 px-3">Document #</th>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">
                  {filterType === 'address' ? 'Recipient / Customer' : 'Customer & Destination'}
                </th>
                {filterType === 'address' ? (
                  <th className="py-2.5 px-3">Address & Contact</th>
                ) : (
                  <th className="py-2.5 px-3 text-right">Total Pricing</th>
                )}
                <th className="py-2.5 px-3 text-right w-px whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)]">
              {filteredDocs.map((doc) => {
                const isBooking = doc.doc_type === 'booking' || doc.doc_type === 'awb' || doc.doc_number?.startsWith('AWB-')
                const isAddress = doc.doc_type === 'address' || doc.doc_number?.startsWith('ADD-')

                return (
                  <tr
                    key={doc.id || doc.doc_number}
                    className="hover:bg-[var(--bg-card-hover)] transition-colors"
                  >
                    {/* Number & Type Badge */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className={`font-mono-tech text-[9px] font-bold px-1.5 py-0.5 rounded uppercase border ${
                          isBooking
                            ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                            : isAddress
                            ? 'bg-blue-500/15 text-blue-500 border-blue-500/30'
                            : 'bg-[var(--accent-red)]/15 text-[var(--accent-red)] border-[var(--accent-red)]/30'
                        }`}>
                          {isBooking ? 'AWB' : isAddress ? 'LABEL' : 'INV'}
                        </span>
                        <span className="font-mono-tech text-xs font-bold text-[var(--text-primary)]">
                          {doc.doc_number}
                        </span>
                      </div>
                    </td>

                    {/* Date */}
                    <td className="py-3 px-3 font-mono-tech text-xs text-[var(--text-secondary)] whitespace-nowrap">
                      {doc.date}
                    </td>

                    {/* Customer / Recipient */}
                    <td className="py-3 px-3">
                      <div className="font-mono-tech text-xs text-[var(--text-primary)] font-bold">
                        {doc.customer?.name || 'Unknown'}
                      </div>
                      <div className="font-mono-tech text-[10.5px] text-[var(--text-secondary)]">
                        {doc.customer?.city ? `${doc.customer.city}, ${doc.customer?.state || ''}` : ''}
                      </div>
                    </td>

                    {/* Total or Address Detail */}
                    {isAddress || filterType === 'address' ? (
                      <td className="py-3 px-3 font-mono-tech text-xs text-[var(--text-secondary)]">
                        <div>{doc.customer?.address_line_1 || 'No address line'}</div>
                        <div className="text-[10.5px] text-[var(--text-muted)]">
                          PIN: {doc.customer?.postal_code || 'N/A'} • {doc.customer?.phone || 'No phone'}
                        </div>
                      </td>
                    ) : (
                      <td className="py-3 px-3 text-right font-mono-tech text-xs font-bold text-[var(--text-primary)] whitespace-nowrap">
                        ₹{doc.total}
                      </td>
                    )}

                    {/* Actions */}
                    <td className="py-3 px-3 text-right w-px whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* Load into Editor */}
                        <button
                          type="button"
                          onClick={() => onLoadDocument(doc)}
                          className="btn-secondary text-[10.5px] py-1 px-2.5 flex items-center gap-1 cursor-pointer"
                          title="Load into Form"
                        >
                          <ArrowUpRight className="h-3 w-3 text-[var(--accent-red)]" />
                          <span>OPEN</span>
                        </button>

                        {/* Download PDF (Only for Invoice and Address Label) */}
                        {!isBooking && (
                          <button
                            type="button"
                            onClick={() => handleDownloadDirect(doc)}
                            className="btn-secondary text-[10.5px] py-1 px-2 flex items-center gap-1 text-[var(--text-primary)] cursor-pointer"
                            title={`Download ${isAddress ? 'Address Label' : 'Invoice'} PDF`}
                          >
                            {isAddress ? <Tag className="h-3 w-3 text-blue-500" /> : <FileText className="h-3 w-3" />}
                            <span>PDF</span>
                          </button>
                        )}

                        {/* Delete Document */}
                        <button
                          type="button"
                          onClick={() => handleDeleteDocument(doc.doc_number)}
                          className="btn-secondary text-[10.5px] py-1 px-2 flex items-center gap-1 text-[var(--accent-red)] hover:bg-[var(--accent-red)]/15 border-[var(--border-color)] hover:border-[var(--accent-red)] cursor-pointer transition-colors"
                          title={`Delete Document #${doc.doc_number}`}
                        >
                          <Trash2 className="h-3 w-3 text-[var(--accent-red)]" />
                          <span>DELETE</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
