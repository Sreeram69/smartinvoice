import React, { useState } from 'react'
import { CornerGrid } from '../common/CornerGrid'
import { ArrowLeftRight, Check, X, Eye, EyeOff, AlertTriangle, Building, UserCheck } from 'lucide-react'
import type { AddressInfo } from '../../types/document'

interface AddressReviewModalProps {
  initialSender: AddressInfo
  initialCustomer: AddressInfo
  rawText: string
  onConfirm: (sender: AddressInfo, customer: AddressInfo) => void
  onCancel: () => void
}

export const AddressReviewModal: React.FC<AddressReviewModalProps> = ({
  initialSender,
  initialCustomer,
  rawText,
  onConfirm,
  onCancel,
}) => {
  const [sender, setSender] = useState<AddressInfo>(initialSender)
  const [customer, setCustomer] = useState<AddressInfo>(initialCustomer)
  const [showRawText, setShowRawText] = useState<boolean>(false)

  const handleSwap = () => {
    const temp = { ...sender }
    setSender({ ...customer })
    setCustomer(temp)
  }

  const handleSenderChange = (field: keyof AddressInfo, val: string) => {
    setSender((prev) => ({ ...prev, [field]: val }))
  }

  const handleCustomerChange = (field: keyof AddressInfo, val: string) => {
    setCustomer((prev) => ({ ...prev, [field]: val }))
  }

  return (
    <div className="rounded-xl border-2 border-[var(--accent-red)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-2xl space-y-4 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label text-[var(--accent-red)] font-bold">
            CONFIRM OCR EXTRACTED ADDRESSES
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleSwap}
            className="btn-secondary text-[11px] py-1 px-3 flex items-center gap-1.5"
            title="Swap Sender and Customer"
          >
            <ArrowLeftRight className="h-3.5 w-3.5 text-[var(--accent-red)]" />
            <span>SWAP ROLES</span>
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] p-1 transition-colors"
            title="Cancel"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Review Warning Callout */}
      <div className="flex items-center gap-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-500 dark:text-amber-300 font-mono-tech">
        <AlertTriangle className="h-4 w-4 shrink-0 text-amber-500 dark:text-amber-400" />
        <span>
          Review required: Verify extracted names, addresses, and phone numbers below before applying to your document.
        </span>
      </div>

      {/* Side-by-side Review Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* SENDER BLOCK */}
        <div className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-4 space-y-2.5">
          <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-2">
            <span className="font-mono-tech text-[11px] font-bold text-[var(--text-primary)] flex items-center gap-1.5 uppercase">
              <Building className="h-3.5 w-3.5 text-[var(--accent-red)]" />
              DETECTED SENDER (FROM)
            </span>
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Company / Sender Name</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. KOVELAKONDA MOHAN RAO"
              value={sender.name}
              onChange={(e) => handleSenderChange('name', e.target.value)}
            />
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Address Line 1 (Street / Building)</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. 16-42-41/3, INDRA COL"
              value={sender.address_line_1}
              onChange={(e) => handleSenderChange('address_line_1', e.target.value)}
            />
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Address Line 2 (Area / Locality / Landmark)</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. Near Ramaraopeta"
              value={sender.address_line_2 || ''}
              onChange={(e) => handleSenderChange('address_line_2', e.target.value)}
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="input-container group">
              <label className="section-label block mb-1">City</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="City"
                value={sender.city}
                onChange={(e) => handleSenderChange('city', e.target.value)}
              />
            </div>
            <div className="input-container group">
              <label className="section-label block mb-1">State / Region</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="State"
                value={sender.state || ''}
                onChange={(e) => handleSenderChange('state', e.target.value)}
              />
            </div>
            <div className="input-container group">
              <label className="section-label block mb-1">Postal Code</label>
              <input
                type="text"
                className="nothing-input font-mono-tech"
                placeholder="PIN/ZIP"
                value={sender.postal_code}
                onChange={(e) => handleSenderChange('postal_code', e.target.value)}
              />
            </div>
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Phone</label>
            <input
              type="text"
              className="nothing-input font-mono-tech"
              placeholder="Phone number"
              value={sender.phone}
              onChange={(e) => handleSenderChange('phone', e.target.value)}
            />
          </div>
        </div>

        {/* CUSTOMER BLOCK */}
        <div className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-4 space-y-2.5">
          <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-2">
            <span className="font-mono-tech text-[11px] font-bold text-[var(--text-primary)] flex items-center gap-1.5 uppercase">
              <UserCheck className="h-3.5 w-3.5 text-[var(--accent-red)]" />
              DETECTED CUSTOMER (TO)
            </span>
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Customer / Recipient Name</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. JAFFAR MIRZA"
              value={customer.name}
              onChange={(e) => handleCustomerChange('name', e.target.value)}
            />
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Address Line 1 (Street / Building)</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. BLVD FNO 102"
              value={customer.address_line_1}
              onChange={(e) => handleCustomerChange('address_line_1', e.target.value)}
            />
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Address Line 2 (Area / Locality / Landmark)</label>
            <input
              type="text"
              className="nothing-input"
              placeholder="e.g. PT-655D ASTER HOSPITAL, AL RAFFA, BUR"
              value={customer.address_line_2 || ''}
              onChange={(e) => handleCustomerChange('address_line_2', e.target.value)}
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="input-container group">
              <label className="section-label block mb-1">City</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="City"
                value={customer.city}
                onChange={(e) => handleCustomerChange('city', e.target.value)}
              />
            </div>
            <div className="input-container group">
              <label className="section-label block mb-1">State / Country</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="e.g. UAE"
                value={customer.state || ''}
                onChange={(e) => handleCustomerChange('state', e.target.value)}
              />
            </div>
            <div className="input-container group">
              <label className="section-label block mb-1">Postal Code</label>
              <input
                type="text"
                className="nothing-input font-mono-tech"
                placeholder="PIN/ZIP"
                value={customer.postal_code}
                onChange={(e) => handleCustomerChange('postal_code', e.target.value)}
              />
            </div>
          </div>

          <div className="input-container group">
            <label className="section-label block mb-1">Phone</label>
            <input
              type="text"
              className="nothing-input font-mono-tech"
              placeholder="Phone number"
              value={customer.phone}
              onChange={(e) => handleCustomerChange('phone', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Raw Text Accordion Toggle */}
      <div>
        <button
          type="button"
          onClick={() => setShowRawText(!showRawText)}
          className="font-mono-tech text-[10.5px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] flex items-center gap-1.5 transition-colors"
        >
          {showRawText ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
          <span>{showRawText ? 'HIDE RAW EXTRACTED OCR TEXT' : 'VIEW RAW EXTRACTED OCR TEXT'}</span>
        </button>
        {showRawText && (
          <pre className="mt-2 p-3 rounded bg-[var(--bg-primary)] border border-[var(--border-color)] font-mono-tech text-[10px] text-[var(--text-secondary)] whitespace-pre-wrap max-h-36 overflow-y-auto">
            {rawText || 'No raw text available.'}
          </pre>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 pt-2 border-t border-[var(--border-color)]">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary px-4 py-2 text-xs"
        >
          CANCEL
        </button>
        <button
          type="button"
          onClick={() => onConfirm(sender, customer)}
          className="btn-primary px-5 py-2 text-xs flex items-center gap-2"
        >
          <Check className="h-4 w-4" />
          <span>CONFIRM & APPLY TO DOCUMENT</span>
        </button>
      </div>
    </div>
  )
}
